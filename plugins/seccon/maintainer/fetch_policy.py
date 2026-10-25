# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Ordinary HTTP acquisition with conservative robots and redirect checks."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

USER_AGENT = "ph-seccon/2.1 (AI-assisted conference metadata maintenance)"
# Honor AI-specific restrictions even when a generic crawler would be allowed.
POLICY_AGENTS = ("ph-seccon", "GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot")
STOP_OUTCOMES = {
    "policy-denied",
    "policy-blocked",
    "policy-rate-limited",
    "policy-timeout",
    "policy-unavailable",
    "blocked",
    "rate-limited",
    "budget-exhausted",
}
MAX_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class FetchResult:
    url: str
    effective_url: str = ""
    status: int | None = None
    content_type: str = ""
    body: str = ""
    outcome: str = "ok"
    reason: str = ""
    retry_after: str = ""
    acquired_at: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    assets: tuple[dict[str, object], ...] = ()


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(url: str, timeout: float) -> FetchResult:
    """Fetch one response without automatic redirects or transport retries."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        response = build_opener(NoRedirect).open(req, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        raw = response.read(MAX_BYTES + 1)
        headers = {key.lower(): value for key, value in response.headers.items()}
        if len(raw) > MAX_BYTES:
            return FetchResult(
                url,
                status=response.code,
                outcome="too-large",
                reason=f"Response exceeds {MAX_BYTES} bytes",
            )
        return FetchResult(
            url=url,
            effective_url=url,
            status=response.code,
            content_type=headers.get("content-type", "").split(";")[0].lower(),
            body=raw.decode(response.headers.get_content_charset() or "utf-8", errors="replace"),
            headers=headers,
            acquired_at=datetime.now(UTC).isoformat(),
        )


def origin(url: str) -> str:
    parts = urlsplit(url)
    if (
        parts.scheme not in {"https", "http"}
        or not parts.hostname
        or parts.username
        or parts.password
    ):
        raise ValueError(f"Only credential-free HTTP(S) URLs are supported: {url}")
    return f"{parts.scheme}://{parts.netloc.lower()}"


def _groups(text: str) -> list[tuple[list[str], list[tuple[str, str]]]]:
    groups = []
    agents: list[str] = []
    directives: list[tuple[str, str]] = []
    for line in [*text.splitlines(), "User-agent: end-of-file"]:
        key, sep, value = line.split("#", 1)[0].partition(":")
        if not sep:
            continue
        key, value = key.strip().lower(), value.strip()
        if key == "user-agent":
            if directives:
                groups.append((agents, directives))
                agents, directives = [], []
            agents.append(value.lower())
        elif agents:
            directives.append((key, value))
    return groups


def _matching_rule(key: str, value: str, path: str) -> tuple[int, bool] | None:
    if key not in {"allow", "disallow"} or not value:
        return None
    pattern = re.escape(unquote(value)).replace(r"\*", ".*")
    pattern = pattern[:-2] + "$" if pattern.endswith(r"\$") else pattern
    if re.match(pattern, path):
        return len(value.replace("*", "").rstrip("$")), key == "allow"
    return None


def _crawl_delay(key: str, value: str) -> float:
    if key == "crawl-delay" and re.fullmatch(r"\d+(?:\.\d+)?", value):
        return float(value)
    if key == "request-rate" and re.fullmatch(r"\d+/\d+", value):
        count, seconds = map(int, value.split("/"))
        return seconds / max(count, 1)
    return 1.0


def robots_access(text: str, url: str) -> tuple[bool, float]:
    """Honor wildcard/end-anchored rules for the crawler and AI identities.

    Longest matching path wins; Allow wins ties. Denial for any declared AI
    identity is honored rather than selecting a looser identity.
    """
    groups = _groups(text)
    parts = urlsplit(url)
    path = unquote(parts.path or "/") + ("?" + unquote(parts.query) if parts.query else "")
    delay = 1.0
    for agent in POLICY_AGENTS:
        named = [
            (names, rules)
            for names, rules in groups
            if any(name != "*" and name in agent.lower() for name in names)
        ]
        selected = named or [(names, rules) for names, rules in groups if "*" in names]
        matches = []
        for _, rules in selected:
            for key, value in rules:
                delay = max(delay, _crawl_delay(key, value))
                match = _matching_rule(key, value, path)
                if match:
                    matches.append(match)
        if matches and not max(matches)[1]:
            return False, delay
    return True, delay


def _response_outcome(result: FetchResult) -> FetchResult:
    status = result.status or 0
    if status == 429:
        outcome = "rate-limited"
    elif status in {401, 403}:
        outcome = "blocked"
    elif status == 404:
        outcome = "not-found"
    elif status >= 400:
        outcome = "http-error"
    elif re.search(
        r"<title[^>]*>[^<]*(?:attention required|just a moment|access denied)", result.body, re.I
    ):
        outcome = "blocked"
    else:
        outcome = result.outcome
    reason = result.reason
    if outcome != "ok" and not reason:
        reason = f"HTTP {status}; stop acquisition" if status >= 400 else "Challenge/denial page"
    return replace(
        result, outcome=outcome, reason=reason, retry_after=result.headers.get("retry-after", "")
    )


def _url_years(path: str) -> set[str]:
    years = set(re.findall(r"20\d{2}", path))
    years.update(f"20{short}" for short in re.findall(r"[a-z]+-(\d{2})(?:/|$)", path))
    return years


def redirect_mismatch(before: str, after: str, year: int | None) -> bool:
    old_path, new_path = unquote(urlsplit(before).path), unquote(urlsplit(after).path)
    old_years = _url_years(old_path)
    new_years = _url_years(new_path)
    if new_years and (old_years or year) and new_years != (old_years or {str(year)}):
        return True
    editions = r"([a-z]+)-20\d{2}"
    old_region, new_region = re.findall(editions, old_path), re.findall(editions, new_path)
    return bool(old_region and new_region and old_region != new_region)


class Fetcher:
    """Share robots decisions, host pacing and finite request budgets across a command."""

    def __init__(self, *, max_requests: int = 24, timeout: float = 25):
        self.max_requests = max_requests
        self.timeout = timeout
        self.policies: dict[str, FetchResult] = {}
        self.counts: dict[str, int] = {}
        self.last: dict[str, float] = {}
        self.delays: dict[str, float] = {}
        self.stopped: dict[str, FetchResult] = {}

    def _request(self, url: str) -> FetchResult:
        host = origin(url)
        if host in self.stopped:
            return replace(self.stopped[host], url=url, body="")
        if self.counts.get(host, 0) >= self.max_requests:
            return FetchResult(url, outcome="budget-exhausted", reason="Per-origin request budget")
        wait = self.delays.get(host, 1) - (time.monotonic() - self.last.get(host, float("-inf")))
        if wait > 0:
            time.sleep(wait)
        self.last[host] = time.monotonic()
        self.counts[host] = self.counts.get(host, 0) + 1
        try:
            result = _response_outcome(request(url, self.timeout))
        except (TimeoutError, URLError, OSError) as exc:
            cause = getattr(exc, "reason", exc)
            outcome = "timeout" if isinstance(cause, TimeoutError) else "network-error"
            return FetchResult(url, effective_url=url, outcome=outcome, reason=str(exc))
        if result.outcome in {"blocked", "rate-limited"}:
            self.stopped[host] = result
        return result

    def _policy(self, url: str) -> FetchResult:
        host = origin(url)
        if host not in self.policies:
            policy = self._request(host + "/robots.txt")
            if policy.status == 404:
                policy = replace(policy, outcome="ok", body="")
            elif policy.outcome != "ok":
                name = {
                    "blocked": "blocked",
                    "rate-limited": "rate-limited",
                    "timeout": "timeout",
                }.get(policy.outcome, "unavailable")
                policy = replace(policy, outcome=f"policy-{name}")
            elif policy.status != 200 or "<html" in policy.body.lower():
                policy = replace(
                    policy,
                    outcome="policy-unavailable",
                    reason="Robots response is redirected or not a robots document",
                )
            self.policies[host] = policy
        policy = self.policies[host]
        if policy.outcome != "ok":
            return replace(policy, url=url, effective_url=policy.url, body="")
        allowed, delay = robots_access(policy.body, url)
        self.delays[host] = delay
        if not allowed:
            return replace(
                policy,
                url=url,
                effective_url=url,
                body="",
                outcome="policy-denied",
                reason=f"Robots disallows crawler/AI access; policy: {policy.url}",
            )
        return replace(policy, url=url)

    def fetch(
        self, url: str, *, allowed_origin: str | None = None, year: int | None = None
    ) -> FetchResult:
        """Check policy before each target/redirect; return causes without retrying denials."""
        initial = url
        for _ in range(5):
            try:
                host = origin(url)
            except ValueError as exc:
                return FetchResult(
                    initial, effective_url=url, outcome="invalid-url", reason=str(exc)
                )
            if allowed_origin and host != allowed_origin:
                return FetchResult(initial, effective_url=url, outcome="external-redirect")
            policy = self._policy(url)
            if policy.outcome != "ok":
                return replace(policy, url=initial)
            result = self._request(url)
            result = replace(result, url=initial, effective_url=url)
            if result.status not in {301, 302, 303, 307, 308} or result.outcome != "ok":
                return result
            target = urljoin(url, result.headers.get("location", ""))
            if target == url:
                return replace(result, outcome="redirect-error", reason="Missing/cyclic Location")
            if redirect_mismatch(initial, target, year):
                return replace(
                    result,
                    effective_url=target,
                    body="",
                    outcome="edition-mismatch",
                    reason="Redirect changes the requested year or region",
                )
            url = target
        return FetchResult(initial, effective_url=url, outcome="redirect-limit")


def validate_content(result: FetchResult, *, year: int | None = None) -> FetchResult:
    """Conservatively label suspicious editions and empty client-rendered programs."""
    if result.outcome != "ok":
        return result
    kind = result.content_type.split(";")[0].lower()
    if kind and not any(part in kind for part in ("html", "json", "xml", "text/plain")):
        return replace(result, outcome="content-type-mismatch", reason=kind)
    if not result.body.strip():
        return replace(result, outcome="empty", reason="Empty response body")
    identity = _validate_identity(result, year)
    if identity.outcome != "ok":
        return identity
    if "json" in kind:
        try:
            json.loads(result.body)
        except ValueError as exc:
            return replace(result, outcome="invalid-json", reason=str(exc))
        return result
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", result.body, flags=re.I | re.S)
    text = unescape(re.sub(r"<[^>]*>", " ", text))
    shell = "_next/" in result.body and len(text.split()) < 80
    shell = shell or not text.strip() or bool(re.search(r"enable javascript", text, re.I))
    if shell:
        return replace(result, outcome="shell", reason="Program requires linked data")
    return result


def _validate_identity(result: FetchResult, year: int | None) -> FetchResult:
    initial = (urlsplit(result.url).hostname or "").removeprefix("www.")
    effective = (urlsplit(result.effective_url or result.url).hostname or "").removeprefix("www.")
    if initial != effective:
        return replace(result, outcome="needs-review", reason="Redirect changes source host")
    title = re.search(r"<title[^>]*>(.*?)</title>", result.body, re.I | re.S)
    if not title:
        return result
    title_years = set(re.findall(r"20\d{2}", title.group(1)))
    if year and title_years and str(year) not in title_years:
        return replace(result, outcome="needs-review", reason="Title conflicts with requested year")
    if re.search(r"^(?:error|not found|404|access denied)\b", title.group(1).strip(), re.I):
        return replace(
            result, outcome="needs-review", reason="Response title identifies an error page"
        )
    return result

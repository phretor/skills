"""Policy, response and content tests; transport is always replaced offline."""

import importlib
import socket
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/seccon/maintainer"))
FIXTURES = Path(__file__).parent / "fixtures/seccon"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("Network forbidden in offline regression tests")

    monkeypatch.setattr(socket, "create_connection", fail)


@pytest.fixture
def policy():
    return importlib.import_module("fetch_policy")


@pytest.fixture
def transport(policy, monkeypatch):
    calls = []
    routes = {}

    def request(url, timeout):
        calls.append(url)
        value = routes[url]
        if isinstance(value, Exception):
            raise value
        status, body, headers = value
        return policy.FetchResult(
            url=url,
            effective_url=url,
            status=status,
            body=body,
            content_type=headers.get("content-type", "text/html"),
            headers=headers,
        )

    monkeypatch.setattr(policy, "request", request)
    monkeypatch.setattr(policy.time, "sleep", lambda seconds: None)
    return routes, calls


@pytest.mark.parametrize(
    "host,path",
    [
        ("dblp.org", "/db/conf/sp/sp2025.xml"),
        ("www.youtube.com", "/feeds/videos.xml?channel_id=example"),
        ("media.defcon.org", "/DEF%20CON%2033/"),
    ],
)
def test_denied_paths_never_requested(policy, transport, host, path):
    routes, calls = transport
    robots = f"https://{host}/robots.txt"
    routes[robots] = (200, (FIXTURES / f"robots-{host}.txt").read_text(), {})
    result = policy.Fetcher().fetch(f"https://{host}{path}")
    assert result.outcome == "policy-denied"
    assert calls == [robots]


@pytest.mark.parametrize(
    "status,body,outcome",
    [
        (403, "challenge", "blocked"),
        (429, "", "rate-limited"),
        (404, "missing", "not-found"),
        (200, "{}", "ok"),
        (200, (FIXTURES / "blackhat-denied.html").read_text(), "blocked"),
    ],
)
def test_response_outcomes(policy, transport, status, body, outcome):
    routes, calls = transport
    routes["https://example.org/robots.txt"] = (404, "", {})
    routes["https://example.org/data"] = (status, body, {"retry-after": "120"})
    result = policy.Fetcher().fetch("https://example.org/data")
    assert result.outcome == outcome
    assert result.status == status
    assert result.retry_after == "120"
    assert calls.count("https://example.org/data") == 1


def test_robots_rate_limit_and_timeout(policy, transport):
    routes, calls = transport
    routes["https://example.org/robots.txt"] = (429, "", {"retry-after": "60"})
    fetcher = policy.Fetcher()
    assert fetcher.fetch("https://example.org/data").outcome == "policy-rate-limited"
    assert fetcher.fetch("https://example.org/other").outcome == "policy-rate-limited"
    assert calls == ["https://example.org/robots.txt"]
    routes["https://timeout.org/robots.txt"] = TimeoutError("timed out")
    assert fetcher.fetch("https://timeout.org/data").outcome == "policy-timeout"
    routes["https://target.org/robots.txt"] = (404, "", {})
    routes["https://target.org/data"] = TimeoutError("timed out")
    assert fetcher.fetch("https://target.org/data").outcome == "timeout"


def test_redirect_policy_and_origin(policy, transport):
    routes, calls = transport
    routes["https://example.org/robots.txt"] = (404, "", {})
    routes["https://example.org/data"] = (302, "", {"location": "https://denied.org/data"})
    routes["https://denied.org/robots.txt"] = (200, "User-agent: *\nDisallow: /", {})
    result = policy.Fetcher().fetch("https://example.org/data")
    assert result.outcome == "policy-denied"
    assert "https://denied.org/data" not in calls
    result = policy.Fetcher().fetch(
        "https://example.org/data", allowed_origin="https://example.org"
    )
    assert result.outcome == "external-redirect"


def test_host_budget_and_delay(policy, transport, monkeypatch):
    routes, calls = transport
    sleeps = []
    monkeypatch.setattr(policy.time, "sleep", sleeps.append)
    routes["https://example.org/robots.txt"] = (200, "User-agent: *\nCrawl-delay: 20", {})
    routes["https://example.org/a"] = (200, "a", {})
    fetcher = policy.Fetcher(max_requests=2)
    assert fetcher.fetch("https://example.org/a").outcome == "ok"
    assert fetcher.fetch("https://example.org/b").outcome == "budget-exhausted"
    assert sleeps and sleeps[0] >= 19
    assert len(calls) == 2


@pytest.mark.parametrize(
    "name,outcome",
    [
        ("ccs.html", "shell"),
        ("sp2025.html", "needs-review"),
        ("sp2025-program.html", "ok"),
        ("ndss2025.html", "ok"),
        ("recon2025.html", "ok"),
    ],
)
def test_content_evidence(policy, name, outcome):
    result = policy.FetchResult(
        url="https://example.org/2025/",
        effective_url="https://example.org/2025/",
        status=200,
        body=(FIXTURES / name).read_text(),
        content_type="text/html",
    )
    assert policy.validate_content(result, year=2025).outcome == outcome


def test_edition_redirects_and_types(policy, transport):
    routes, calls = transport
    routes["https://hardwear.io/robots.txt"] = (404, "", {})
    routes["https://hardwear.io/netherlands-2025/talks/"] = (
        301,
        "",
        {"location": "https://hardwear.io/usa-2026/talks-speakers/"},
    )
    result = policy.Fetcher().fetch("https://hardwear.io/netherlands-2025/talks/", year=2025)
    assert result.outcome == "edition-mismatch"
    assert "https://hardwear.io/usa-2026/talks-speakers/" not in calls
    routes["https://hardwear.io/2025"] = (301, "", {"location": "/2025/"})
    routes["https://hardwear.io/2025/"] = (200, "<h1>2025</h1><p>A valid program</p>", {})
    result = policy.Fetcher().fetch("https://hardwear.io/2025", year=2025)
    assert result.effective_url == "https://hardwear.io/2025/"
    assert result.status == 200
    assert result.outcome == "ok"
    result = policy.FetchResult(
        url="https://example.org/x", status=200, body="%PDF", content_type="application/pdf"
    )
    assert policy.validate_content(result).outcome == "content-type-mismatch"


def test_same_year_region_change(policy, transport):
    routes, calls = transport
    routes["https://hardwear.io/robots.txt"] = (404, "", {})
    routes["https://hardwear.io/netherlands-2025/"] = (
        302,
        "",
        {"location": "https://hardwear.io/usa-2025/"},
    )
    assert (
        policy.Fetcher().fetch("https://hardwear.io/netherlands-2025/").outcome
        == "edition-mismatch"
    )
    assert len(calls) == 2


@pytest.mark.parametrize(
    "html",
    [
        "<html><div id='app'></div></html>",
        "<html><title>Program 2025</title><p>Please enable JavaScript to view papers.</p></html>",
    ],
)
def test_empty_shell_without_framework_markers(policy, html):
    result = policy.FetchResult("https://example.org/2025/", body=html, content_type="text/html")
    assert policy.validate_content(result, year=2025).outcome == "shell"


def test_stale_title_conflicting_body(policy):
    result = policy.FetchResult(
        "https://example.org/2025/",
        body=(
            "<title>IEEE S&P 2024</title><h1>IEEE S&P 2025</h1><p>A valid 2025 paper and author</p>"
        ),
        content_type="text/html",
    )
    checked = policy.validate_content(result, year=2025)
    assert checked.outcome == "needs-review"
    assert checked.body == result.body


def test_robots_path_rules(policy):
    rules = "User-agent: *\nDisallow: /*.xml$\nAllow: /public.xml$\n"
    assert policy.robots_access(rules, "https://example.org/private.xml")[0] is False
    assert policy.robots_access(rules, "https://example.org/public.xml")[0] is True
    assert policy.robots_access(rules, "https://example.org/private.xml.html")[0] is True


def test_robots_redirect_fails_closed(policy, transport):
    routes, calls = transport
    routes["https://example.org/robots.txt"] = (
        302,
        "",
        {"location": "https://other.org/robots.txt"},
    )
    assert policy.Fetcher().fetch("https://example.org/a").outcome == "policy-unavailable"
    assert calls == ["https://example.org/robots.txt"]


def test_redirect_between_venues_needs_review(policy):
    result = policy.FetchResult(
        "https://ccs.example/2025/",
        effective_url="https://ndss.example/2025/",
        content_type="text/html",
        body="<title>NDSS 2025</title><p>Accepted papers</p>",
    )
    assert policy.validate_content(result, year=2025).outcome == "needs-review"
    canonical = policy.FetchResult(
        "https://www.ccs.example/2025/",
        effective_url="https://ccs.example/2025/",
        content_type="text/html",
        body="<title>CCS 2025</title><p>Accepted papers</p>",
    )
    assert policy.validate_content(canonical, year=2025).outcome == "ok"


def test_short_year_redirect_mismatch(policy, transport):
    routes, calls = transport
    routes["https://blackhat.com/robots.txt"] = (404, "", {})
    routes["https://blackhat.com/us-25/sessions.json"] = (
        302,
        "",
        {"location": "/us-26/sessions.json"},
    )
    result = policy.Fetcher().fetch("https://blackhat.com/us-25/sessions.json", year=2025)
    assert result.outcome == "edition-mismatch"
    assert len(calls) == 2


def test_mislabeled_html_error_is_not_program(policy):
    response = policy.FetchResult(
        "https://example.org/2025/",
        content_type="text/plain",
        body="<html><title>Error</title><h1>Not Found</h1></html>",
    )
    assert policy.validate_content(response).outcome == "needs-review"


def test_transport_keeps_http_error_metadata(policy, monkeypatch):
    from email.message import Message
    from io import BytesIO
    from urllib.error import HTTPError

    headers = Message()
    headers["Content-Type"] = "text/html; charset=utf-8"
    headers["Retry-After"] = "120"
    error = HTTPError("https://example.org/a", 403, "Forbidden", headers, BytesIO(b"denied"))

    class Opener:
        def open(self, req, timeout):
            assert req.get_header("User-agent").startswith("ph-seccon/")
            raise error

    monkeypatch.setattr(policy, "build_opener", lambda *handlers: Opener())
    result = policy.request("https://example.org/a", 1)
    assert result.status == 403
    assert result.content_type == "text/html"
    assert result.body == "denied"
    assert result.acquired_at
    assert result.headers["retry-after"] == "120"


@pytest.mark.parametrize(
    "status,body,outcome",
    [
        (403, "denied", "policy-blocked"),
        (503, "unavailable", "policy-unavailable"),
        (200, "<html>challenge</html>", "policy-unavailable"),
    ],
)
def test_unavailable_robots_stops_target(policy, transport, status, body, outcome):
    routes, calls = transport
    routes["https://example.org/robots.txt"] = (status, body, {})
    result = policy.Fetcher().fetch("https://example.org/program")
    assert result.outcome == outcome
    assert calls == ["https://example.org/robots.txt"]


def test_invalid_url_redirect_loop_and_server_error(policy, transport):
    routes, calls = transport
    assert policy.Fetcher().fetch("ftp://example.org/a").outcome == "invalid-url"
    assert calls == []
    routes["https://example.org/robots.txt"] = (404, "", {})
    routes["https://example.org/a"] = (302, "", {"location": "/a"})
    assert policy.Fetcher().fetch("https://example.org/a").outcome == "redirect-error"
    routes["https://example.org/a"] = (500, "error", {})
    assert policy.Fetcher().fetch("https://example.org/a").outcome == "http-error"

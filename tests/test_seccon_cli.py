"""Exercise the real command dispatch with recorded, policy-checked HTTP responses."""

import importlib
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAINTAINER = ROOT / "plugins/seccon/maintainer"
sys.path.insert(0, str(MAINTAINER))
FIXTURES = Path(__file__).parent / "fixtures/seccon"
URL = "https://www.sigsac.org/ccs/CCS2025/accepted-papers/"


@pytest.fixture
def crawler(monkeypatch):
    module = importlib.import_module("crawl_conferences")
    policy = importlib.import_module("fetch_policy")
    calls = []
    page = (FIXTURES / "ccs.html").read_text()
    chunk = page.split('src="')[1].split('"')[0]
    routes = {
        "https://www.sigsac.org/robots.txt": (200, "User-agent: *\nCrawl-delay: 20", "text/plain"),
        URL: (200, page, "text/html"),
        "https://www.sigsac.org" + chunk: (
            200,
            (FIXTURES / "ccs.js").read_text(),
            "application/javascript",
        ),
        "https://www.sigsac.org/ccs/CCS2025/assets/accepted-papers.json": (
            200,
            (FIXTURES / "ccs.json").read_text(),
            "application/json",
        ),
    }

    def request(url, timeout):
        calls.append(url)
        status, body, content_type = routes[url]
        return policy.FetchResult(
            url=url, effective_url=url, status=status, body=body, content_type=content_type
        )

    def fail(*a, **kw):
        raise AssertionError("unexpected network/resolver access")

    monkeypatch.setattr(socket, "create_connection", fail)
    monkeypatch.setattr(policy, "request", request)
    monkeypatch.setattr(policy.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(module, "FETCHER", policy.Fetcher())
    monkeypatch.setattr(module, "resolve_url", fail)
    return module, calls, routes


def test_explicit_and_registry_cli_equivalent(crawler, monkeypatch, capsys):
    module, calls, _routes = crawler
    results = []
    for extra in (["--url", URL], ["--conference", "ccs"]):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "crawl_conferences.py",
                "--crawl-content",
                "--year",
                "2025",
                "--format",
                "json",
                *extra,
            ],
        )
        module.main()
        result = json.loads(capsys.readouterr().out)
        assert "Split Unlearning" in result["raw_page"]
        assert result["outcome"] == "ok"
        results.append(result["raw_page"])
    assert results[0] == results[1]
    assert (
        sum(url.endswith(".js") for url in calls) == 2
    )  # One per command, despite duplicate tags.


@pytest.mark.parametrize("alias", ["sp", "S&P", "ieee-sp", "ieee-s&p", "IEEE S&P", "s-p"])
def test_ieee_aliases(crawler, alias):
    module, _, _ = crawler
    assert module.select_confs(module.ACADEMIC_CONFS, alias)[0].abbrev == "ieee-sp"


@pytest.mark.parametrize(
    "alias,slug",
    [
        ("usenix", "usenix-security"),
        ("asia-ccs", "asiaccs"),
        ("bhusa", "blackhat-usa"),
        ("bheu", "blackhat-eu"),
        ("bhasia", "blackhat-asia"),
        ("def-con", "defcon"),
        ("offensivecon", "offensivecon"),
    ],
)
def test_registry_aliases(crawler, alias, slug):
    module, _, _ = crawler
    assert (
        module.select_confs(module.ACADEMIC_CONFS + module.INDUSTRY_CONFS, alias)[0].abbrev == slug
    )


def test_assets_bounded_and_external_forbidden(crawler):
    module, calls, routes = crawler
    routes[URL] = (
        200,
        "<title>CCS 2025</title><ul></ul>"
        + "".join(f'<script src="_next/static/chunks/app/page-{n}.js"></script>' for n in range(20))
        + '<script src="https://evil.org/_next/static/chunks/app/page.js"></script>',
        "text/html",
    )
    for n in range(20):
        url = URL + f"_next/static/chunks/app/page-{n}.js"
        routes[url] = (200, 'fetch("https://evil.org/papers.json")', "application/javascript")
    result = module.crawl_url(URL, 2025)
    assert result.outcome == "shell"
    assert sum(url.endswith(".js") for url in calls) == 8
    assert not any("evil.org" in url for url in calls)


def test_denial_stops_cli_fallbacks(crawler, monkeypatch, capsys):
    module, calls, routes = crawler
    routes["https://www.sigsac.org/robots.txt"] = (200, "User-agent: *\nDisallow: /", "text/plain")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "crawl_conferences.py",
            "--crawl-content",
            "--conference",
            "ccs",
            "--year",
            "2025",
            "--format",
            "json",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code == 1
    assert json.loads(capsys.readouterr().out)["outcome"] == "policy-denied"
    assert calls == ["https://www.sigsac.org/robots.txt"]


def test_actual_bad_import_process(tmp_path):
    source = tmp_path / "bhus25-sessions.json"
    source.write_text((FIXTURES / "blackhat-denied.html").read_text())
    process = subprocess.run(
        [
            sys.executable,
            str(MAINTAINER / "import_bh.py"),
            str(source),
            "--output-dir",
            str(tmp_path / "cache"),
        ],
        capture_output=True,
        text=True,
    )
    assert process.returncode == 1
    assert "import failed" in process.stderr
    assert not (tmp_path / "cache").exists()


def test_population_unsupported_and_explicit_year(crawler, monkeypatch, tmp_path, capsys):
    module = importlib.import_module("populate_cache")
    monkeypatch.setattr(
        sys,
        "argv",
        ["populate_cache.py", "--venue", "pets", "--year", "2026", "--output-dir", str(tmp_path)],
    )
    monkeypatch.setattr(module, "RESOURCES", tmp_path)
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code == 1
    result = json.loads((tmp_path / "academic/2026/pets/refresh.json").read_text())
    assert result["outcome"] == "unsupported"
    assert "unsupported" in capsys.readouterr().out
    assert not list(tmp_path.glob("*/2025/*/refresh.json"))


def test_denied_linked_data_does_not_escalate(crawler):
    module, calls, routes = crawler
    routes["https://www.sigsac.org/robots.txt"] = (
        200,
        "User-agent: *\nDisallow: /ccs/CCS2025/assets/",
        "text/plain",
    )
    conf = module.select_confs(module.ACADEMIC_CONFS, "ccs")[0]
    result = module.crawl_raw_page(conf, 2025)
    assert result.outcome == "policy-denied"
    assert not any(url.endswith(".json") or url.endswith("/program/") for url in calls)


def test_json_type_mismatch(crawler):
    module, _, routes = crawler
    routes[URL] = (200, "<html>Not a JSON program</html>", "application/json")
    assert module.crawl_url(URL, 2025).outcome == "invalid-json"


def test_relative_json_from_chunk(crawler):
    module, _, routes = crawler
    page = '<title>CCS 2025</title><script src="_next/static/chunks/app/page.js"></script>'
    routes[URL] = (200, page, "text/html")
    routes[URL + "_next/static/chunks/app/page.js"] = (
        200,
        'fetch("papers.json")',
        "application/javascript",
    )
    routes[URL + "_next/static/chunks/app/papers.json"] = (
        200,
        '[{"title":"Relative program paper"}]',
        "application/json",
    )
    assert "Relative program paper" in module.crawl_url(URL, 2025).body


def test_failed_refresh_retains_age_and_records(crawler, monkeypatch, tmp_path):
    module = importlib.import_module("populate_cache")
    policy = importlib.import_module("fetch_policy")
    monkeypatch.setattr(module, "RESOURCES", tmp_path)
    monkeypatch.setattr(module, "FETCHER", policy.Fetcher())
    index = tmp_path / "academic/2025/ccs/index.json"
    index.parent.mkdir(parents=True)
    index.write_text(
        json.dumps(
            {
                "conference": {"year": 2025},
                "papers": [{"title": "Earlier paper", "authors": ["Researcher"]}],
                "coverage": {"last_crawled": "2025-01-01"},
            }
        )
    )
    _, calls, routes = crawler
    routes["https://dblp.org/robots.txt"] = (
        200,
        (FIXTURES / "robots-dblp.org.txt").read_text(),
        "text/plain",
    )
    before = index.read_bytes()
    assert module.refresh_one("academic", "ccs", 2025) is False
    assert index.read_bytes() == before
    manifest = module.build_manifest(tmp_path)
    venue = manifest["coverage"]["academic"]["venues"]["ccs"]
    assert venue["quality"]["2025"]["last_crawled"] == "2025-01-01"
    assert venue["refresh"]["2025"]["outcome"] == "policy-denied"
    assert not any(url.endswith(".xml") for url in calls)


def test_unsafe_asset_schemes_are_ignored(crawler):
    module, calls, routes = crawler
    routes[URL] = (
        200,
        "<title>CCS 2025</title><h1>Program</h1><p>Published papers</p>"
        '<a href="javascript:papers.json">data</a>',
        "text/html",
    )
    result = module.crawl_url(URL, 2025)
    assert result.outcome == "ok"
    assert calls == ["https://www.sigsac.org/robots.txt", URL]


def test_population_rejects_stale_edition(crawler, monkeypatch):
    module = importlib.import_module("populate_cache")
    _, _, routes = crawler
    policy = importlib.import_module("fetch_policy")
    monkeypatch.setattr(module, "FETCHER", policy.Fetcher())
    url = "https://www.sigsac.org/ccs/CCS2025/accepted-papers/"
    routes[url] = (
        200,
        "<title>CCS 2024</title><p>2025 data conflicting with stale title</p>",
        "text/html",
    )
    with pytest.raises(module.RefreshError) as exc:
        module._fetch_body(url)
    assert exc.value.result.outcome == "needs-review"


def test_empty_json_is_explicit(crawler):
    module, _, routes = crawler
    routes[URL] = (200, "{}", "application/json")
    result = module.crawl_url(URL, 2025)
    assert result.outcome == "empty-data"
    assert result.status == 200
    assert result.body == "{}"

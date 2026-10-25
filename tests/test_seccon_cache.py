"""Offline cache regressions from the seccon investigation."""

import importlib
import json
import sys
from pathlib import Path

import pytest

MAINTAINER = Path(__file__).resolve().parents[1] / "plugins/seccon/maintainer"
sys.path.insert(0, str(MAINTAINER))
import import_bh  # noqa: E402
import populate_cache  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures/seccon"


@pytest.mark.parametrize("attempt", [1, 2])
def test_offensivecon_keeps_real_talks(tmp_path, monkeypatch, attempt):
    monkeypatch.setattr(populate_cache, "RESOURCES", tmp_path)
    html = (FIXTURES / f"offensive-{attempt}.html").read_text()
    monkeypatch.setattr(populate_cache, "_fetch_body", lambda *a, **kw: html)
    assert populate_cache.crawl_offensivecon_year(2025) == 17
    index = json.loads((tmp_path / "industry/2025/offensivecon/index.json").read_text())
    entrysign = next(t for t in index["talks"] if t["title"].startswith("Entrysign:"))
    assert entrysign["speakers"] == [
        "Matteo Rizzo",
        "Kristoffer `spq` Janke",
        "Eduardo Vela Nava",
        "Josh Eads",
    ]
    assert all(t["speakers"] for t in index["talks"])


def test_import_failure_exit(monkeypatch, tmp_path):
    path = tmp_path / "bhus25-sessions.json"
    path.write_text((FIXTURES / "blackhat-denied.html").read_text())
    monkeypatch.setattr(sys, "argv", ["import_bh.py", str(path)])
    with pytest.raises(SystemExit) as exc:
        import_bh.main()
    assert exc.value.code == 1


def test_import_truthful_coverage(monkeypatch, tmp_path):
    monkeypatch.setattr(import_bh, "RESOURCES", tmp_path / "resources")
    path = tmp_path / "bhus25-sessions.json"
    path.write_text(
        json.dumps(
            {
                "sessions": {
                    "1": {
                        "title": "A GPU assessment",
                        "speakers": [{"person_id": 7}],
                        "description": "Novel fuzzing techniques",
                        "bh_files": {
                            "slides": {"url": "https://example.org/slides.pdf"},
                            "whitepaper": "https://example.org/paper.pdf",
                        },
                    }
                },
                "speakers": {"7": {"first_name": "A", "last_name": "Researcher"}},
            }
        )
    )
    assert import_bh.import_file(str(path)) == ("blackhat-usa", 2025, 1)
    index = json.loads((tmp_path / "resources/industry/2025/blackhat-usa/index.json").read_text())
    assert index["coverage"]["has_slides"] is True
    assert index["coverage"]["has_abstracts"] is True
    assert index["talks"][0]["whitepaper_url"].endswith("paper.pdf")
    assert index["coverage"]["source_acquired_at"] != "2026-04-24"


@pytest.mark.parametrize(
    "data", [[], {"sessions": []}, {"sessions": {}}, {"sessions": {"1": "bad"}}]
)
def test_bad_import_preserves_cache(monkeypatch, tmp_path, data):
    monkeypatch.setattr(import_bh, "RESOURCES", tmp_path / "resources")
    old = tmp_path / "resources/industry/2025/blackhat-usa/index.json"
    old.parent.mkdir(parents=True)
    old.write_text("old cache")
    path = tmp_path / "bhus25-sessions.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        import_bh.import_file(str(path))
    assert old.read_text() == "old cache"


def test_maintenance_horizon():
    assert populate_cache.selected_years(None, current_year=2027) == list(range(2021, 2028))
    assert populate_cache.selected_years([2025, 2023, 2025], current_year=2027) == [2023, 2025]
    with pytest.raises(ValueError):
        populate_cache.selected_years([2000], current_year=2027)


def test_manifest_import_has_no_side_effects(tmp_path, monkeypatch):
    module = importlib.import_module("write_manifest")
    monkeypatch.setattr(module, "RESOURCES", tmp_path)
    assert module.build_manifest()["cached_range"]["latest"] >= 2026


def test_offensivecon_structure_edges(tmp_path, monkeypatch):
    monkeypatch.setattr(populate_cache, "RESOURCES", tmp_path)
    html = """<div class="col-sm-8 extra">A &amp; B by <b>Alice</b> and <b>Bob</b></div>
    <div class="col-sm-8"><a href="/talks/keynote">Keynote</a></div>
    <div class="col-sm-8">Lunch</div><div class="col-sm-8">No speaker or link</div>"""
    monkeypatch.setattr(populate_cache, "_fetch_body", lambda *a, **kw: html)
    assert populate_cache.crawl_offensivecon_year(2025) == 2
    path = tmp_path / "industry/2025/offensivecon/index.json"
    talks = json.loads(path.read_text())["talks"]
    assert talks[0]["title"] == "A & B"
    assert talks[0]["speakers"] == ["Alice", "Bob"]
    assert talks[1]["session_url"].endswith("/talks/keynote")
    monkeypatch.setattr(
        populate_cache, "_fetch_body", lambda *a, **kw: '<div class="col-sm-8">Lunch</div>'
    )
    before = path.read_bytes()
    assert populate_cache.crawl_offensivecon_year(2025) == 0
    assert path.read_bytes() == before


def test_import_partial_batch(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(import_bh, "RESOURCES", tmp_path / "resources")
    bad = tmp_path / "bhus25-sessions.json"
    bad.write_text("not JSON")
    good = tmp_path / "bheu25-sessions.json"
    good.write_text(
        json.dumps(
            {
                "sessions": {
                    "1": {
                        "title": "Keynote",
                        "speakers": [{"role": "Alice"}],
                        "bh_files": {"slides": "https://example.org/slides.pdf"},
                    }
                }
            }
        )
    )
    monkeypatch.setattr(sys, "argv", ["import_bh.py", str(bad), str(good)])
    with pytest.raises(SystemExit) as exc:
        import_bh.main()
    assert exc.value.code == 1
    assert (tmp_path / "resources/industry/2025/blackhat-eu/index.json").exists()
    assert "bhus25-sessions.json" in capsys.readouterr().err


def test_recon_working_static(tmp_path, monkeypatch):
    monkeypatch.setattr(populate_cache, "RESOURCES", tmp_path)
    monkeypatch.setattr(
        populate_cache, "_fetch_body", lambda *a, **kw: (FIXTURES / "recon2025.html").read_text()
    )
    assert populate_cache.crawl_recon_year(2025) == 26


def test_manifest_quality_and_future_year(tmp_path, monkeypatch):
    module = importlib.import_module("write_manifest")
    monkeypatch.setattr(module, "RESOURCES", tmp_path)
    idx = tmp_path / "industry/2028/offensivecon/index.json"
    idx.parent.mkdir(parents=True)
    idx.write_text(
        json.dumps(
            {
                "conference": {"year": 2028},
                "talks": [{"title": "Registration", "speakers": []}],
                "coverage": {"last_crawled": "2020-01-01"},
            }
        )
    )
    manifest = module.build_manifest()
    venue = manifest["coverage"]["industry"]["venues"]["offensivecon"]
    assert manifest["cached_range"]["latest"] == 2028
    assert 2028 in venue["cached"]  # Availability is separate from quality.
    assert venue["quality"]["2028"]["outcome"] == "needs-review"
    assert venue["quality"]["2028"]["last_crawled"] == "2020-01-01"


def test_atomic_write_retains_previous_index(tmp_path, monkeypatch):
    module = importlib.import_module("cache_io")
    index = tmp_path / "index.json"
    index.write_text("old cache")

    def fail(*args):
        raise OSError("interrupted replacement")

    monkeypatch.setattr(module.os, "replace", fail)
    with pytest.raises(OSError, match="interrupted"):
        module.write_json(index, {"talks": []})
    assert index.read_text() == "old cache"
    assert list(tmp_path.iterdir()) == [index]


def test_rss_is_partial_and_filtered_by_selected_year(tmp_path, monkeypatch):
    monkeypatch.setattr(populate_cache, "RESOURCES", tmp_path)
    monkeypatch.setattr(
        populate_cache,
        "_fetch_body",
        lambda *a, **kw: (
            """<feed>
        <entry><title>Hardwear.io NL 2026: Research by Alice</title>
        <yt:videoId>one</yt:videoId></entry>
        <entry><title>Hardwear.io NL 2025: Older talk</title><yt:videoId>two</yt:videoId></entry>
        </feed>"""
        ),
    )
    assert populate_cache.crawl_hardwear_year(2026) == 1
    index = json.loads((tmp_path / "industry/2026/hardwear/index.json").read_text())
    assert index["talks"][0]["title"] == "Research"
    assert index["coverage"]["source_scope"] == "YouTube RSS (limited)"
    assert index["coverage"]["last_crawled"] is None


def test_academic_coverage_uses_acquisition_time(tmp_path, monkeypatch):
    policy = importlib.import_module("fetch_policy")
    monkeypatch.setattr(populate_cache, "RESOURCES", tmp_path)
    url = populate_cache.DBLP_XML_URLS["ccs"].format(year=2025)
    monkeypatch.setitem(
        populate_cache.FETCHED, url, policy.FetchResult(url, acquired_at="2025-07-10T00:00:00Z")
    )
    populate_cache.write_academic_index("ccs", 2025, [{"title": "A paper", "authors": ["Alice"]}])
    index = json.loads((tmp_path / "academic/2025/ccs/index.json").read_text())
    assert index["coverage"]["last_crawled"] == "2025-07-10T00:00:00Z"


def test_partial_rss_does_not_replace_older_records(tmp_path, monkeypatch):
    monkeypatch.setattr(populate_cache, "RESOURCES", tmp_path)
    path = tmp_path / "industry/2026/hardwear/index.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "conference": {"year": 2026},
                "talks": [
                    {
                        "title": "Older talk outside RSS window",
                        "video_url": "https://example.org/old",
                    }
                ],
            }
        )
    )
    before = path.read_bytes()
    monkeypatch.setattr(
        populate_cache,
        "_fetch_body",
        lambda *a, **kw: (
            """<feed><entry>
        <title>Hardwear.io NL 2026: Recent talk by Alice</title><yt:videoId>new</yt:videoId>
        </entry></feed>"""
        ),
    )
    assert populate_cache.refresh_one("industry", "hardwear", 2026) is False
    assert path.read_bytes() == before
    refresh = json.loads(path.with_name("refresh.json").read_text())
    assert refresh["outcome"] == "needs-review"


@pytest.mark.parametrize(
    "session,people",
    [
        ({"title": 1}, {}),
        ({"title": "Talk", "speakers": "bad"}, {}),
        ({"title": "Talk", "speakers": ["bad"]}, {}),
        ({"title": "Talk", "speakers": [{"person_id": 1}]}, {"1": "bad"}),
        ({"title": "Talk", "speakers": [{"person_id": 1}]}, {"1": {"first_name": 1}}),
        ({"title": "Talk", "speakers": [{"role": 1}]}, {}),
        ({"title": "Talk", "speakers": [{"role": "Alice"}], "description": 1}, {}),
        ({"title": "Talk", "speakers": [{"role": "Alice"}], "bh_files": [1]}, {}),
        ({"title": "Talk", "speakers": [{"role": "Alice"}], "bh_files": {"slides": 1}}, {}),
    ],
)
def test_malformed_session_details_are_actionable(session, people):
    with pytest.raises(ValueError):
        import_bh.parse_sessions({"sessions": {"1": session}, "speakers": people}, "bhus25")


def test_missing_and_misnamed_imports_fail(tmp_path):
    with pytest.raises(ValueError, match="Filename"):
        import_bh.import_file(str(tmp_path / "wrong.json"))
    with pytest.raises(OSError):
        import_bh.import_file(str(tmp_path / "bhus25-sessions.json"))


def test_manifest_invalid_json_is_reviewable(tmp_path, monkeypatch):
    module = importlib.import_module("write_manifest")
    index = tmp_path / "industry/2026/offensivecon/index.json"
    index.parent.mkdir(parents=True)
    index.write_text("<html>not JSON</html>")
    manifest = module.build_manifest(tmp_path)
    assert (
        manifest["coverage"]["industry"]["venues"]["offensivecon"]["quality"]["2026"]["outcome"]
        == "needs-review"
    )


def test_defcon_edition_does_not_shift_with_current_year():
    assert populate_cache._defcon_edition(2025) == 33
    assert populate_cache._defcon_edition(2026) == 34

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from bioproject_inspector import web

FAKE = "# BioProject report: PRJNA1\n\n## Findings\n- [WARNING] test <b>x</b>\n"


def test_home_ok():
    assert TestClient(web.app).get("/").status_code == 200


def test_report_renders_and_escapes(monkeypatch):
    monkeypatch.setattr(web, "build_report", lambda acc: FAKE)
    r = TestClient(web.app).get("/report", params={"accession": "prjna1"})
    assert r.status_code == 200
    assert "<h1>BioProject report: PRJNA1</h1>" in r.text
    assert "&lt;b&gt;x&lt;/b&gt;" in r.text and "<b>x</b>" not in r.text


def test_invalid_accession_rejected():
    r = TestClient(web.app).get("/report", params={"accession": "<script>"})
    assert r.status_code == 400


def test_error_is_shown(monkeypatch):
    def boom(acc):
        raise RuntimeError("ENA down")
    monkeypatch.setattr(web, "build_report", boom)
    r = TestClient(web.app).get("/report", params={"accession": "PRJNA1"})
    assert r.status_code == 502 and "ENA down" in r.text

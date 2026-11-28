from bioproject_inspector import ncbi


class FakeResp:
    def __init__(self, data):
        self._d = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._d


def test_fetch_bioproject_parses(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        if url.endswith("esearch.fcgi"):
            return FakeResp({"esearchresult": {"idlist": ["42"]}})
        return FakeResp({"result": {"42": {
            "project_title": "T", "project_description": "D",
            "project_data_type": "Raw sequence reads",
            "submitter_organization": "Org",
            "registration_date": "2020/01/01 00:00"}}})
    monkeypatch.setattr(ncbi.requests, "get", fake_get)
    info = ncbi.fetch_bioproject("PRJNA1")
    assert info["title"] == "T"
    assert info["organization"] == "Org"
    assert info["registered"] == "2020/01/01"


def test_fetch_bioproject_returns_none_on_error(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network down")
    monkeypatch.setattr(ncbi.requests, "get", boom)
    assert ncbi.fetch_bioproject("PRJNA1") is None

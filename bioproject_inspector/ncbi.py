"""Optional NCBI BioProject lookup via E-utilities (read-only, best effort)."""
import requests

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def fetch_bioproject(accession, timeout=15):
    """Return a dict of NCBI BioProject fields, or None if anything goes wrong."""
    try:
        r = requests.get(BASE + "esearch.fcgi", params={
            "db": "bioproject", "term": "%s[Project Accession]" % accession,
            "retmode": "json"}, timeout=timeout)
        r.raise_for_status()
        ids = r.json()["esearchresult"]["idlist"]
        if not ids:
            return None
        d = requests.get(BASE + "esummary.fcgi", params={
            "db": "bioproject", "id": ids[0], "retmode": "json"}, timeout=timeout)
        d.raise_for_status()
        doc = d.json()["result"][ids[0]]
    except Exception:
        return None
    return {
        "title": (doc.get("project_title") or "").strip(),
        "description": " ".join((doc.get("project_description") or "").split()),
        "data_type": (doc.get("project_data_type") or "").strip(),
        "organization": (doc.get("submitter_organization") or "").strip(),
        "registered": (doc.get("registration_date") or "")[:10],
    }

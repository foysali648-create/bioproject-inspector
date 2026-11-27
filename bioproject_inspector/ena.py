"""Core module: fetch run metadata for a BioProject from the ENA Portal API."""
import re
import time
from dataclasses import dataclass, field

import requests

BASE_URL = "https://www.ebi.ac.uk/ena/portal/api/filereport"
ACCESSION_RE = re.compile(r"^(PRJ(NA|EB|DB)\d+|[SED]RP\d+)$", re.IGNORECASE)

FIELDS = [
    "run_accession", "experiment_accession", "sample_accession",
    "study_accession", "scientific_name", "instrument_platform",
    "instrument_model", "library_strategy", "library_source",
    "library_selection", "library_layout", "read_count", "base_count",
    "first_public", "sample_alias", "study_title",
    "fastq_bytes", "fastq_md5", "fastq_ftp",
]


class ENAError(Exception):
    """Raised when fetching or parsing ENA data fails."""


def _split(value):
    return [v for v in value.split(";") if v]


def _int(value):
    try:
        return int(value)
    except ValueError:
        return 0


@dataclass
class Run:
    run_accession: str
    experiment_accession: str = ""
    sample_accession: str = ""
    study_accession: str = ""
    scientific_name: str = ""
    instrument_platform: str = ""
    instrument_model: str = ""
    library_strategy: str = ""
    library_source: str = ""
    library_selection: str = ""
    library_layout: str = ""
    read_count: int = 0
    base_count: int = 0
    first_public: str = ""
    sample_alias: str = ""
    study_title: str = ""
    fastq_ftp: list = field(default_factory=list)
    fastq_bytes: list = field(default_factory=list)
    fastq_md5: list = field(default_factory=list)

    @classmethod
    def from_row(cls, row):
        def g(key):
            return row.get(key, "")

        return cls(
            run_accession=g("run_accession"),
            experiment_accession=g("experiment_accession"),
            sample_accession=g("sample_accession"),
            study_accession=g("study_accession"),
            scientific_name=g("scientific_name"),
            instrument_platform=g("instrument_platform"),
            instrument_model=g("instrument_model"),
            library_strategy=g("library_strategy"),
            library_source=g("library_source"),
            library_selection=g("library_selection"),
            library_layout=g("library_layout"),
            read_count=_int(g("read_count")),
            base_count=_int(g("base_count")),
            first_public=g("first_public"),
            sample_alias=g("sample_alias"),
            study_title=g("study_title"),
            fastq_ftp=_split(g("fastq_ftp")),
            fastq_bytes=[_int(x) for x in _split(g("fastq_bytes"))],
            fastq_md5=_split(g("fastq_md5")),
        )


def parse_filereport(text):
    """Parse ENA filereport TSV text into a list of Run objects.

    Raises ENAError if a row has a different column count than the header,
    so a truncated download can never silently produce wrong data.
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    header = lines[0].split("\t")
    runs = []
    for n, line in enumerate(lines[1:], start=2):
        parts = line.split("\t")
        if len(parts) != len(header):
            raise ENAError("line %d: column count mismatch (response may be truncated)" % n)
        runs.append(Run.from_row(dict(zip(header, parts))))
    return runs


def fetch_runs(accession, retries=3):
    acc = accession.strip().upper()
    if not ACCESSION_RE.match(acc):
        raise ValueError("Unrecognised accession format: %r (example: PRJNA633959)" % accession)

    params = {
        "accession": acc,
        "result": "read_run",
        "fields": ",".join(FIELDS),
        "format": "tsv",
    }
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(BASE_URL, params=params, timeout=(10, 120))
            if r.status_code == 200:
                try:
                    runs = parse_filereport(r.text)
                except ENAError as e:
                    last_err = e
                else:
                    if not runs:
                        raise ENAError("No runs found in ENA for %s" % acc)
                    return runs
            elif r.status_code in (400, 404):
                raise ENAError("ENA rejected the request: %s %s" % (r.status_code, r.text[:200]))
            else:
                last_err = ENAError("HTTP %s" % r.status_code)
        except requests.RequestException as e:
            last_err = e
        time.sleep(2 ** attempt)
    raise ENAError("Failed after %d attempts: %s" % (retries, last_err))

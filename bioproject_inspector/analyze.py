"""Classify a BioProject and run sanity checks on its ENA run metadata."""
from collections import Counter
from dataclasses import dataclass

from bioproject_inspector.files import split_files

# Heuristic minimum read counts per library strategy (adjust for your study).
LOW_READS = {"AMPLICON": 5000, "WGS": 1000000, "RNA-Seq": 1000000}
LARGE_DOWNLOAD_GB = 50


@dataclass
class Finding:
    level: str  # "warning" or "info"
    code: str
    message: str


def _top(counter):
    return counter.most_common(1)[0][0] if counter else ""


def classify(runs):
    strategies = Counter(r.library_strategy for r in runs)
    sources = Counter(r.library_source for r in runs)
    strategy, source = _top(strategies), _top(sources)
    if len(strategies) > 1:
        return "Mixed (%s)" % ", ".join(sorted(strategies))
    if strategy == "AMPLICON":
        return "Amplicon sequencing (e.g. 16S/ITS; target gene is not in ENA metadata)"
    if strategy == "WGS" and source == "METAGENOMIC":
        return "Shotgun metagenome"
    if strategy == "WGS":
        return "Whole-genome sequencing (%s)" % (source.lower() or "source unknown")
    if strategy == "RNA-Seq" and source == "METATRANSCRIPTOMIC":
        return "Metatranscriptome (RNA-Seq)"
    return strategy or "Unknown"


def check(runs):
    """Return a list of Finding objects describing possible problems."""
    findings = []
    n = len(runs)
    strategies = Counter(r.library_strategy for r in runs)
    layouts = Counter(r.library_layout for r in runs)
    platforms = Counter(r.instrument_platform for r in runs)
    organisms = Counter(r.scientific_name for r in runs)
    samples = {r.sample_accession for r in runs}

    def add(level, code, message):
        findings.append(Finding(level, code, message))

    def eg(items):
        return ", ".join(items[:3])

    if len(strategies) > 1:
        add("warning", "mixed_strategy",
            "Several library strategies in one project: %s. Analyse each type separately." % dict(strategies))
    if len(layouts) > 1:
        add("warning", "mixed_layout",
            "Both paired and single-end runs: %s. Use separate commands for each layout." % dict(layouts))
    if len(platforms) > 1:
        add("warning", "mixed_platform",
            "Different sequencing platforms: %s. Expect batch effects and different error profiles." % dict(platforms))
    if len(organisms) > 1:
        add("info", "multiple_organisms", "Several organism labels: %s." % dict(organisms))

    no_fastq = [r.run_accession for r in runs if not r.fastq_ftp]
    if no_fastq:
        add("warning", "missing_fastq",
            "%d runs have no FASTQ on ENA (e.g. %s). They may only be available through SRA." % (len(no_fastq), eg(no_fastq)))

    bad_pairs = []
    extra_file = []
    for r in runs:
        if r.library_layout == "PAIRED" and r.fastq_ftp:
            r1, r2, other = split_files(r)
            if not r1 or not r2:
                bad_pairs.append(r.run_accession)
            elif other:
                extra_file.append(r.run_accession)
    if bad_pairs:
        add("warning", "paired_file_count",
            "%d paired runs lack a _1 or _2 FASTQ file (e.g. %s). Check them before processing." % (len(bad_pairs), eg(bad_pairs)))
    if extra_file:
        add("info", "extra_unpaired_file",
            "%d paired runs also have an extra unsuffixed FASTQ file (e.g. %s). It is not part of the _1/_2 pair; leave it out of a standard paired-end command." % (len(extra_file), eg(extra_file)))

    top = _top(strategies)
    threshold = LOW_READS.get(top)
    if threshold:
        low = [r.run_accession for r in runs if 0 < r.read_count < threshold]
        if low:
            add("warning", "low_reads",
                "%d runs have fewer than %s reads (heuristic threshold for %s; e.g. %s)." % (len(low), format(threshold, ","), top, eg(low)))

    if len(samples) == 1 and n > 1:
        add("warning", "one_sample_many_runs",
            "%d runs share a single sample accession. Check sample_alias and experiment_accession: the submitter may have registered one sample for many libraries, or sample metadata is incomplete." % n)

    total_gb = sum(sum(r.fastq_bytes) for r in runs) / 1e9
    if total_gb > LARGE_DOWNLOAD_GB:
        add("warning", "large_download",
            "Total FASTQ size is %.0f GB. Check free disk space before downloading; consider a subset." % total_gb)

    return findings

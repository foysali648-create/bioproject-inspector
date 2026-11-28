"""Build a full text report for a BioProject (metadata only, no downloads)."""
from collections import Counter

from bioproject_inspector.ena import fetch_runs
from bioproject_inspector.analyze import classify, check
from bioproject_inspector.hints import checklist
from bioproject_inspector.ncbi import fetch_bioproject


def build_report(accession):
    acc = accession.strip().upper()
    runs = fetch_runs(acc)
    samples = {r.sample_accession for r in runs}
    total_gb = sum(sum(r.fastq_bytes) for r in runs) / 1e9
    out = ["# BioProject report: %s" % acc]
    titles = sorted({r.study_title for r in runs if r.study_title})
    if titles:
        out.append("Title: %s" % titles[0])
    info = fetch_bioproject(acc)
    if info:
        if info["title"]:
            out.append("NCBI title: %s" % info["title"])
        if info["data_type"]:
            out.append("NCBI data type: %s" % info["data_type"])
        if info["organization"]:
            out.append("Submitter organization: %s" % info["organization"])
        if info["registered"]:
            out.append("Registered at NCBI: %s" % info["registered"])
        if info["description"]:
            d = info["description"]
            out.append("NCBI description: %s" % (d[:400] + ("..." if len(d) > 400 else "")))
    out.append("")
    out.append("Type: %s" % classify(runs))
    out.append("Runs: %d | Sample accessions in ENA: %d | FASTQ size: %.1f GB"
               % (len(runs), len(samples), total_gb))
    for label, attr in [("Strategy", "library_strategy"), ("Source", "library_source"),
                        ("Layout", "library_layout"), ("Platform", "instrument_platform"),
                        ("Organism", "scientific_name")]:
        c = Counter(getattr(r, attr) or "unknown" for r in runs)
        out.append("%s: %s" % (label, ", ".join("%s (%d)" % kv for kv in c.most_common())))
    out.append("")
    out.append("## Findings")
    findings = check(runs)
    if not findings:
        out.append("No warnings.")
    for f in findings:
        out.append("- [%s] %s" % (f.level.upper(), f.message))
    out.append("")
    out.append("## Checklist")
    for title, steps in checklist(runs).items():
        out.append("### " + title)
        for s in steps:
            out.append("- " + s)
        out.append("")
    out.append("## Download")
    out.append("This report downloads nothing. For a disk-aware script run: "
               "python download_cli.py %s --max-runs N --outdir DIR" % acc)
    return "\n".join(out) + "\n"

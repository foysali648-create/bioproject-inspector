"""QC checklist and pipeline hints, chosen by data type."""
from collections import Counter


def _top(counter):
    return counter.most_common(1)[0][0] if counter else ""


COMMON = [
    "Verify every downloaded file against the MD5 value listed by ENA.",
    "Run FastQC on a few files and summarise all of them with MultiQC before any analysis.",
    "Match run accessions to your sample metadata (group, age, sex, batch) using the paper's supplementary table; ENA metadata alone is usually not enough.",
]

AMPLICON = [
    "Confirm the target region and primer sequences from the paper or the SRA experiment description (ENA metadata does not state them).",
    "Remove primers and adapters (for example with cutadapt) before denoising.",
    "Check that forward and reverse reads overlap enough for the amplicon length; if not, consider using forward reads only.",
    "Denoise to ASVs (DADA2, or the DADA2/Deblur plugins in QIIME2) and choose truncation lengths from the quality plots.",
    "Assign taxonomy with a reference database that suits the region (for example SILVA or Greengenes2).",
    "Check per-sample read depth after filtering and pick a depth cut-off before diversity analysis.",
    "If the study has negative controls or mock communities, inspect them before trusting rare taxa.",
]

SHOTGUN = [
    "Trim adapters and low-quality bases (fastp or Trimmomatic).",
    "If the samples come from a host (for example human gut), remove host reads by mapping to the host genome and keeping unmapped reads, before profiling.",
    "Run taxonomic profiling (MetaPhlAn, or Kraken2 with Bracken). Check the database memory need against your RAM; smaller prebuilt databases exist.",
    "Functional profiling (for example HUMAnN) is heavy; test the whole pipeline on 1-2 samples first.",
    "Process samples one at a time or in small batches, and delete raw files only after you have verified the results.",
]

RNASEQ = [
    "Check strandedness and read length before choosing aligner or quantifier settings.",
    "Trim adapters, align or pseudo-align, and check mapping rate per sample.",
]

PAIRED = [
    "Paired-end data: always process _1 and _2 together and keep them in the same order.",
]


def checklist(runs):
    """Return a dict of section name -> list of steps for this project."""
    strategy = _top(Counter(r.library_strategy for r in runs))
    layout = _top(Counter(r.library_layout for r in runs))
    sections = {"General": list(COMMON)}
    if strategy == "AMPLICON":
        sections["Amplicon (16S/ITS) workflow"] = list(AMPLICON)
    elif strategy == "WGS":
        sections["Shotgun / WGS workflow"] = list(SHOTGUN)
    elif strategy == "RNA-Seq":
        sections["RNA-Seq workflow"] = list(RNASEQ)
    if layout == "PAIRED":
        sections["Paired-end handling"] = list(PAIRED)
    return sections

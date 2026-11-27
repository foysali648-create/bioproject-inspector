# bioproject-inspector

Unofficial community tool. Not affiliated with NCBI or EMBL-EBI.

Give it a BioProject accession (for example PRJNA633959) and it reads run
metadata from the ENA Portal API and tells you, before you download anything:

- what kind of data it is (amplicon, shotgun metagenome, and so on)
- sanity warnings: mixed layouts or platforms, missing FASTQ files, low read
  counts, one sample accession shared by many runs, very large downloads
- a QC and analysis checklist for that data type
- a disk-aware download script that fetches only the _1/_2 FASTQ files, checks
  free space, resumes interrupted downloads and verifies MD5 checksums

The report step downloads nothing and needs almost no disk space.

## Install

    pip install -e .

## Use

    bioproject-inspector PRJNA633959 --out report.md
    python download_cli.py PRJNA679346 --max-runs 2 --outdir data --script dl.sh

## Limits

- Relies on ENA metadata. The sequenced gene or region of an amplicon study is
  not in that metadata, so check the paper.
- Read-count thresholds and checklists are rules of thumb, not a substitute
  for reading the study.
- Subsets from --max-runs follow the metadata order and may not be balanced
  between groups.

## Tests

    pip install pytest
    python -m pytest -q

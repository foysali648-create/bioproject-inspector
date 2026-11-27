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

For the web interface also install FastAPI and Uvicorn:

    pip install fastapi uvicorn

## Use

Command line report:

    bioproject-inspector PRJNA633959 --out report.md

Web interface (light and dark theme), then open http://127.0.0.1:8000 :

    uvicorn bioproject_inspector.web:app

A JSON/markdown endpoint is also available at /api/report/PRJNA633959 and the
interactive API docs at /docs.

Disk-aware download script (it only writes a script; nothing is downloaded
until you run it with bash):

    python download_cli.py PRJNA679346 --max-runs 2 --outdir data --script dl.sh
    python download_cli.py PRJNA679346 --max-gb 20 --include-singletons

By default only the _1/_2 files of paired runs are included. Use
--include-singletons to also fetch the unpaired file that some paired runs
have. To resume a partly finished download on a nearly full disk:

    SKIP_SPACE_CHECK=1 bash dl.sh

## Examples

| Accession | What the tool reports |
|---|---|
| PRJNA633959 | Amplicon, 171 paired Illumina runs; warns that all runs share one sample_alias |
| PRJNA1506799 | Amplicon, 41 paired Illumina runs, 1.7 GB |
| PRJNA679346 | Shotgun metagenome, 43 paired runs, 632 GB; warns about size and extra unpaired files |

## Limits

- Relies on ENA metadata. The sequenced gene or region of an amplicon study is
  not in that metadata, so check the paper.
- Only projects with sequencing runs in ENA can be inspected. Some BioProjects
  hold only assemblies or other data, or are not public yet; they return no runs.
- Read-count thresholds and checklists are rules of thumb, not a substitute
  for reading the study.
- Subsets from --max-runs follow the metadata order and may not be balanced
  between groups.
- Under WSL the free space shown is the virtual disk's; the Windows drive that
  holds it may have much less.

## Tests

    pip install pytest httpx fastapi
    python -m pytest -q

## License

MIT

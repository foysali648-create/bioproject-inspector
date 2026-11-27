"""Helpers for working with ENA FASTQ file lists."""
import os


def split_files(run):
    """Return (r1, r2, other) FASTQ URLs for a run, split by file name."""
    r1 = ""
    r2 = ""
    other = []
    for url in run.fastq_ftp:
        name = os.path.basename(url)
        if name.endswith("_1.fastq.gz"):
            r1 = url
        elif name.endswith("_2.fastq.gz"):
            r2 = url
        else:
            other.append(url)
    return r1, r2, other

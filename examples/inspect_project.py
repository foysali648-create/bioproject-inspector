import sys
from collections import Counter
from bioproject_inspector.ena import fetch_runs

runs = fetch_runs(sys.argv[1])
print("runs:", len(runs))
print("distinct sample_alias:", len({r.sample_alias for r in runs}))
print("distinct experiment_accession:", len({r.experiment_accession for r in runs}))
print("sample_alias examples:", [r.sample_alias for r in runs[:3]])
print("files per run:", dict(Counter(len(r.fastq_ftp) for r in runs)))
r = runs[0]
print("example run:", r.run_accession, r.library_layout)
for u, b in zip(r.fastq_ftp, r.fastq_bytes):
    print("  ", u, b)

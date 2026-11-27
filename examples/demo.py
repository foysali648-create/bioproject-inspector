import sys
from collections import Counter
from bioproject_inspector.ena import fetch_runs

acc = sys.argv[1]
runs = fetch_runs(acc)
samples = {r.sample_accession for r in runs}
print("%s: %d runs, %d samples" % (acc, len(runs), len(samples)))
for label, attr in [("Strategy", "library_strategy"), ("Source", "library_source"),
                    ("Layout", "library_layout"), ("Platform", "instrument_platform"),
                    ("Organism", "scientific_name")]:
    print("%-9s" % label, dict(Counter(getattr(r, attr) for r in runs)))
total_gb = sum(sum(r.fastq_bytes) for r in runs) / 1e9
print("Total FASTQ size: %.1f GB" % total_gb)

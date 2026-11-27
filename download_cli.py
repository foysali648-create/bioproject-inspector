import argparse
import os
import shutil

from bioproject_inspector.ena import fetch_runs
from bioproject_inspector.download import select_runs, make_script

p = argparse.ArgumentParser(description="Generate a disk-aware download script")
p.add_argument("accession")
p.add_argument("--max-runs", type=int)
p.add_argument("--max-gb", type=float)
p.add_argument("--outdir", default="data")
p.add_argument("--script", default="download.sh")
a = p.parse_args()

runs = fetch_runs(a.accession)
chosen, total = select_runs(runs, a.max_runs, a.max_gb)
if not chosen:
    raise SystemExit("No runs fit the limits. Raise --max-gb or --max-runs.")

target = a.outdir if os.path.isdir(a.outdir) else "."
free = shutil.disk_usage(target).free
print("Selected %d of %d runs, %.1f GB to download" % (len(chosen), len(runs), total / 1e9))
print("Free disk space at %s: %.1f GB" % (target, free / 1e9))
if total * 1.1 > free:
    print("WARNING: not enough free space for this selection.")

with open(a.script, "w") as fh:
    fh.write(make_script(chosen, a.outdir))
print("Wrote %s (run it with: bash %s)" % (a.script, a.script))

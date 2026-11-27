import sys
from bioproject_inspector.ena import fetch_runs
from bioproject_inspector.analyze import classify, check

acc = sys.argv[1]
runs = fetch_runs(acc)
samples = {r.sample_accession for r in runs}
print("%s: %d runs, %d samples" % (acc, len(runs), len(samples)))
print("Type:", classify(runs))
findings = check(runs)
if not findings:
    print("No warnings.")
for f in findings:
    print("[%s] %s: %s" % (f.level.upper(), f.code, f.message))

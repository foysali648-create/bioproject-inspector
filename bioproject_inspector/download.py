"""Generate a disk-aware download script for a BioProject."""
import shlex

from bioproject_inspector.files import split_files


def wanted_files(run, include_singletons=False):
    """Files to download as (url, bytes, md5): _1/_2 for paired runs, all files otherwise."""
    sizes = dict(zip(run.fastq_ftp, run.fastq_bytes))
    md5s = dict(zip(run.fastq_ftp, run.fastq_md5))
    if run.library_layout == "PAIRED":
        r1, r2, other = split_files(run)
        urls = [u for u in (r1, r2) if u]
        if include_singletons:
            urls += other
    else:
        urls = list(run.fastq_ftp)
    return [(u, sizes.get(u, 0), md5s.get(u, "")) for u in urls]


def select_runs(runs, max_runs=None, max_gb=None, include_singletons=False):
    """Pick runs in order until a run or size limit would be exceeded."""
    chosen = []
    total = 0
    for r in runs:
        if max_runs is not None and len(chosen) >= max_runs:
            break
        size = sum(b for _, b, _ in wanted_files(r, include_singletons))
        if max_gb is not None and total + size > max_gb * 1e9:
            break
        chosen.append(r)
        total += size
    return chosen, total


def make_script(runs, outdir, include_singletons=False):
    """Return the text of a bash script that downloads and verifies the files."""
    files = []
    for r in runs:
        files.extend(wanted_files(r, include_singletons))
    need = int(sum(b for _, b, _ in files) * 1.1)
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "OUTDIR=%s" % shlex.quote(outdir),
        'mkdir -p "$OUTDIR"',
        "NEED=%d" % need,
        'AVAIL=$(df --output=avail -B1 "$OUTDIR" | tail -1 | tr -d " ")',
        'if [ "${SKIP_SPACE_CHECK:-0}" != "1" ] && [ "$AVAIL" -lt "$NEED" ]; then',
        '  echo "Not enough free disk space: need $NEED bytes, have $AVAIL bytes" >&2',
        '  echo "(if you are resuming a partial download: SKIP_SPACE_CHECK=1 bash $0)" >&2',
        "  exit 1",
        "fi",
        "",
        "get() {",
        '  url="$1"; md5="$2"; f="$OUTDIR/$(basename "$url")"',
        '  if [ -f "$f" ] && [ -n "$md5" ] && [ "$(md5sum "$f" | cut -d" " -f1)" = "$md5" ]; then',
        '    echo "ok (already downloaded): $f"; return 0',
        "  fi",
        '  wget -c -q --show-progress -P "$OUTDIR" "ftp://$url"',
        '  if [ -n "$md5" ] && [ "$(md5sum "$f" | cut -d" " -f1)" != "$md5" ]; then',
        '    echo "MD5 mismatch: $f (deleted, re-run to retry)" >&2; rm -f "$f"; return 1',
        "  fi",
        "}",
        "",
    ]
    for url, _, md5 in files:
        lines.append("get %s %s" % (shlex.quote(url), shlex.quote(md5)))
    lines.append('echo "Done: %d files in $OUTDIR"' % len(files))
    return "\n".join(lines) + "\n"

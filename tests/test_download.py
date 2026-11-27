from bioproject_inspector.ena import Run
from bioproject_inspector.download import wanted_files, select_runs, make_script


def mk(acc, gb):
    n = int(gb * 1e9)
    return Run(run_accession=acc, library_layout="PAIRED",
               fastq_ftp=["x/%s.fastq.gz" % acc, "x/%s_1.fastq.gz" % acc, "x/%s_2.fastq.gz" % acc],
               fastq_bytes=[999, n, n], fastq_md5=["m0", "m1", "m2"])


def test_wanted_files_skips_extra():
    urls = [u for u, _, _ in wanted_files(mk("R1", 1))]
    assert urls == ["x/R1_1.fastq.gz", "x/R1_2.fastq.gz"]


def test_select_runs_respects_max_gb():
    runs = [mk("R1", 5), mk("R2", 5), mk("R3", 5)]
    chosen, total = select_runs(runs, max_gb=11)
    assert [r.run_accession for r in chosen] == ["R1"]
    assert total == 10 * 10**9


def test_select_runs_respects_max_runs():
    chosen, _ = select_runs([mk("R1", 1), mk("R2", 1)], max_runs=1)
    assert len(chosen) == 1


def test_script_has_disk_check_and_md5():
    script = make_script([mk("R1", 1)], "data")
    assert "NEED=" in script
    assert "md5sum" in script
    assert "ftp://$url" in script
    stripped = script.replace("R1_1.fastq.gz", "").replace("R1_2.fastq.gz", "")
    assert "R1.fastq.gz" not in stripped

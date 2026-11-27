from bioproject_inspector.ena import Run
from bioproject_inspector.analyze import classify, check
from bioproject_inspector.files import split_files


def mk(**kw):
    base = dict(
        run_accession="SRR1", sample_accession="S1",
        library_strategy="AMPLICON", library_source="METAGENOMIC",
        library_layout="PAIRED", instrument_platform="ILLUMINA",
        scientific_name="human gut metagenome", read_count=10000,
        fastq_ftp=["x/a_1.fastq.gz", "x/a_2.fastq.gz"], fastq_bytes=[1, 1],
    )
    base.update(kw)
    return Run(**base)


def codes(runs):
    return {f.code for f in check(runs)}


def two_runs(**second):
    return [mk(run_accession="R1", sample_accession="S1"),
            mk(run_accession="R2", sample_accession="S2", **second)]


def test_classify_amplicon():
    assert classify([mk()]).startswith("Amplicon")


def test_classify_shotgun():
    assert classify([mk(library_strategy="WGS")]) == "Shotgun metagenome"


def test_clean_project_has_no_findings():
    assert check(two_runs()) == []


def test_mixed_layout():
    assert "mixed_layout" in codes(two_runs(library_layout="SINGLE", fastq_ftp=["x/a.fastq.gz"]))


def test_one_sample_many_runs():
    runs = [mk(run_accession="R1"), mk(run_accession="R2")]
    assert "one_sample_many_runs" in codes(runs)


def test_low_reads():
    runs = [mk(run_accession="R1", sample_accession="S1", read_count=100),
            mk(run_accession="R2", sample_accession="S2")]
    assert "low_reads" in codes(runs)


def test_missing_fastq():
    assert "missing_fastq" in codes(two_runs(fastq_ftp=[], fastq_bytes=[]))


def test_split_files():
    r = mk(fastq_ftp=["x/S.fastq.gz", "x/S_1.fastq.gz", "x/S_2.fastq.gz"])
    r1, r2, other = split_files(r)
    assert r1.endswith("S_1.fastq.gz")
    assert r2.endswith("S_2.fastq.gz")
    assert other == ["x/S.fastq.gz"]


def test_extra_file_is_info_not_warning():
    three = ["x/b.fastq.gz", "x/b_1.fastq.gz", "x/b_2.fastq.gz"]
    levels = {f.code: f.level for f in check(two_runs(fastq_ftp=three, fastq_bytes=[1, 1, 1]))}
    assert levels["extra_unpaired_file"] == "info"
    assert "paired_file_count" not in levels

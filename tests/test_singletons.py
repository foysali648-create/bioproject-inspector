from types import SimpleNamespace

from bioproject_inspector.download import wanted_files, make_script

BASE = "ftp.sra.ebi.ac.uk/vol1/fastq/SRR130/070/SRR13083070/SRR13083070"


def paired_run():
    urls = [BASE + ".fastq.gz", BASE + "_1.fastq.gz", BASE + "_2.fastq.gz"]
    return SimpleNamespace(
        fastq_ftp=urls,
        fastq_bytes=[10, 100, 200],
        fastq_md5=["a", "b", "c"],
        library_layout="PAIRED",
    )


def test_singletons_excluded_by_default():
    urls = [u for u, _, _ in wanted_files(paired_run())]
    assert urls == [BASE + "_1.fastq.gz", BASE + "_2.fastq.gz"]


def test_singletons_included_on_request():
    urls = [u for u, _, _ in wanted_files(paired_run(), include_singletons=True)]
    assert BASE + ".fastq.gz" in urls and len(urls) == 3


def test_script_has_resume_and_md5_cleanup():
    script = make_script([paired_run()], "data")
    assert "SKIP_SPACE_CHECK" in script
    assert "rm -f" in script

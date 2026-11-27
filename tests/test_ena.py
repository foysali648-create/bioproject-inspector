import pytest
from bioproject_inspector.ena import parse_filereport, ENAError

HEADER = "run_accession\tlibrary_layout\tread_count\tfastq_bytes\tfastq_md5\tfastq_ftp"
ROW = ("SRR1\tPAIRED\t1000\t10;20\taaa;bbb\t"
       "ftp.sra.ebi.ac.uk/a_1.fastq.gz;ftp.sra.ebi.ac.uk/a_2.fastq.gz")


def test_parse_paired():
    runs = parse_filereport(HEADER + "\n" + ROW + "\n")
    assert len(runs) == 1
    r = runs[0]
    assert r.library_layout == "PAIRED"
    assert r.read_count == 1000
    assert r.fastq_bytes == [10, 20]
    assert len(r.fastq_ftp) == 2


def test_truncated_response_raises():
    with pytest.raises(ENAError):
        parse_filereport(HEADER + "\nSRR1\tPAIRED\t10")

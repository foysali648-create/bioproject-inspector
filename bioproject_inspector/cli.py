import argparse

from bioproject_inspector.report import build_report


def main():
    p = argparse.ArgumentParser(
        description="Inspect an ENA/SRA BioProject (metadata only; nothing is downloaded)")
    p.add_argument("accession")
    p.add_argument("--out", help="also save the report to this file")
    a = p.parse_args()
    text = build_report(a.accession)
    print(text)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)


if __name__ == "__main__":
    main()

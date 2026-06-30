import argparse
import csv
import json
import sys
from pathlib import Path

DEFAULT_INPUT_FOLDER = Path(__file__).parent.parent / "data"
DEFAULT_CLASSIFICATION_FIELDS = ["geometry", "family"]


def flatten_classification(
    classification: dict
) -> dict[str, str]:
    """
    Flatten classification leaves for CSV export.

    :param classification: Preset classification dictionary
    :return: Flat dictionary of classification leaf values
    """
    morphology = classification.get("morphology", {})
    return {
        "geometry": classification.get("geometry", ""),
        "family": classification.get("family", ""),
        **morphology
    }


def get_csv_fields(
    rows: list[dict[str, str]]
) -> list[str]:
    """
    Build CSV fields from extracted rows, keeping stable classification fields first.

    :param rows: Extracted row dictionaries
    :return: CSV field names
    """
    fields = ["filename", *DEFAULT_CLASSIFICATION_FIELDS]

    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)

    return fields


def collect_rows(input_folder: Path) -> list[dict[str, str]]:
    """
    Extract classification fields from JSON preset files.

    :param input_folder: Folder containing JSON files
    :return: CSV row dictionaries
    """
    rows = []

    for file in sorted(input_folder.glob("*.json")):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        rows.append({"filename": file.stem, **flatten_classification(data.get("classification", {}))})

    return rows


def write_csv(rows: list[dict[str, str]], output_file: Path | None = None) -> None:
    """
    Write extracted rows as CSV.

    :param rows: CSV row dictionaries
    :param output_file: Optional output file path. Writes to stdout when omitted.
    """
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=get_csv_fields(rows), restval="")
            writer.writeheader()
            writer.writerows(rows)
        return

    writer = csv.DictWriter(sys.stdout, fieldnames=get_csv_fields(rows), restval="")
    writer.writeheader()
    writer.writerows(rows)


def main() -> None:
    """
    Entry point for the preset taxonomy CSV exporter.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT_FOLDER,
                        help="Input folder containing JSON preset files")
    parser.add_argument("-o", "--output", type=Path,
                        help="Output CSV file. Prints to stdout when omitted")
    args = parser.parse_args()

    rows = collect_rows(Path(args.input))
    write_csv(rows, args.output)


if __name__ == "__main__":
    main()

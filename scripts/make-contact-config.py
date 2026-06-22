import argparse
import json
from pathlib import Path
from datetime import datetime

DEFAULT_CONTACT_SHEET_IMAGE_NAME = "contact-sheet"
DEFAULT_INPUT_FOLDER = Path(__file__).parent.parent / "renders"
DEFAULT_OUTPUT_FILE = Path(__file__).parent.parent / "data" / "contact-sheet.config"


def print_message(
    message: str
) -> None:
    """
    Show a timestamped message

    :param message: Message text
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} : {message}")


def get_file_annotations(
    file: Path
) -> str:
    """
    
    """
    parts = file.stem.split("-")
    preset = "-".join(parts[:-2])
    name = " ".join(parts[:-2]).title()
    render_type = parts[-2].title()
    viewpoint = parts[-1].title()
    return preset, name, render_type, "Isometric" if viewpoint == "Iso" else viewpoint


def build_config(
    input_folder: Path | str,
    exclude_images: list
) -> dict:
    """
    Build a dictionary of images for the contact sheet
    
    :param input_folder: Folder containing the individual images
    :param page: Page number for the sheet
    :param rows: Number of rows in the sheet
    :param cols: Number of columns in the sheet
    :return: Dictionary of file details
    """
    print_message(f"Finding images in {input_folder}")

    # Get a list of image files that aren't in the exclusion list
    file_names = sorted(Path(input_folder).glob("*.png"))
    file_names = [
        f for f in file_names
        if not any(f.stem.startswith(prefix) for prefix in exclude_images)
    ]

    # Build the configuration dictionary
    config = {
        "folder": str(input_folder.relative_to(Path.cwd())),
        "files": []
    }

    # Add the files to the configuration dictionary
    for file in file_names:
        preset, shell_type, render_type, viewpoint = get_file_annotations(file)
        config["files"].append({
            "preset": preset,
            "filename": file.name,
            "shell_type": shell_type,
            "render_type": render_type,
            "viewpoint": viewpoint
        })

    print_message(f"Found {len(file_names)} images")
    return config


def write_config(path: Path, content: dict, indent: int = 2) -> None:
    """
    Write a dictionary to a JSON file

    :param path: Path to the file to save
    :param content: Configuration dictionary to save
    :param indent: JSON indentation level
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(content, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def main() -> None:
    """
    Entry point for the contact sheet generator
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT_FOLDER,
                        help="Input folder containing the images to add to the config")
    parser.add_argument("-e", "--exclude", nargs="+", type=str,
                        help="List of file names to exclude (without path and extension)")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_FILE, help="Output configuration file name")
    args = parser.parse_args()

    excluded_images = [DEFAULT_CONTACT_SHEET_IMAGE_NAME, *(args.exclude or [])]
    config = build_config(Path(args.input), excluded_images)
    write_config(Path(args.output), config)


if __name__ == "__main__":
    main()

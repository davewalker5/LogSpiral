import math
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

CAPTION_Y_OFFSET = 8

DEFAULT_CONFIG_FILE = Path(__file__).parent.parent / "data" / "contact-sheet.config"
DEFAULT_OUTPUT_FILE = Path(__file__).parent.parent / "renders" / "contact-sheet"
DEFAULT_ROWS = 0
DEFAULT_COLS = 6
DEFAULT_PAGE = 0


def print_message(message: str) -> None:
    """
    Show a timestamped message

    :param message: Message text
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} : {message}")


def print_error(message):
    """
    Show a timestamped error message

    :param message: Message text
    """
    print_message(f"ERROR: {message}")


def load_configuration(path: Path) -> dict:
    """
    Load a JSON file and return a dictionary of its contents

    :param path: Path to the file to load
    :return: Dictionary of JSON contents
    """
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def get_config_for_page(
    config: dict,
    page: int,
    rows: int,
    cols: int
) -> list[Path]:
    """
    Extract a page of images for a specified page of the contact sheet
    
    :param config: Configuration for all pages of the contact sheet
    :param page: Page number for the sheet
    :param rows: Number of rows in the sheet
    :param cols: Number of columns in the sheet
    :return: Dictionary of file details for the specified page
    """

    print_message(f"Extracting images for page {page}")
    print_message(f"Page size = {rows} x {cols}")

    if rows > 0 and cols > 0:
        offset = (page - 1) * rows * cols
        print_message(f"Page offset = {offset}")
        page_config = {
            "folder": config["folder"],
            "files": config["files"][offset:offset + rows * cols]
        }
    else:
        page_config = config

    print_message(f"Found {len(page_config["files"])} images")
    return page_config


def make_single_contact_sheet(
    config: dict,
    output_file: Path | str,
    rows: int,
    cols: int,
    image_width: int = 120,
    padding: int = 10,
    caption_spacing: int = 2,
    background: tuple = (25, 25, 25),
    missing_fill: tuple = (0, 0, 0),
    text: tuple = (255, 255, 255)
) -> None:
    """
    Create a single contact sheet for a list of PNG images
    
    :param files: List of the individual image files
    :param output_file: Output contact sheet file path, name and extension
    :param rows: Number of rows in the sheet
    :param cols: Number of columns in the sheet
    :param image_width: Width of individual images in the sheet
    :param padding: Padding around each image
    :param background: Background colour for the contact sheet
    :param missing_fill: Incomplete last row fill colour
    """
    images = []
    for file in config["files"]:
        # Get the caption
        print_message(f"Loading {file['filename']} : {file['shell_type']}, {file['render_type']}, {file['viewpoint']}")

        # Load the current image
        image_path = Path(config["folder"]) / file["filename"]
        img = Image.open(image_path).convert("RGBA")

        # Calculate the aspect ratio and resized height
        aspect = img.height / img.width
        new_height = int(image_width * aspect)

        # Resize the image and add it to the list
        img = img.resize((image_width, new_height), Image.LANCZOS)
        images.append(img)

    # Calculate the cell dimensions
    font = ImageFont.load_default()
    caption_height = 55

    image_cell_height = max(img.height for img in images)
    cell_width = image_width
    cell_height = image_cell_height + caption_height

    # Calculate the total grid dimensions
    grid_width = cols * cell_width + (cols + 1) * padding
    grid_height = rows * cell_height + (rows + 1) * padding

    # Create a canvas
    canvas = Image.new("RGBA", (grid_width, grid_height), background + (255,))

    total_cells = rows * cols
    for index in range(total_cells):
        # Calculate the current cell coordinates
        row = index // cols
        col = index % cols

        # Determine X and Y coordinates on the canvas, accounting for padding
        x = padding + col * (cell_width + padding)
        y = (row - 1) * padding +  row * cell_height

        if index < len(images):
            # We have an image at this index so draw it into the canvas
            img = images[index]
            y_img = y + (cell_height - img.height) // 2
            canvas.alpha_composite(img, (x, y_img))

            # Define the lines in the caption
            file = config["files"][index]
            caption_lines = [
                file["shell_type"],
                f"{file['render_type']} render",
                f"{file['viewpoint']} view"
            ]

            # Measure each line
            draw = ImageDraw.Draw(canvas)
            line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in caption_lines]
            line_widths = [bbox[2] - bbox[0] for bbox in line_bboxes]
            line_heights = [bbox[3] - bbox[1] for bbox in line_bboxes]

            # Calculate the total text block height
            total_text_height = (sum(line_heights) + caption_spacing * (len(caption_lines) - 1))

            # Position the whole text block within the caption area
            caption_top = y + image_cell_height
            block_y = caption_top + (caption_height - total_text_height) + CAPTION_Y_OFFSET

            # Draw each line centred
            current_y = block_y
            for line, width, height in zip(caption_lines, line_widths, line_heights):
                text_x = x + (cell_width - width) // 2
                draw.text(
                    (text_x, current_y),
                    line,
                    fill=text + (255,),
                    font=font,
                )
                current_y += height + caption_spacing
        else:
            # We have no image at this postion so draw an empty cell
            fill = missing_fill + (255,)
            rect = Image.new("RGBA", (cell_width, cell_height - caption_height), fill)
            y_img = y + (cell_height - img.height) // 2
            canvas.alpha_composite(rect, (x, y_img))

    # Save the canvas to the output file
    canvas.convert("RGB").save(output_file)


def make_contact_sheets(
    config: dict,
    output_file_name: str,
    page: int,
    rows: int,
    cols: int,
) -> None:
    """
    Create a set of contact sheets of given size for a list of images

    :param config: Contact sheet configuration 
    :param output_file: Output contact sheet file
    :param page: Page number to generate
    :param rows: Number of rows per sheet
    :param cols: Number of columns per sheet
    """
    if page > 0:
        start_page = end_page = page
    else:
        start_page = 1
        end_page = 1 if rows == 0 else math.ceil(len(config["files"]) / (rows * cols))

    print_message(f"Generating sheets for pages {start_page} to {end_page}")

    # If rows hasn't been specified, calculate the number of rows
    if rows == 0:
        rows = math.ceil(len(config["files"]) / cols)
        print_message(f"Calculated number of rows is {rows}")

    # Iterate over all pages
    for page in range(start_page, end_page + 1):
        # Extract the config for this page
        page_config = get_config_for_page(config, page, rows, cols)
        if not page_config["files"]:
            print_error(f"No images found for page {page}")

        output_file = f"{output_file_name}-{page:04d}.png"
        make_single_contact_sheet(page_config, output_file, rows, cols)


def main() -> None:
    """
    Entry point for the contact sheet generator
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-cfg", "--configuration", type=Path, default=DEFAULT_CONFIG_FILE,
                        help="Contact sheet configuration file")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_FILE, help="Output contact sheet path")
    parser.add_argument("-r", "--rows", type=int, default=DEFAULT_ROWS, help="Number of rows per page")
    parser.add_argument("-c", "--cols", type=int, default=DEFAULT_COLS, help="Number of columns per page")
    parser.add_argument("-p", "--page", type=int, default=DEFAULT_PAGE,
                        help="Page number to generate or 0 for all pages")
    args = parser.parse_args()

    config = load_configuration(args.configuration)
    make_contact_sheets(config, args.output, args.page, args.rows, args.cols)


if __name__ == "__main__":
    main()

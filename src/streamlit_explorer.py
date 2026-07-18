from __future__ import annotations

import os
import shutil
from pathlib import Path
from urllib.parse import urljoin

from morphospace_explorer import (
    DEFAULT_CLASSIFICATION_FILE,
    DEFAULT_MESH_FOLDER,
    write_explorer,
)


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_STATIC_FOLDER = Path(__file__).parent / "static"
DEFAULT_STATIC_MESH_FOLDER = DEFAULT_STATIC_FOLDER / "meshes"
DEFAULT_STATIC_EXPLORER = DEFAULT_STATIC_FOLDER / "morphospace-explorer.html"


def link_or_copy(source: Path, destination: Path) -> None:
    """Create a hard link when possible, falling back to a regular copy."""
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def mirror_meshes(
    source_folder: Path = DEFAULT_MESH_FOLDER,
    destination_folder: Path = DEFAULT_STATIC_MESH_FOLDER,
) -> None:
    """Mirror committed mesh assets into Streamlit's static file directory."""
    if not source_folder.is_dir():
        raise FileNotFoundError(f"Mesh folder not found: {source_folder}")

    destination_folder.mkdir(parents=True, exist_ok=True)
    source_files = {path.relative_to(source_folder): path for path in source_folder.rglob("*.json")}

    for relative_path, source in source_files.items():
        destination = destination_folder / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            source_stat = source.stat()
            destination_stat = destination.stat()
            if (
                source_stat.st_size == destination_stat.st_size
                and source_stat.st_mtime_ns == destination_stat.st_mtime_ns
            ):
                continue
            destination.unlink()

        link_or_copy(source, destination)

    for destination in destination_folder.rglob("*.json"):
        if destination.relative_to(destination_folder) not in source_files:
            destination.unlink()


def prepare_streamlit_explorer(
    classification_file: Path = DEFAULT_CLASSIFICATION_FILE,
    mesh_folder: Path = DEFAULT_MESH_FOLDER,
    static_folder: Path = DEFAULT_STATIC_FOLDER,
    mesh_url_prefix: str = "/app/static/meshes",
) -> Path:
    """Prepare the existing explorer and its meshes for Streamlit static serving."""
    static_mesh_folder = static_folder / "meshes"
    output_file = static_folder / "morphospace-explorer.html"

    mirror_meshes(mesh_folder, static_mesh_folder)
    write_explorer(
        classification_file=classification_file,
        mesh_folder=mesh_folder,
        output_file=output_file,
        mesh_url_prefix=mesh_url_prefix,
    )
    return output_file


def streamlit_mesh_url(app_url: str) -> str:
    """Build an absolute static mesh URL from Streamlit's browser-visible URL."""
    return urljoin(app_url.rstrip("/") + "/", "app/static/meshes")


def main() -> None:
    """Run the Morphospace Explorer inside Streamlit."""
    import streamlit as st

    st.set_page_config(page_title="Morphospace Explorer", layout="wide")

    try:
        explorer_file = prepare_streamlit_explorer(
            mesh_url_prefix=streamlit_mesh_url(st.context.url),
        )
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Unable to prepare the Morphospace Explorer: {exc}")
        st.stop()

    st.iframe(
        explorer_file,
        width="stretch",
        height=900,
    )


if __name__ == "__main__":
    main()

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from streamlit_explorer import mirror_meshes, prepare_streamlit_explorer, streamlit_mesh_url


class StreamlitExplorerTests(unittest.TestCase):
    def test_mirror_meshes_adds_updates_and_removes_json_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "data" / "meshes"
            destination = root / "static" / "meshes"
            source_shell = source / "ammonite" / "shell.json"
            source_shell.parent.mkdir(parents=True)
            source_shell.write_text('{"version": 1}', encoding="utf-8")

            mirror_meshes(source, destination)
            mirrored_shell = destination / "ammonite" / "shell.json"
            self.assertEqual(mirrored_shell.read_text(encoding="utf-8"), '{"version": 1}')

            source_shell.write_text('{"version": 2}', encoding="utf-8")
            stale_file = destination / "stale" / "shell.json"
            stale_file.parent.mkdir()
            stale_file.write_text("{}", encoding="utf-8")
            mirror_meshes(source, destination)

            self.assertEqual(mirrored_shell.read_text(encoding="utf-8"), '{"version": 2}')
            self.assertFalse(stale_file.exists())

    def test_prepare_streamlit_explorer_uses_static_mesh_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            classification = root / "classification.json"
            meshes = root / "data" / "meshes"
            static = root / "static"
            shell = meshes / "ammonite" / "shell.json"
            shell.parent.mkdir(parents=True)
            shell.write_text("{}", encoding="utf-8")
            classification.write_text(
                json.dumps([{"filename": "ammonite", "family": "ammonoid"}]),
                encoding="utf-8",
            )

            output = prepare_streamlit_explorer(classification, meshes, static)

            html = output.read_text(encoding="utf-8")
            self.assertIn("/app/static/meshes/ammonite/shell.json", html)
            self.assertTrue((static / "meshes" / "ammonite" / "shell.json").exists())

    def test_streamlit_mesh_url_uses_browser_visible_app_url(self):
        self.assertEqual(
            streamlit_mesh_url("https://logspiral.streamlit.app"),
            "https://logspiral.streamlit.app/app/static/meshes",
        )
        self.assertEqual(
            streamlit_mesh_url("http://localhost:8501/explorer"),
            "http://localhost:8501/explorer/app/static/meshes",
        )


if __name__ == "__main__":
    unittest.main()

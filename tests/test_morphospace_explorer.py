import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from morphospace_explorer import (
    append_query,
    build_records,
    classification_fields,
    current_asset_version,
    explorer_payload,
    filter_options,
    output_url_path,
    render_html,
)


class MorphospaceExplorerTests(unittest.TestCase):
    def test_classification_fields_follow_first_seen_order(self):
        rows = [
            {"filename": "ammonite", "family": "ammonoid", "geometry": "log-spiral"},
            {"filename": "orthocone", "axis": "straight", "family": "orthoceratoid"},
        ]

        fields = classification_fields(rows)

        self.assertEqual(fields, ["family", "geometry", "axis"])

    def test_records_include_available_optional_meshes(self):
        with tempfile.TemporaryDirectory() as tmp:
            mesh_folder = Path(tmp)
            shell_folder = mesh_folder / "ammonite"
            shell_folder.mkdir()
            for name in ["shell.json", "siphuncle.json"]:
                (shell_folder / name).write_text("{}", encoding="utf-8")

            records = build_records(
                [{"filename": "ammonite", "family": "ammonoid"}],
                ["family"],
                mesh_folder,
                "meshes",
            )

        self.assertEqual(records[0].meshes["shell"], "meshes/ammonite/shell.json")
        self.assertEqual(records[0].meshes["siphuncle"], "meshes/ammonite/siphuncle.json")
        self.assertNotIn("chamber-septa", records[0].meshes)

    def test_current_asset_version_uses_timestamp_format(self):
        self.assertRegex(current_asset_version(), r"^\d{14}$")

    def test_records_can_version_mesh_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            mesh_folder = Path(tmp)
            shell_folder = mesh_folder / "ammonite"
            shell_folder.mkdir()
            (shell_folder / "shell.json").write_text("{}", encoding="utf-8")

            records = build_records(
                [{"filename": "ammonite", "family": "ammonoid"}],
                ["family"],
                mesh_folder,
                "https://assets.example.test/meshes",
                "20260701",
            )

        self.assertEqual(
            records[0].meshes["shell"],
            "https://assets.example.test/meshes/ammonite/shell.json?v=20260701",
        )

    def test_append_query_preserves_existing_query_parameters(self):
        url = append_query("https://assets.example.test/meshes/shell.json?x=1", {"v": "20260701"})

        self.assertEqual(url, "https://assets.example.test/meshes/shell.json?x=1&v=20260701")

    def test_write_explorer_versions_mesh_urls_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            classification_file = tmp_path / "classification.json"
            mesh_folder = tmp_path / "meshes"
            output_file = tmp_path / "explorer.html"
            shell_folder = mesh_folder / "ammonite"
            shell_folder.mkdir(parents=True)
            classification_file.write_text(
                json.dumps([{"filename": "ammonite", "family": "ammonoid"}]),
                encoding="utf-8",
            )
            (shell_folder / "shell.json").write_text("{}", encoding="utf-8")

            from morphospace_explorer import write_explorer

            write_explorer(
                classification_file=classification_file,
                mesh_folder=mesh_folder,
                output_file=output_file,
                mesh_url_prefix="https://assets.example.test/meshes",
            )

            html = output_file.read_text(encoding="utf-8")

        self.assertRegex(
            html,
            r"https://assets[.]example[.]test/meshes/ammonite/shell[.]json[?]v=\d{14}",
        )

    def test_filter_options_exclude_missing_values(self):
        records = [
            type("Record", (), {"classification": {"family": "ammonoid"}})(),
            type("Record", (), {"classification": {"family": "gastropod", "axis": "curved"}})(),
        ]

        options = filter_options(records, ["family", "axis"])

        self.assertEqual(options["family"], ["ammonoid", "gastropod"])
        self.assertEqual(options["axis"], ["curved"])

    def test_render_html_embeds_payload_without_mesh_data(self):
        payload = explorer_payload([], ["family"])
        html = render_html(payload)

        self.assertIn("const explorer = ", html)
        self.assertIn("color-scheme: dark", html)
        self.assertIn("--panel: #11161d", html)
        self.assertIn("--control: #0b0f15", html)
        self.assertIn("background: var(--panel-raised)", html)
        self.assertIn("grid-template-columns: minmax(240px, 300px) minmax(240px, 320px) minmax(0, 1fr)", html)
        self.assertIn("height: 100vh", html)
        self.assertIn('class="panel filter-panel"', html)
        self.assertIn('class="panel results-panel"', html)
        self.assertNotIn("<header>", html)
        self.assertNotIn("<h1>Morphospace Explorer</h1>", html)
        self.assertIn('window.location.protocol === "http:"', html)
        self.assertIn("window.location.replace", html)
        self.assertIn('"127.0.0.1"', html)
        self.assertIn("Local file mode cannot load mesh JSON", html)
        self.assertIn("Morphospace Explorer failed while", html)
        self.assertIn("await Plotly.react", html)
        self.assertIn('paper_bgcolor: "#000000"', html)
        self.assertIn("const YL_OR_BR_COLORSCALE = [", html)
        self.assertIn('trace.colorscale = YL_OR_BR_COLORSCALE', html)
        self.assertIn('trace.intensitymode = "vertex"', html)
        self.assertIn("--siphuncle: rgb(180,120,80)", html)
        self.assertNotIn('colorscale = "YlOrBr"', html)
        self.assertNotIn("--shell: rgb", html)
        self.assertNotIn('getPropertyValue("--shell")', html)
        self.assertNotIn("__EXPLORER_PAYLOAD__", html)
        embedded = html.split("const explorer = ", 1)[1].split(";", 1)[0]
        self.assertEqual(json.loads(embedded), payload)

    def test_output_url_path_is_project_relative(self):
        output_file = Path(__file__).parent.parent / "docs" / "morphospace-explorer.html"

        self.assertEqual(output_url_path(output_file), "/docs/morphospace-explorer.html")


if __name__ == "__main__":
    unittest.main()

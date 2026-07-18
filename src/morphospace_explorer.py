from __future__ import annotations

import argparse
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CLASSIFICATION_FILE = PROJECT_ROOT / "data" / "similarity" / "shell-classification.json"
DEFAULT_MESH_FOLDER = PROJECT_ROOT / "data" / "meshes"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "data" / "morphospace-explorer.html"
def current_asset_version() -> str:
    """
    Build a timestamp suitable for mesh asset cache busting.

    :return: Current timestamp as YYYYMMDDHHMMSS
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")


DEFAULT_ASSET_VERSION = current_asset_version()
MESH_PARTS = ("shell", "chamber-septa", "siphuncle")


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    """
    Static file handler that keeps local explorer serving output concise.
    """

    def handle(self) -> None:
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            return

    def log_message(self, format: str, *args: Any) -> None:
        return


@dataclass(frozen=True)
class ShellRecord:
    """
    Classification metadata and available mesh files for one shell.
    """

    filename: str
    classification: dict[str, str]
    meshes: dict[str, str]


def load_classification(classification_file: Path) -> list[dict[str, Any]]:
    """
    Load shell classification rows from JSON.

    :param classification_file: Path to shell-classification.json
    :return: Classification rows
    """
    with classification_file.open("r", encoding="utf-8") as f:
        rows = json.load(f)

    if not isinstance(rows, list):
        raise ValueError("Classification JSON must contain a list of shell records.")

    for row in rows:
        if not isinstance(row, dict) or not row.get("filename"):
            raise ValueError("Each classification row must be an object with a filename field.")

    return rows


def classification_fields(rows: list[dict[str, Any]]) -> list[str]:
    """
    Determine data-driven filter fields in stable first-seen order.

    :param rows: Classification rows
    :return: Field names excluding filename
    """
    fields = []
    for row in rows:
        for field in row:
            if field != "filename" and field not in fields:
                fields.append(field)
    return fields


def append_query(url: str, params: dict[str, str]) -> str:
    """
    Append query parameters to a URL or URL path.

    :param url: Base URL or path
    :param params: Query parameters to append
    :return: URL with query parameters
    """
    if not params:
        return url

    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urlencode(params)}"


def mesh_manifest(
    filename: str,
    mesh_folder: Path,
    mesh_url_prefix: str,
    mesh_asset_version: str | None = None,
) -> dict[str, str]:
    """
    Build URL mappings for the mesh files available for one shell.

    :param filename: Shell filename identifier
    :param mesh_folder: Local mesh folder used to check available files
    :param mesh_url_prefix: URL/path prefix to use inside generated HTML
    :return: Mesh part names mapped to URLs
    """
    meshes = {}
    for part in MESH_PARTS:
        mesh_file = mesh_folder / filename / f"{part}.json"
        if mesh_file.exists():
            mesh_url = f"{mesh_url_prefix.rstrip('/')}/{filename}/{part}.json"
            meshes[part] = append_query(
                mesh_url,
                {"v": mesh_asset_version} if mesh_asset_version else {},
            )

    if "shell" not in meshes:
        raise FileNotFoundError(f"Missing required shell mesh: {mesh_folder / filename / 'shell.json'}")

    return meshes


def build_records(
    rows: list[dict[str, Any]],
    fields: list[str],
    mesh_folder: Path,
    mesh_url_prefix: str,
    mesh_asset_version: str | None = None,
) -> list[ShellRecord]:
    """
    Combine classification metadata with a mesh availability manifest.

    :param rows: Classification rows
    :param fields: Classification fields
    :param mesh_folder: Local mesh folder
    :param mesh_url_prefix: Mesh URL/path prefix for generated HTML
    :return: Shell records
    """
    records = []
    for row in rows:
        filename = str(row["filename"])
        records.append(
            ShellRecord(
                filename=filename,
                classification={
                    field: str(row[field])
                    for field in fields
                    if row.get(field) not in ("", None)
                },
                meshes=mesh_manifest(
                    filename,
                    mesh_folder,
                    mesh_url_prefix,
                    mesh_asset_version,
                ),
            )
        )
    return records


def filter_options(records: list[ShellRecord], fields: list[str]) -> dict[str, list[str]]:
    """
    Build unique filter values for every classification field.

    :param records: Shell records
    :param fields: Classification fields
    :return: Field names mapped to sorted unique values
    """
    options = {}
    for field in fields:
        values = {
            record.classification[field]
            for record in records
            if field in record.classification
        }
        options[field] = sorted(values, key=lambda value: value.casefold())
    return options


def format_label(value: str) -> str:
    """
    Convert machine-oriented identifiers into compact display text.

    :param value: Raw field or shell identifier
    :return: Human-readable label
    """
    return value.replace("_", " ").replace("-", " ").title()


def explorer_payload(records: list[ShellRecord], fields: list[str]) -> dict[str, Any]:
    """
    Build the data payload embedded in the generated explorer.

    :param records: Shell records
    :param fields: Classification fields
    :return: JSON-serialisable explorer payload
    """
    return {
        "fields": fields,
        "fieldLabels": {field: format_label(field) for field in fields},
        "filterOptions": filter_options(records, fields),
        "shells": [
            {
                "filename": record.filename,
                "name": format_label(record.filename),
                "classification": record.classification,
                "meshes": record.meshes,
            }
            for record in records
        ],
    }


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Morphospace Explorer</title>
  <script>
    (() => {
      if (window.parent !== window) {
        window.parent.postMessage({
          isStreamlitMessage: true,
          type: "streamlit:componentReady",
          apiVersion: 1,
        }, "*");
        window.parent.postMessage({
          isStreamlitMessage: true,
          type: "streamlit:setFrameHeight",
          height: 900,
        }, "*");
      }

      const localHosts = new Set(["localhost", "127.0.0.1", "::1", "[::1]"]);
      if (window.location.protocol === "http:" && !localHosts.has(window.location.hostname)) {
        window.location.replace(`https:${window.location.href.slice(window.location.protocol.length)}`);
      }
    })();
  </script>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      color-scheme: dark;
      --bg: #07090d;
      --panel: #11161d;
      --panel-raised: #171d26;
      --control: #0b0f15;
      --text: #f2f5f8;
      --muted: #99a4b2;
      --line: #2a3340;
      --accent: #f59e0b;
      --accent-dark: #b45309;
      --siphuncle: rgb(180,120,80);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.4;
    }

    main {
      display: grid;
      grid-template-columns: minmax(240px, 300px) minmax(240px, 320px) minmax(0, 1fr);
      height: 100vh;
      min-height: 0;
    }

    .panel {
      border-right: 1px solid var(--line);
      background: var(--panel);
      padding: 18px;
      overflow: auto;
    }

    .viewer {
      display: grid;
      grid-template-rows: auto minmax(420px, 1fr);
      min-width: 0;
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px clamp(16px, 3vw, 32px);
      border-bottom: 1px solid var(--line);
      background: var(--panel-raised);
    }

    .toolbar h2 {
      margin: 0;
      font-size: 1.05rem;
      letter-spacing: 0;
    }

    .filters {
      display: grid;
      gap: 12px;
    }

    .panel-title {
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0;
      margin: 0 0 12px;
      text-transform: uppercase;
    }

    label {
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--control);
      color: var(--text);
      padding: 8px 10px;
      font-size: 0.95rem;
    }

    .shell-count {
      color: var(--muted);
      font-size: 0.9rem;
      margin: 0 0 10px;
    }

    .shell-list {
      display: grid;
      gap: 8px;
    }

    .shell-button {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--control);
      color: var(--text);
      cursor: pointer;
      padding: 10px;
      text-align: left;
    }

    .shell-button:hover,
    .shell-button:focus {
      border-color: var(--accent);
      background: #141b24;
      outline: none;
    }

    .shell-button.active {
      border-color: var(--accent);
      box-shadow: inset 3px 0 0 var(--accent);
      background: #171d26;
    }

    .shell-button strong {
      display: block;
      font-size: 0.98rem;
      margin-bottom: 4px;
    }

    .shell-button span {
      color: var(--muted);
      display: block;
      font-size: 0.82rem;
    }

    .toggle {
      align-items: center;
      color: var(--text);
      display: flex;
      font-size: 0.9rem;
      font-weight: 600;
      gap: 8px;
      text-transform: none;
    }

    .toggle input {
      accent-color: var(--accent);
      height: 18px;
      width: 18px;
    }

    #plot {
      background: #000000;
      min-height: 420px;
      height: 100%;
      width: 100%;
    }

    .empty-state,
    .loading-state,
    .error-state {
      align-items: center;
      color: var(--muted);
      display: flex;
      min-height: 420px;
      justify-content: center;
      padding: 24px;
      text-align: center;
    }

    .error-state {
      color: #fda4af;
    }

    @media (max-width: 860px) {
      main {
        grid-template-columns: 1fr;
      }

      .panel {
        border-right: 0;
        border-bottom: 1px solid var(--line);
        max-height: 36vh;
      }

      .toolbar {
        align-items: flex-start;
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <main>
    <aside class="panel filter-panel">
      <h2 class="panel-title">Filters</h2>
      <form class="filters" id="filters"></form>
    </aside>
    <aside class="panel results-panel">
      <h2 class="panel-title">Results</h2>
      <p class="shell-count" id="shell-count"></p>
      <div class="shell-list" id="shell-list"></div>
    </aside>
    <section class="viewer">
      <div class="toolbar">
        <h2 id="selected-shell">Select a shell</h2>
        <label class="toggle">
          <input type="checkbox" id="transparent-shell">
          Semi-transparent shell
        </label>
      </div>
      <div id="plot" class="empty-state">Choose a shell to load its geometry.</div>
    </section>
  </main>

  <script>
    const explorer = __EXPLORER_PAYLOAD__;
    const state = {
      filters: {},
      selected: null,
      traces: [],
    };

    const filtersElement = document.getElementById("filters");
    const shellListElement = document.getElementById("shell-list");
    const shellCountElement = document.getElementById("shell-count");
    const plotElement = document.getElementById("plot");
    const selectedShellElement = document.getElementById("selected-shell");
    const transparentShellElement = document.getElementById("transparent-shell");
    const YL_OR_BR_COLORSCALE = [
      [0.0, "rgb(255,255,229)"],
      [0.125, "rgb(255,247,188)"],
      [0.25, "rgb(254,227,145)"],
      [0.375, "rgb(254,196,79)"],
      [0.5, "rgb(254,153,41)"],
      [0.625, "rgb(236,112,20)"],
      [0.75, "rgb(204,76,2)"],
      [0.875, "rgb(153,52,4)"],
      [1.0, "rgb(102,37,6)"],
    ];

    function valueLabel(value) {
      return String(value).replaceAll("_", " ").replaceAll("-", " ").replace(/\b\w/g, match => match.toUpperCase());
    }

    function renderFilters() {
      filtersElement.innerHTML = "";
      for (const field of explorer.fields) {
        const label = document.createElement("label");
        label.textContent = explorer.fieldLabels[field];

        const select = document.createElement("select");
        select.dataset.field = field;

        const allOption = document.createElement("option");
        allOption.value = "";
        allOption.textContent = "All";
        select.appendChild(allOption);

        for (const value of explorer.filterOptions[field]) {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = valueLabel(value);
          select.appendChild(option);
        }

        select.addEventListener("change", event => {
          const selectedValue = event.target.value;
          if (selectedValue) {
            state.filters[field] = selectedValue;
          } else {
            delete state.filters[field];
          }
          renderShellList();
        });

        label.appendChild(select);
        filtersElement.appendChild(label);
      }
    }

    function matchingShells() {
      return explorer.shells.filter(shell => {
        for (const [field, value] of Object.entries(state.filters)) {
          if (shell.classification[field] !== value) {
            return false;
          }
        }
        return true;
      });
    }

    function renderShellList() {
      const shells = matchingShells();
      shellListElement.innerHTML = "";
      shellCountElement.textContent = `${shells.length} shell${shells.length === 1 ? "" : "s"}`;

      for (const shell of shells) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `shell-button${state.selected?.filename === shell.filename ? " active" : ""}`;
        button.innerHTML = `<strong>${shell.name}</strong><span>${metadataSummary(shell)}</span>`;
        button.addEventListener("click", () => selectShell(shell));
        shellListElement.appendChild(button);
      }
    }

    function metadataSummary(shell) {
      return explorer.fields
        .filter(field => shell.classification[field])
        .slice(0, 3)
        .map(field => valueLabel(shell.classification[field]))
        .join(" · ");
    }

    async function selectShell(shell) {
      state.selected = shell;
      state.traces = [];
      renderShellList();
      selectedShellElement.textContent = shell.name;
      plotElement.className = "loading-state";
      plotElement.textContent = "Loading geometry...";

      try {
        const traces = [];
        traces.push(makeTrace("shell", await loadMesh(shell.meshes.shell), shell));

        if (shell.meshes["chamber-septa"]) {
          traces.push(makeTrace("chamber-septa", await loadMesh(shell.meshes["chamber-septa"]), shell));
        }

        if (shell.meshes.siphuncle) {
          traces.push(makeTrace("siphuncle", await loadMesh(shell.meshes.siphuncle), shell));
        }

        state.traces = traces;
        renderPlot();
      } catch (error) {
        plotElement.className = "error-state";
        plotElement.textContent = `Unable to load geometry for ${shell.name}: ${error.message}`;
      }
    }

    async function loadMesh(url) {
      if (window.location.protocol === "file:") {
        throw new Error("Local file mode cannot load mesh JSON. Run python src/morphospace_explorer.py --serve and open the local http:// address it prints.");
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`${url} returned ${response.status}`);
      }
      return response.json();
    }

    function makeTrace(part, mesh, shell) {
      const isShell = part === "shell";
      const name = {
        "shell": "Shell",
        "chamber-septa": "Chamber septa",
        "siphuncle": "Siphuncle",
      }[part];

      const trace = {
        type: "mesh3d",
        name,
        x: mesh.vertices.x,
        y: mesh.vertices.y,
        z: mesh.vertices.z,
        i: mesh.faces.i,
        j: mesh.faces.j,
        k: mesh.faces.k,
        flatshading: false,
        hoverinfo: "skip",
      };

      if (isShell) {
        trace.opacity = transparentShellElement.checked ? 0.35 : 1.0;
        if (mesh.intensity) {
          trace.intensity = mesh.intensity;
          trace.intensitymode = "vertex";
          trace.colorscale = YL_OR_BR_COLORSCALE;
          trace.showscale = false;
        }
        trace.lighting = {
          ambient: 0.35,
          diffuse: 0.95,
          specular: 1.2,
          roughness: 0.12,
          fresnel: 0.5,
        };
      } else if (part === "chamber-septa") {
        trace.opacity = 0.72;
        if (mesh.intensity) {
          trace.intensity = mesh.intensity;
          trace.intensitymode = "vertex";
          trace.colorscale = YL_OR_BR_COLORSCALE;
          trace.showscale = false;
        }
      } else {
        trace.color = getComputedStyle(document.documentElement).getPropertyValue("--siphuncle").trim();
        trace.opacity = 0.95;
      }

      return trace;
    }

    function renderPlot() {
      if (!state.selected || state.traces.length === 0) {
        return;
      }

      state.traces = state.traces.map(trace => {
        if (trace.name === "Shell") {
          return {...trace, opacity: transparentShellElement.checked ? 0.35 : 1.0};
        }
        return trace;
      });

      plotElement.className = "";
      plotElement.textContent = "";

      Plotly.react(plotElement, state.traces, {
        margin: {l: 0, r: 0, t: 0, b: 0},
        paper_bgcolor: "#000000",
        plot_bgcolor: "#000000",
        showlegend: true,
        legend: {
          x: 0.02,
          y: 0.98,
          bgcolor: "rgba(0,0,0,0.68)",
          font: {color: "#f8fafc"},
        },
        scene: {
          aspectmode: "data",
          bgcolor: "rgba(0,0,0,0)",
          xaxis: {visible: false},
          yaxis: {visible: false},
          zaxis: {visible: false},
          camera: {eye: {x: 1.6, y: 1.7, z: 1.1}},
        },
      }, {responsive: true, displaylogo: false});
    }

    transparentShellElement.addEventListener("change", renderPlot);

    renderFilters();
    renderShellList();
  </script>
</body>
</html>
"""


def render_html(payload: dict[str, Any]) -> str:
    """
    Render the standalone explorer HTML.

    :param payload: Explorer data payload
    :return: HTML document
    """
    return HTML_TEMPLATE.replace(
        "__EXPLORER_PAYLOAD__",
        json.dumps(payload, ensure_ascii=False),
    )


def write_explorer(
    classification_file: Path = DEFAULT_CLASSIFICATION_FILE,
    mesh_folder: Path = DEFAULT_MESH_FOLDER,
    output_file: Path = DEFAULT_OUTPUT_FILE,
    mesh_url_prefix: str | None = None,
    mesh_asset_version: str | None = DEFAULT_ASSET_VERSION,
) -> None:
    """
    Write a static Morphospace Explorer HTML file.

    :param classification_file: Input classification JSON
    :param mesh_folder: Local mesh folder
    :param output_file: Output HTML file
    :param mesh_url_prefix: Optional mesh URL/path prefix for HTML fetches
    :param mesh_asset_version: Version appended to mesh URLs as a query string
    """
    if mesh_url_prefix is None:
        mesh_url_prefix = str(Path("../data/meshes"))

    rows = load_classification(classification_file)
    fields = classification_fields(rows)
    records = build_records(rows, fields, mesh_folder, mesh_url_prefix, mesh_asset_version)
    html = render_html(explorer_payload(records, fields))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html, encoding="utf-8")


def output_url_path(output_file: Path, serve_root: Path = PROJECT_ROOT) -> str:
    """
    Build the HTTP path for an output file served from the project root.

    :param output_file: Generated HTML output file
    :param serve_root: Directory served by the local HTTP server
    :return: URL path to the generated HTML file
    """
    try:
        relative_path = output_file.resolve().relative_to(serve_root.resolve())
    except ValueError as exc:
        raise ValueError(
            f"Cannot serve {output_file} from {serve_root}. "
            "Use an output path inside the project folder."
        ) from exc

    return "/" + relative_path.as_posix()


def serve_explorer(output_file: Path, host: str, port: int) -> None:
    """
    Serve the project folder so the explorer can fetch mesh JSON over HTTP.

    :param output_file: Generated explorer HTML file
    :param host: HTTP server host
    :param port: HTTP server port
    """
    handler = partial(QuietHTTPRequestHandler, directory=str(PROJECT_ROOT))
    url_path = output_url_path(output_file)

    with ThreadingHTTPServer((host, port), handler) as server:
        actual_host, actual_port = server.server_address[:2]
        print(f"Morphospace Explorer: http://{actual_host}:{actual_port}{url_path}", flush=True)
        print("Keep this process running while using the explorer.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nMorphospace Explorer server stopped.", flush=True)


def main() -> None:
    """
    Entry point for the Morphospace Explorer generator.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--classification", type=Path, default=DEFAULT_CLASSIFICATION_FILE,
                        help="Input shell classification JSON file")
    parser.add_argument("-m", "--meshes", type=Path, default=DEFAULT_MESH_FOLDER, 
                        help="Input folder containing precomputed shell mesh folders")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT_FILE,
                        help="Output HTML file")
    parser.add_argument("-pr", "--mesh-url-prefix",
                        help="URL/path prefix used by the generated page to fetch mesh JSON files")
    parser.add_argument("-mv", "--mesh-asset-version", default=DEFAULT_ASSET_VERSION,
                        help="Version appended to mesh URLs, defaulting to the current date and timestamp")
    parser.add_argument("-s", "--serve", action="store_true",
                        help="Start a local HTTP server after writing the explorer HTML")
    parser.add_argument("-ho", "--host", default="127.0.0.1", help="Host for --serve")
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Port for --serve; use 0 to choose an available port")
    args = parser.parse_args()

    write_explorer(
        classification_file=args.classification,
        mesh_folder=args.meshes,
        output_file=args.output,
        mesh_url_prefix=args.mesh_url_prefix,
        mesh_asset_version=args.mesh_asset_version,
    )

    if args.serve:
        serve_explorer(args.output, args.host, args.port)


if __name__ == "__main__":
    main()

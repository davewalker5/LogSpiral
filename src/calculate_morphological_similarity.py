import argparse
import csv
import json
import sys
from pathlib import Path

from morphological_similarity import (
    DEFAULT_INPUT_FOLDER,
    DEFAULT_WEIGHTS_FILE,
    build_comparison_matrix,
    compare_presets,
    display_names,
    iter_pairwise_comparisons,
    load_presets,
    load_weights,
    nearest_neighbours,
    render_markdown_report,
)


def configure_matplotlib():
    """
    Configure Matplotlib for non-interactive file output.

    :return: Matplotlib pyplot module
    """
    import os
    import tempfile

    matplotlib_config_dir = Path(tempfile.gettempdir()) / "logspiral-matplotlib-cache"
    matplotlib_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_config_dir))

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def write_pairwise_csv(presets, weights, output_file: Path) -> None:
    """
    Write one CSV row for each unique shell-preset pair.

    :param presets: Shell presets to compare
    :param weights: Classification field weighting table
    :param output_file: CSV file to write
    """
    names = display_names(presets)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "left",
                "right",
                "similarity",
                "matched_weight",
                "compared_weight",
                "matching_characteristics",
                "differing_characteristics",
            ],
        )
        writer.writeheader()
        for comparison in iter_pairwise_comparisons(presets, weights):
            writer.writerow(
                {
                    "left": names[comparison.left.filename],
                    "right": names[comparison.right.filename],
                    "similarity": f"{comparison.score:.6f}",
                    "matched_weight": f"{comparison.matched_weight:g}",
                    "compared_weight": f"{comparison.compared_weight:g}",
                    "matching_characteristics": "; ".join(
                        field.field for field in comparison.matching_fields
                    ),
                    "differing_characteristics": "; ".join(
                        field.field for field in comparison.differing_fields
                    ),
                }
            )


def write_matrix_csv(presets, weights, output_file: Path) -> None:
    """
    Write the all-against-all similarity matrix as CSV in dendrogram order.

    :param presets: Shell presets to compare
    :param weights: Classification field weighting table
    :param output_file: CSV file to write
    """
    presets = order_presets_by_dendrogram(presets, weights)
    matrix = build_comparison_matrix(presets, weights)
    names = display_names(presets)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["shell", *(names[preset.filename] for preset in presets)])
        for left in presets:
            writer.writerow(
                [
                    names[left.filename],
                    *(
                        f"{matrix[(left.filename, right.filename)].percentage:.1f}"
                        for right in presets
                    ),
                ]
            )


def write_matrix_plot_png(presets, weights, output_file: Path) -> None:
    """
    Write the all-against-all similarity matrix as an annotated PNG plot in dendrogram order.

    :param presets: Shell presets to compare
    :param weights: Classification field weighting table
    :param output_file: PNG file to write
    """
    plt = configure_matplotlib()
    presets = order_presets_by_dendrogram(presets, weights)
    matrix = build_comparison_matrix(presets, weights)
    names = display_names(presets)
    labels = [names[preset.filename] for preset in presets]
    values = [
        [
            matrix[(left.filename, right.filename)].percentage
            for right in presets
        ]
        for left in presets
    ]

    size = max(8.0, min(18.0, len(presets) * 0.9))
    fig, ax = plt.subplots(figsize=(size, size), constrained_layout=True)
    image = ax.imshow(values, cmap="YlOrRd", vmin=0.0, vmax=100.0)

    ax.set_title("Morphological Similarity Matrix")
    ax.set_xticks(range(len(labels)), labels=labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)), labels=labels)
    ax.set_xticks([index - 0.5 for index in range(1, len(labels))], minor=True)
    ax.set_yticks([index - 0.5 for index in range(1, len(labels))], minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)

    for row_index, row in enumerate(values):
        for column_index, value in enumerate(row):
            text_colour = "white" if value >= 65.0 else "black"
            ax.text(
                column_index,
                row_index,
                f"{value:.0f}%",
                ha="center",
                va="center",
                color=text_colour,
                fontsize=8,
            )

    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Similarity (%)")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file, dpi=200)
    plt.close(fig)


def average_cluster_distance(left: dict, right: dict, distances: dict[tuple[int, int], float]) -> float:
    """
    Calculate average pairwise distance between two clusters.

    :param left: First cluster node
    :param right: Second cluster node
    :param distances: Original item distances keyed by item index pair
    :return: Average distance between cluster members
    """
    values = [
        distances[tuple(sorted((left_index, right_index)))]
        for left_index in left["members"]
        for right_index in right["members"]
    ]
    return sum(values) / len(values)


def build_similarity_dendrogram(presets, weights) -> dict:
    """
    Build an average-linkage dendrogram tree from similarity scores.

    :param presets: Shell presets to cluster
    :param weights: Classification field weighting table
    :return: Root dendrogram node
    """
    if len(presets) < 2:
        raise ValueError("At least two presets are required to build a dendrogram.")

    matrix = build_comparison_matrix(presets, weights)
    distances = {}
    for left_index, left in enumerate(presets):
        for right_index, right in enumerate(presets):
            if left_index < right_index:
                similarity = matrix[(left.filename, right.filename)].percentage
                distances[(left_index, right_index)] = 100.0 - similarity

    clusters = [
        {
            "members": [index],
            "height": 0.0,
            "left": None,
            "right": None,
            "label": preset.filename,
        }
        for index, preset in enumerate(presets)
    ]

    while len(clusters) > 1:
        best_pair = None
        best_distance = None
        for left_index, left in enumerate(clusters):
            for right_index, right in enumerate(clusters[left_index + 1:], start=left_index + 1):
                distance = average_cluster_distance(left, right, distances)
                member_key = (
                    min(left["members"]),
                    min(right["members"]),
                    len(left["members"]) + len(right["members"]),
                )
                candidate = (distance, member_key)
                if best_distance is None or candidate < best_distance:
                    best_distance = candidate
                    best_pair = (left_index, right_index, distance)

        left_index, right_index, distance = best_pair
        left = clusters[left_index]
        right = clusters[right_index]
        merged = {
            "members": sorted([*left["members"], *right["members"]]),
            "height": distance,
            "left": left,
            "right": right,
            "label": None,
        }

        clusters = [
            cluster
            for index, cluster in enumerate(clusters)
            if index not in (left_index, right_index)
        ]
        clusters.append(merged)

    return clusters[0]


def assign_dendrogram_positions(node: dict, positions: dict[int, float], next_position: list[int]) -> float:
    """
    Assign axis positions to dendrogram leaves and internal nodes.

    :param node: Dendrogram node to position
    :param positions: Leaf positions keyed by preset index
    :param next_position: Mutable next leaf position counter
    :return: Axis position for the node
    """
    if node["left"] is None and node["right"] is None:
        index = node["members"][0]
        position = float(next_position[0])
        next_position[0] += 1
        positions[index] = position
        node["x"] = position
        return position

    left_x = assign_dendrogram_positions(node["left"], positions, next_position)
    right_x = assign_dendrogram_positions(node["right"], positions, next_position)
    node["x"] = (left_x + right_x) / 2.0
    return node["x"]


def dendrogram_leaf_order(presets, weights) -> list[int]:
    """
    Get preset indexes in dendrogram leaf order.

    :param presets: Shell presets to cluster
    :param weights: Classification field weighting table
    :return: Preset indexes ordered by dendrogram leaf position
    """
    if len(presets) < 2:
        return list(range(len(presets)))

    root = build_similarity_dendrogram(presets, weights)
    positions = {}
    assign_dendrogram_positions(root, positions, [0])
    return sorted(positions, key=lambda index: positions[index])


def order_presets_by_dendrogram(presets, weights):
    """
    Sort shell presets by dendrogram leaf order.

    :param presets: Shell presets to order
    :param weights: Classification field weighting table
    :return: Shell presets ordered by clustering position
    """
    return [presets[index] for index in dendrogram_leaf_order(presets, weights)]


def draw_dendrogram_node(ax, node: dict) -> None:
    """
    Draw one dendrogram node and its children.

    :param ax: Matplotlib axes to draw on
    :param node: Dendrogram node to draw
    """
    if node["left"] is None and node["right"] is None:
        return

    left = node["left"]
    right = node["right"]
    x = 100.0 - node["height"]
    left_x = 100.0 - left["height"]
    right_x = 100.0 - right["height"]
    ax.plot([x, left_x], [left["x"], left["x"]], color="#9c2f1a", linewidth=1.8)
    ax.plot([x, right_x], [right["x"], right["x"]], color="#9c2f1a", linewidth=1.8)
    ax.plot([x, x], [left["x"], right["x"]], color="#9c2f1a", linewidth=1.8)
    draw_dendrogram_node(ax, left)
    draw_dendrogram_node(ax, right)


def draw_dendrogram_leaf_extensions(ax, y_positions: list[float]) -> None:
    """
    Draw terminal branches from each leaf node to the label edge.

    :param ax: Matplotlib axes to draw on
    :param y_positions: Y-axis positions for dendrogram leaves
    """
    for y_position in y_positions:
        ax.plot([100.0, 102.0], [y_position, y_position], color="#9c2f1a", linewidth=1.8)


def write_dendrogram_png(presets, weights, output_file: Path) -> None:
    """
    Write a similarity dendrogram as a PNG image.

    :param presets: Shell presets to cluster
    :param weights: Classification field weighting table
    :param output_file: PNG file to write
    """
    plt = configure_matplotlib()
    names = display_names(presets)
    root = build_similarity_dendrogram(presets, weights)
    positions = {}
    assign_dendrogram_positions(root, positions, [0])

    ordered_indices = sorted(positions, key=lambda index: positions[index])
    labels = [names[presets[index].filename] for index in ordered_indices]
    y_positions = [positions[index] for index in ordered_indices]

    height = max(8.0, min(18.0, len(presets) * 0.55))
    fig, ax = plt.subplots(figsize=(12.0, height), constrained_layout=True)
    draw_dendrogram_node(ax, root)
    draw_dendrogram_leaf_extensions(ax, y_positions)
    ax.set_title("Morphological Similarity Dendrogram")
    ax.set_xlabel("Merge similarity (%)")
    ax.set_xlim(left=0.0, right=102.0)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_yticks(y_positions, labels=labels)
    ax.yaxis.tick_right()
    ax.tick_params(axis="y", labelright=True, labelleft=False)
    ax.grid(axis="x", color="#dddddd", linestyle="-", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file, dpi=200)
    plt.close(fig)


def write_nearest_csv(presets, weights, output_file: Path) -> None:
    """
    Write closest and most distinct neighbours for each shell preset.

    :param presets: Shell presets to compare
    :param weights: Classification field weighting table
    :param output_file: CSV file to write
    """
    matrix = build_comparison_matrix(presets, weights)
    names = display_names(presets)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "shell",
                "closest_shell",
                "closest_similarity",
                "most_distinct_shell",
                "most_distinct_similarity",
            ],
        )
        writer.writeheader()
        for preset in presets:
            closest, most_distinct = nearest_neighbours(preset, matrix)
            writer.writerow(
                {
                    "shell": names[preset.filename],
                    "closest_shell": names[closest.right.filename],
                    "closest_similarity": f"{closest.percentage:.1f}",
                    "most_distinct_shell": names[most_distinct.right.filename],
                    "most_distinct_similarity": f"{most_distinct.percentage:.1f}",
                }
            )


def write_json(presets, weights, output_file: Path) -> None:
    """
    Write machine-readable similarity comparisons as JSON.

    :param presets: Shell presets to compare
    :param weights: Classification field weighting table
    :param output_file: JSON file to write
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    comparisons = []
    for left in presets:
        for right in presets:
            comparison = compare_presets(left, right, weights)
            comparisons.append(
                {
                    "left": left.filename,
                    "right": right.filename,
                    "similarity": comparison.score,
                    "matching_characteristics": [
                        field.field for field in comparison.matching_fields
                    ],
                    "differing_characteristics": [
                        field.field for field in comparison.differing_fields
                    ],
                }
            )

    output_file.write_text(
        json.dumps({"weights": weights, "comparisons": comparisons}, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """
    Run the morphological similarity command line interface.
    """
    parser = argparse.ArgumentParser(
        description="Calculate morphological similarity between shell presets."
    )
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT_FOLDER,
                        help="Input folder containing shell preset JSON files")
    parser.add_argument("-w", "--weights", type=Path, default=DEFAULT_WEIGHTS_FILE,
                        help="JSON file containing classification field weights")
    parser.add_argument("-md", "--markdown", type=Path,
                        help="Markdown report output file. Prints to stdout when omitted")
    parser.add_argument("-mc", "--matrix-csv", type=Path,
                        help="Similarity matrix CSV with one pairwise score per cell")
    parser.add_argument("-mp", "--matrix-plot", type=Path,
                        help="Annotated 2D similarity matrix PNG plot")
    parser.add_argument("-dp", "--dendrogram-plot", type=Path,
                        help="Similarity dendrogram PNG using average-linkage clustering")
    parser.add_argument("-pc", "--pairwise-csv", type=Path, help="Pairwise comparison CSV")
    parser.add_argument("-nc", "--nearest-csv", type=Path, help="Nearest-neighbour CSV")
    parser.add_argument("-j", "--json", type=Path, help="Optional machine-readable JSON output")
    args = parser.parse_args()

    presets = load_presets(args.input)
    weights = load_weights(args.weights)

    report = render_markdown_report(presets, weights)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report, encoding="utf-8")

    if args.matrix_csv:
        write_matrix_csv(presets, weights, args.matrix_csv)

    if args.matrix_plot:
        write_matrix_plot_png(presets, weights, args.matrix_plot)

    if args.dendrogram_plot:
        write_dendrogram_png(presets, weights, args.dendrogram_plot)

    if args.pairwise_csv:
        write_pairwise_csv(presets, weights, args.pairwise_csv)

    if args.nearest_csv:
        write_nearest_csv(presets, weights, args.nearest_csv)

    if args.json:
        write_json(presets, weights, args.json)


if __name__ == "__main__":
    main()

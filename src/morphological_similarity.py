from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_INPUT_FOLDER = Path(__file__).parent.parent / "data" / "presets"
DEFAULT_WEIGHTS_FILE = Path(__file__).parent.parent / "data" / "config" / "morphological-similarity-weights.config"


@dataclass(frozen=True)
class ShellPreset:
    """
    Classification metadata for one shell preset.
    """

    filename: str
    name: str
    classification: dict[str, str]


@dataclass(frozen=True)
class FieldComparison:
    """
    Comparison result for one classification field.
    """

    field: str
    weight: float
    left_value: str
    right_value: str
    matches: bool


@dataclass(frozen=True)
class SimilarityComparison:
    """
    Weighted similarity result for two shell presets.
    """

    left: ShellPreset
    right: ShellPreset
    score: float
    matched_weight: float
    compared_weight: float
    fields: tuple[FieldComparison, ...]

    @property
    def percentage(self) -> float:
        """
        Express the fractional similarity score as a percentage.

        :return: Similarity percentage
        """
        return self.score * 100.0

    @property
    def matching_fields(self) -> tuple[FieldComparison, ...]:
        """
        Get the classification fields with identical values.

        :return: Field comparisons that matched
        """
        return tuple(field for field in self.fields if field.matches)

    @property
    def differing_fields(self) -> tuple[FieldComparison, ...]:
        """
        Get the classification fields with differing values.

        :return: Field comparisons that differed
        """
        return tuple(field for field in self.fields if not field.matches)


def flatten_classification(classification: dict) -> dict[str, str]:
    """
    Flatten preset classification metadata into comparable fields.

    :param classification: Nested preset classification dictionary
    :return: Flat dictionary of populated classification values
    """
    morphology = classification.get("morphology", {})
    flattened = {
        "family": classification.get("family", ""),
        "geometry": classification.get("geometry", ""),
        **morphology,
    }
    return {key: str(value) for key, value in flattened.items() if value not in ("", None)}


def load_weights(weights_file: Path = DEFAULT_WEIGHTS_FILE) -> dict[str, float]:
    """
    Load positive classification field weights from a JSON file.

    :param weights_file: Path to the weighting JSON file
    :return: Mapping of classification field names to positive weights
    """
    with weights_file.open("r", encoding="utf-8") as f:
        weights = json.load(f)

    return {field: float(weight) for field, weight in weights.items() if float(weight) > 0.0}


def load_presets(input_folder: Path = DEFAULT_INPUT_FOLDER) -> list[ShellPreset]:
    """
    Load shell presets with classification metadata from a folder.

    :param input_folder: Folder containing shell preset JSON files
    :return: Shell presets sorted by filename
    """
    presets = []

    for file in sorted(input_folder.glob("*.json")):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if "classification" not in data:
            continue

        presets.append(
            ShellPreset(
                filename=file.stem,
                name=data.get("name", file.stem),
                classification=flatten_classification(data.get("classification", {})),
            )
        )

    return presets


def compare_presets(
    left: ShellPreset,
    right: ShellPreset,
    weights: dict[str, float],
) -> SimilarityComparison:
    """
    Compare two shell presets using weighted classification matches.

    :param left: First shell preset to compare
    :param right: Second shell preset to compare
    :param weights: Classification field weighting table
    :return: Weighted similarity comparison
    """
    fields = []
    matched_weight = 0.0
    compared_weight = 0.0

    for field, weight in weights.items():
        left_value = left.classification.get(field, "")
        right_value = right.classification.get(field, "")

        if not left_value and not right_value:
            continue

        matches = left_value == right_value
        compared_weight += weight
        if matches:
            matched_weight += weight

        fields.append(
            FieldComparison(
                field=field,
                weight=weight,
                left_value=left_value,
                right_value=right_value,
                matches=matches,
            )
        )

    score = matched_weight / compared_weight if compared_weight else 0.0

    return SimilarityComparison(
        left=left,
        right=right,
        score=score,
        matched_weight=matched_weight,
        compared_weight=compared_weight,
        fields=tuple(fields),
    )


def build_comparison_matrix(
    presets: list[ShellPreset],
    weights: dict[str, float],
) -> dict[tuple[str, str], SimilarityComparison]:
    """
    Compare every shell preset against every other preset.

    :param presets: Shell presets to compare
    :param weights: Classification field weighting table
    :return: Matrix keyed by left and right preset filenames
    """
    return {
        (left.filename, right.filename): compare_presets(left, right, weights)
        for left in presets
        for right in presets
    }


def iter_pairwise_comparisons(
    presets: list[ShellPreset],
    weights: dict[str, float],
) -> Iterable[SimilarityComparison]:
    """
    Iterate over each unique unordered pair of shell presets.

    :param presets: Shell presets to compare
    :param weights: Classification field weighting table
    :return: Iterator of pairwise similarity comparisons
    """
    for left_index, left in enumerate(presets):
        for right in presets[left_index + 1:]:
            yield compare_presets(left, right, weights)


def nearest_neighbours(
    preset: ShellPreset,
    comparisons: dict[tuple[str, str], SimilarityComparison],
) -> tuple[SimilarityComparison, SimilarityComparison]:
    """
    Find the closest and most distinct shells for one preset.

    :param preset: Shell preset to inspect
    :param comparisons: Full comparison matrix
    :return: Closest comparison followed by most distinct comparison
    """
    related = [
        comparison
        for (left, right), comparison in comparisons.items()
        if left == preset.filename and right != preset.filename
    ]
    return (
        max(related, key=lambda comparison: (comparison.score, comparison.right.name)),
        min(related, key=lambda comparison: (comparison.score, comparison.right.name)),
    )


def format_field_name(field: str) -> str:
    """
    Format a classification field name for human-readable reports.

    :param field: Raw classification field name
    :return: Title-cased display name
    """
    return field.replace("_", " ").title()


def format_percentage(value: float) -> str:
    """
    Format a numeric percentage for report output.

    :param value: Percentage value
    :return: Percentage string with compact precision
    """
    rounded = round(value)
    if abs(value - rounded) < 0.005:
        return f"{rounded:.0f}%"
    return f"{value:.1f}%"


def display_names(presets: list[ShellPreset]) -> dict[str, str]:
    """
    Build stable display names, disambiguating duplicate preset names.

    :param presets: Shell presets to name
    :return: Display names keyed by preset filename
    """
    name_counts = {
        preset.name: sum(candidate.name == preset.name for candidate in presets)
        for preset in presets
    }
    return {
        preset.filename: (
            f"{preset.name} ({preset.filename})"
            if name_counts[preset.name] > 1
            else preset.name
        )
        for preset in presets
    }


def render_markdown_report(
    presets: list[ShellPreset],
    weights: dict[str, float],
) -> str:
    """
    Render a full Markdown similarity report.

    :param presets: Shell presets to include in the report
    :param weights: Classification field weighting table
    :return: Markdown report text
    """
    matrix = build_comparison_matrix(presets, weights)
    pairwise = list(iter_pairwise_comparisons(presets, weights))
    names = display_names(presets)
    lines = [
        "# Morphological Similarity Analysis",
        "",
        "Similarity is calculated from preset classification metadata only. Mesh geometry is not inspected.",
        "",
        "## Weighting",
        "",
        "| Characteristic | Weight |",
        "|---|---:|",
    ]

    for field, weight in weights.items():
        lines.append(f"| {format_field_name(field)} | {weight:g} |")

    lines.extend(["", "## Similarity Matrix", ""])
    header = "| Shell | " + " | ".join(names[preset.filename] for preset in presets) + " |"
    alignment = "|---|" + "|".join("---:" for _ in presets) + "|"
    lines.extend([header, alignment])

    for left in presets:
        row = [names[left.filename]]
        for right in presets:
            row.append(format_percentage(matrix[(left.filename, right.filename)].percentage))
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## Nearest Neighbours", ""])
    for preset in presets:
        closest, most_distinct = nearest_neighbours(preset, matrix)
        lines.extend(
            [
                f"### {names[preset.filename]}",
                "",
                f"- Closest: {names[closest.right.filename]} ({format_percentage(closest.percentage)})",
                f"- Most distinct: {names[most_distinct.right.filename]} ({format_percentage(most_distinct.percentage)})",
                "",
            ]
        )

    lines.extend(["## Pairwise Comparisons", ""])
    for comparison in pairwise:
        lines.extend(
            [
                f"### {names[comparison.left.filename]} <-> {names[comparison.right.filename]}",
                "",
                f"Similarity: {format_percentage(comparison.percentage)}",
                "",
                "Shared:",
            ]
        )
        if comparison.matching_fields:
            for field in comparison.matching_fields:
                lines.append(f"- {format_field_name(field.field)}: {field.left_value}")
        else:
            lines.append("- None")

        lines.extend(["", "Differences:"])
        if comparison.differing_fields:
            for field in comparison.differing_fields:
                left_value = field.left_value or "not classified"
                right_value = field.right_value or "not classified"
                lines.append(
                    f"- {format_field_name(field.field)}: "
                    f"{names[comparison.left.filename]} = {left_value}; "
                    f"{names[comparison.right.filename]} = {right_value}"
                )
        else:
            lines.append("- None")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

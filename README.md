[![GitHub issues](https://img.shields.io/github/issues/davewalker5/LogSpiral)](https://github.com/davewalker5/LogSpiral/issues)
[![Releases](https://img.shields.io/github/v/release/davewalker5/LogSpiral.svg?include_prereleases)](https://github.com/davewalker5/LogSpiral/releases)
[![License](https://img.shields.io/badge/License-mit-blue.svg)](https://github.com/davewalker5/LogSpiral/blob/main/LICENSE)
[![Language](https://img.shields.io/badge/language-python-blue.svg)](https://www.python.org)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/davewalker5/LogSpiral)](https://github.com/davewalker5/LogSpiral/)


# LogSpiral - Procedural Shell Morphology

![Example Output](https://github.com/davewalker5/LogSpiral/blob/main/images/shell-002.png?raw=true)

A small exploratory project investigating procedural shell generation using logarithmic spirals, swept apertures and simple growth rules.

The project began after a visit to the Oxford University Museum of Natural History and an observation that many shell forms can emerge from relatively small variations on a simple underlying mathematical model:

> Mollusc shells illustrate beautifully how diversity can arise from just a few variations on one simple mathematical model, encoded in the genes

At its core, the shell geometry is generated from the logarithmic spiral:

```
r = ae^(b x theta)
```

Where:

- a controls the initial shell scale
- b controls the growth rate and tightness of coiling

The shell is treated as a record of growth. An elliptical aperture is swept along the spiral path, expanding over time and stitched into a continuous mesh surface.

Additional features can then be layered onto the basic geometry:

- Growth ribs via periodic aperture modulation
- Pigmentation banding
- Aperture lip flare
- Translucent shell rendering
- Internal chamber septa

The result is not intended as a strict biological simulation, but as an exploration of how relatively simple mathematical and geometric rules can generate complex natural forms.


## Shell Mesh Builder

```python
build_shell_mesh()
```

Builds the outer shell surface by:

1. Generating a sequence of elliptical apertures along the logarithmic spiral
2. Scaling the apertures as the shell grows
3. Optionally modulating aperture size to produce growth ribs
4. Optionally flaring the final aperture to simulate a mature shell lip
5. Stitching neighbouring aperture rings into a continuous triangular mesh

Each aperture ring represents a moment in the shell's growth history.

Per-vertex colour values are also generated to simulate shell pigmentation patterns.

## Chamber Septa Builder

```python
build_chamber_septa()
```

Builds curved internal chamber walls (septa) inside the shell.

At intervals along the growth path:

1. An existing aperture ring is selected
2. Nested interpolated rings are generated inward from the aperture edge
3. The centre of the surface is displaced backward along the growth direction
4. The resulting geometry forms a shallow concave chamber wall

Older chambers can optionally be rendered darker than newer chambers to emphasise shell growth history.

## Rendering

The meshes are rendered using Plotly Mesh3d, allowing:

- Interactive rotation and zooming
- Translucent shell rendering
- Chamber visualisation
- Procedural colour banding
- Shell-like lighting and shading

## Current Status

The project currently supports:

- Logarithmic shell growth
- Ribbed shell surfaces
- Pigmentation bands
- Aperture lip flare
- Curved chamber septa
- Transparent shell rendering

Future directions may include:

- Shell wall thickness
- Siphuncle generation
- Animated shell growth
- Parameter presets for different shell forms

[![GitHub issues](https://img.shields.io/github/issues/davewalker5/LogSpiral)](https://github.com/davewalker5/LogSpiral/issues)
[![Releases](https://img.shields.io/github/v/release/davewalker5/LogSpiral.svg?include_prereleases)](https://github.com/davewalker5/LogSpiral/releases)
[![License](https://img.shields.io/badge/License-mit-blue.svg)](https://github.com/davewalker5/LogSpiral/blob/main/LICENSE)
[![Language](https://img.shields.io/badge/language-python-blue.svg)](https://www.python.org)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/davewalker5/LogSpiral)](https://github.com/davewalker5/LogSpiral/)


# LogSpiral - Procedural Shell Morphology

<table>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/shell-001.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/shell-002.png" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/shell-003.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/shell-004.png" width="100%"></td>
  </tr>
</table>

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

The shell is treated as a record of growth:

1. A sequence of elliptical apertures is generated along the logarithmic spiral
2. The apertures scale progressively as the shell grows
3. Aperture size can be periodically modulated to produce growth ribs
4. The final aperture can be enlarged to simulate a mature shell lip flare
5. An inner shell surface can be generated to create visible shell wall thickness
6. Outer and inner shell surfaces are stitched together into continuous triangular meshes
7. Per-vertex colour values are generated to simulate shell pigmentation banding

Each aperture ring represents a moment in the shell’s developmental history.

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
- Shell wall thickness

Future directions may include:

- Siphuncle generation
- Animated shell growth
- Parameter presets for different shell forms

## Acknowledgements

Inspired by the mathematics of logarithmic shell growth and the broader traditions of theoretical morphology and computational natural history, including the work of D’Arcy Wentworth Thompson and David Raup. All code and implementations in this repository are original to this project.
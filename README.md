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

The result is not intended as a strict biological simulation, but as an exploration of how relatively simple mathematical and geometric rules can generate complex natural forms. That said, the use of logarithmic spirals here is not simply aesthetic or descriptive.

Many real molluscan shells grow by accretion at the aperture edge: new shell material is continuously added around the opening while the overall aperture shape remains broadly similar as the organism enlarges.

Under these conditions, growth becomes approximately self-similar:

- the shell expands continuously
- proportions remain relatively stable
- each new growth stage resembles a scaled version of earlier stages

This tends to produce shell geometries closely approximated by logarithmic spirals, where radial expansion is proportional to current size rather than occurring in fixed linear increments.

The logarithmic spiral therefore acts both as:

- a useful mathematical model of shell form
- and as a simplified representation of an underlying biological growth process

Real shells additionally reflect genetics, environment, biomechanics and ecological pressures, all of which can perturb or modify the underlying geometric pattern.

---

## Example Shell Presets

The shell generator includes a growing collection of parameter presets that explore different regions of shell morphospace using variations in:

- Logarithmic growth rate
- Aperture scaling
- Coiling geometry
- Shell inflation
- Ornamentation (ribbing)
- Aperture flare
- Shell wall thickness

Although highly simplified, these presets demonstrate how a relatively small set of growth parameters can produce shell forms reminiscent of real molluscan and cephalopod shells.

### Nautilus-Like Shell

<table>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/nautilus-001.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/nautilus-002.png" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/nautilus-003.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/nautilus-004.png" width="100%"></td>
  </tr>
</table>

The nautilus-like preset produces a tightly coiled, inflated shell with adjacent whorls in contact.

Characteristics:

- Smooth rounded whorl profile
- Relatively low expansion rate
- Planispiral coiling
- Broad inflated chambers
- Visible siphuncle and chamber septa

This form resembles extant chambered nautiluses, whose shells grow as expanding logarithmic spirals with internally partitioned buoyancy chambers.

The model demonstrates how relatively modest geometric rules can produce biologically recognisable cephalopod shell forms.

### Smooth Nautilus

<table>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/smooth-nautilus-001.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/smooth-nautilus-002.png" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/smooth-nautilus-003.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/smooth-nautilus-004.png" width="100%"></td>
  </tr>
</table>

The smooth nautilus variant removes geometric ribbing while retaining pigmentation banding and shell inflation.

Compared with the ornamented nautilus-like form:

- Shell growth appears calmer and more continuous
- The underlying logarithmic geometry becomes more visually apparent
- Pigmentation and curvature dominate the visual texture

This preset highlights the distinction between:

- Shell geometry
- Shell ornamentation
- Shell pigmentation

which are treated separately within the model.

### Ammonite-Like Shell

<table>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/ammonite-001.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/ammonite-002.png" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/ammonite-003.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/ammonite-004.png" width="100%"></td>
  </tr>
</table>

The ammonite-like preset exaggerates shell expansion and ornamentation relative to the nautilus form.

Characteristics:

- Broader outer whorl
- Stronger radial ribbing
- More compressed appearance
- Faster shell expansion
- Larger visible aperture

The resulting morphology resembles many fossil ammonites, particularly strongly ribbed planispiral forms.

The model demonstrates how relatively small parameter changes can shift shell morphology from nautilus-like inflation toward more ornamented ammonite-like geometries.

Transparent rendering additionally reveals:

- Internal chamber spacing
- Septal placement
- Siphuncle trajectory

providing a simplified visualisation of cephalopod internal shell structure.

### Ramshorn-Like Shell

<table>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/ramshorn-001.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/ramshorn-002.png" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/ramshorn-003.png" width="100%"></td>
  </tr>
</table>

The ramshorn preset explores planispiral gastropod morphology rather than chambered cephalopods.

Characteristics:

- Smooth rounded tube-like whorls
- Strongly flattened coiling
- Broad body whorl
- Relatively simple aperture geometry
- Minimal ornamentation

The resulting form resembles freshwater ramshorn snails (Planorbidae), whose shells coil within a near-planar spiral.

Unlike the cephalopod-inspired presets, this form is primarily driven by smooth continuous growth rather than chambered internal structure.

Reducing ribbing proved important here, as excessive ornamentation quickly pushed the morphology back toward ammonite-like forms.

### Flared Shell

<table>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/flared-001.png" width="100%"></td>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/flared-002.png" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/davewalker5/LogSpiral/blob/main/images/flared-003.png" width="100%"></td>
  </tr>
</table>

The flared shell preset intentionally explores more open and exaggerated shell geometries.

Characteristics:

- Rapidly expanding aperture
- Separated whorls
- Open spiral growth
- Dramatic terminal flare
- Loosely coiled geometry

Unlike the more biologically conservative presets, this form acts as an exploration of the shell generator’s morphospace.

The resulting geometry resembles aspects of:

- Vermetid shells
- Juvenile uncoiled gastropods
- Speculative or transitional shell forms

and demonstrates how altering aperture expansion can fundamentally change shell architecture.

Interestingly, once whorl abutment is relaxed, the shell begins to behave more like a continuously expanding tube traced through space rather than a tightly packed coil.

### Observations

An important aspect of logarithmic shell growth is self-similarity.

As the shell enlarges, the organism can continue growing without fundamentally changing its body geometry. Earlier shell stages therefore become preserved records of previous growth states, producing the characteristic coiled shell forms seen in many molluscs and cephalopods.

The project therefore treats shell form not simply as static geometry, but as accumulated developmental history emerging from iterative growth rules.

A recurring theme across these presets is that shell morphology emerges from the interaction between only a few core mechanisms:

1. Logarithmic radial growth
2. Aperture scaling
3. Coiling rate
4. Ornamentation modulation
5. Terminal aperture flare

Small parameter changes can produce disproportionately large morphological differences.

The project therefore acts not only as a graphics exercise, but also as a simplified exploration of computational natural history and developmental morphology.

In particular, separating:

- Growth trajectory
- Aperture geometry
- Ornamentation
- Pigmentation
- Internal shell structures

proved important both visually and conceptually.

This mirrors, in a highly simplified way, the layered processes involved in real biological shell formation.

---

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

## Siphuncle Builder

```python
build_siphuncle_mesh()
```

Builds a simplified siphuncle running through the shell chambers.

The siphuncle is modelled as a small tube that follows the shell’s growth path through the chambered interior.

At each growth stage:

1. The centre of an aperture ring is estimated
2. The siphuncle position is offset slightly from the chamber centre
3. A small circular tube section is generated
4. Neighbouring tube sections are stitched into a continuous mesh

This provides a simplified representation of the tube-like structure that connects chambered cephalopod shell compartments.

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
- Siphuncle generation
- Parameter presets for different shell forms

Future directions may include:

- Animated shell growth
- Involute versus evolute coiling

## Acknowledgements

Inspired by the mathematics of logarithmic shell growth and the broader traditions of theoretical morphology and computational natural history, including the work of D’Arcy Wentworth Thompson and David Raup.

All code and implementations in this repository are original to this project.

For the historical and theoretical background, see, please see [BACKGROUND.md](https://github.com/davewalker5/LogSpiral/blob/main/BACKGROUND.md)

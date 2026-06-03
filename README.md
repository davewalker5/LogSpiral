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

## Getting Started

A catalogue of the implemented shell forms, together with modelling notes, observations, and example renderings, is available in the [Wiki](https://github.com/davewalker5/LogSpiral/wiki).

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

For the historical and theoretical background, please see [BACKGROUND.md](https://github.com/davewalker5/LogSpiral/blob/main/BACKGROUND.md)

## Feedback

To file issues or suggestions, please use the [Issues](https://github.com/davewalker5/LogSpiral/issues) page for this project on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

---
id: mod.draw-a-grid-of-colored-cells
kind: mod
status: VERIFIED
title: "Draw a grid of colored cells"
sources: [S57]
---

# Draw a grid of colored cells

**Sources:** [S57](src.s57.md)

For a heat map, a sparkline, or a game board in the terminal, draw one `Raster` and not a `Box` for each cell. A `Raster` takes a `key`, its size in `columns` and `rows`, and `cells`, a base64 string that packs every cell. Each cell is three numbers: the character's code point, its color, and its background color. A color is a 24-bit RGB value in hexadecimal, such as `0xc62828` for a red. The valu

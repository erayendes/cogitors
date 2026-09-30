# Decision Void — final mark

The final geometry uses three **identical** chevrons on an 18-unit horizontal step. Each chevron uses the same 18-unit coordinate thickness; the 36-unit decision square is exactly two grid units. The lightest chevron ends at x=164 and the decision square starts at x=180, leaving a deliberate 16-unit gap.

The full group spans x=40–216, so it is centered at x=128. The 216-unit tile uses a 44-unit corner radius. All artwork is flat fill with no gradients.

## Primary colors

| Role | Hex |
| --- | --- |
| Tile | `#2B1724` |
| Chevron 1 | `#704159` |
| Chevron 2 | `#AA506D` |
| Chevron 3 | `#E17B92` |
| Decision square | `#FBEFF2` |

## Usage

- Use `mark.svg` as the default. Its solid fourth-color square stays visible on light and dark backgrounds.
- Use `favicon.svg` at 16–64 px; its simplified integer grid is tuned for small rendering.
- Minimum digital size: 16 px for the tiled mark, 24 px for `mark-flat.svg`, and 28 px tall for the lockup.
- Keep clear space around the mark equal to one 18-unit grid step (about 7% of its width).
- `mark-flat.svg` is the tile-less adaptation and uses the same solid fourth-color decision square.

## Wordmark

The wordmark uses **Unica One Regular** at 80 px with **+3.2 px tracking (4% of the font size)**. The lockup SVGs store the lettering as outlines, so they have no runtime font dependency.

Unica One is licensed under the **SIL Open Font License 1.1 (OFL)**; the font file and license are in `fonts/` (`UnicaOne.ttf`, `OFL.txt`).

## Files

- `mark.svg`, `mark-flat.svg`: mark with and without the tile.
- `app-icon.svg`, `favicon.svg`: icons.
- `lockup.svg`, `lockup-dark.svg`: mark + wordmark for light and dark backgrounds.
- `png/`: raster renders of the above.

## Social preview

`social-preview.svg` uses the `#2B1724` background, the outlined Unica One lockup, and outlined Inter Medium/Regular text in `#C9A3B2` and `#A98294`. The upload-ready PNG is at `assets/social-preview.png`; upload it manually in **GitHub Settings > General > Social preview**.

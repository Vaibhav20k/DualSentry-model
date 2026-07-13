/**
 * Sentinel palette expressed as literal values for Recharts / SVG.
 *
 * Recharts paints SVG presentation attributes, which do not resolve CSS
 * `var()` — so chart strokes/fills need concrete colors. These mirror the
 * tokens defined in `src/index.css` (the single source of truth for the
 * rest of the UI) and exist only to satisfy the SVG rendering layer.
 */
export const sentinel = {
  primary: "#99462a",
  onPrimary: "#ffffff",
  secondary: "#506358",
  outline: "#88726c",
  error: "#ba1a1a",
  tertiaryContainer: "#7e95a7",
  surfaceContainerLow: "#f5f3ee",
  surfaceContainerLowest: "#ffffff",
  onSurface: "#1b1c19",
  onSurfaceVariant: "#55433d",
  outlineVariant: "#dbc1b9",
  primaryContainer: "#d97757",
} as const;

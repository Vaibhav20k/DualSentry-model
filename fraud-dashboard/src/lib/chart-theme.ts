import { useTheme } from "@/context/theme-context";

export const sentinelLight = {
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

export const sentinelDark = {
  primary: "#F97316",
  onPrimary: "#ffffff",
  secondary: "#22C55E",
  outline: "#2B3B55",
  error: "#EF4444",
  tertiaryContainer: "#FACC15",
  surfaceContainerLow: "#172236",
  surfaceContainerLowest: "#131C2E",
  onSurface: "#F8FAFC",
  onSurfaceVariant: "#94A3B8",
  outlineVariant: "#2B3B55",
  primaryContainer: "#EA580C",
} as const;

export const sentinel = sentinelLight;

export function useSentinelTheme() {
  const { theme } = useTheme();
  return theme === "dark" ? sentinelDark : sentinelLight;
}

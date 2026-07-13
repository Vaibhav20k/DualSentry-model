import { cn } from "@/lib/utils";

type Tone =
  | "allow"
  | "review"
  | "block"
  | "neutral"
  | "secondary"
  | "error";

const tones: Record<Tone, string> = {
  allow: "bg-secondary-fixed text-on-secondary-fixed-variant",
  review: "bg-secondary-container text-on-secondary-fixed-variant",
  block: "bg-error-container text-on-error-container",
  neutral: "bg-surface-container-high text-on-surface-variant",
  secondary: "bg-secondary-container text-on-secondary-container",
  error: "bg-error-container text-on-error-container",
};

interface Props {
  label: string;
  tone?: Tone;
  className?: string;
}

/** Pill-shaped status chip. Decision tones match the Sentinel design. */
export default function StatusBadge({
  label,
  tone = "neutral",
  className,
}: Props) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-sm py-xs text-label-sm font-bold uppercase tracking-wide",
        tones[tone],
        className
      )}
    >
      {label}
    </span>
  );
}

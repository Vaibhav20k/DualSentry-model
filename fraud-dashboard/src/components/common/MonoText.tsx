import { cn } from "@/lib/utils";

interface Props {
  children: React.ReactNode;
  className?: string;
}

/** Inline monospaced text (JetBrains Mono) for IDs, timestamps, metadata. */
export default function MonoText({ children, className }: Props) {
  return (
    <span className={cn("font-mono text-label-sm", className)}>{children}</span>
  );
}

import { cn } from "@/lib/utils";

interface Props {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

/** Page / region heading with optional supporting line and trailing action. */
export default function SectionHeader({
  title,
  subtitle,
  action,
  className,
}: Props) {
  return (
    <div
      className={cn("flex items-start justify-between gap-md mb-lg", className)}
    >
      <div>
        <h2 className="font-heading text-headline-md text-on-surface">{title}</h2>
        {subtitle && (
          <p className="font-body text-body-md text-on-surface-variant mt-xs">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

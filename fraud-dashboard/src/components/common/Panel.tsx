import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

interface PanelProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: LucideIcon;
  /** Draw a hairline divider under the header (tables / logs). */
  headerBorder?: boolean;
  className?: string;
  /** Padding for the body region. Consumers control it per panel. */
  bodyClassName?: string;
  /** Optional pinned footer rendered outside the scrollable body. */
  footer?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * Level-1 surface: pure white, hairline border, soft ambient shadow.
 * Optionally renders a header (title + subtitle + icon + action) and a
 * body region. Used for every elevated container in the dashboard.
 */
export default function Panel({
  title,
  subtitle,
  action,
  icon: Icon,
  headerBorder = false,
  className,
  bodyClassName = "",
  footer,
  children,
}: PanelProps) {
  const hasHeader = Boolean(title || subtitle || action || Icon);

  return (
    <section className={cn("tonal-layer-1 flex flex-col", className)}>
      {hasHeader && (
        <div
          className={cn(
            "p-lg flex items-start justify-between gap-md",
            headerBorder && "border-b border-outline-variant/20"
          )}
        >
          <div className="flex items-center gap-sm">
            {Icon && <Icon className="text-secondary" size={20} />}
            <div>
              {title && (
                <h3 className="font-heading text-headline-sm text-on-surface">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="font-body text-body-md text-on-surface-variant mt-xs">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className={cn(bodyClassName)}>{children}</div>
      {footer && <div className="shrink-0">{footer}</div>}
    </section>
  );
}

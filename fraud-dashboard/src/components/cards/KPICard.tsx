import { cn } from "@/lib/utils";
import type { KpiMetric } from "@/types";

const trendTone: Record<NonNullable<KpiMetric["trend"]>["tone"] & string, string> = {
  positive: "text-secondary",
  negative: "text-error",
  neutral: "text-on-surface-variant opacity-50",
};

/**
 * Compact KPI tile. Optional `icon` keeps the component reusable, though the
 * Sentinel design's dashboard KPIs render label / value / trend only.
 */
export default function KPICard({
  title,
  value,
  trend,
  description,
  icon: Icon,
  variant = "default",
}: KpiMetric) {
  return (
    <div
      className={cn(
        "tonal-layer-1 p-md rounded-xl shadow-soft flex flex-col",
        variant === "danger" && "border-l-4 border-l-error",
        variant === "model" && "bg-surface-container-highest/30"
      )}
    >
      <div className="flex items-start justify-between gap-sm">
        <p className="font-mono text-label-sm uppercase tracking-wider text-on-surface-variant mb-xs">
          {title}
        </p>
        {Icon && (
          <span className="rounded-lg bg-surface-container-high p-2 text-primary-container">
            <Icon size={18} />
          </span>
        )}
      </div>

      {variant === "model" ? (
        <>
          <h2 className="font-label-md text-label-md font-bold text-primary truncate">
            {value}
          </h2>
          {description && (
            <p className="text-[10px] text-secondary font-label-sm mt-1">
              {description}
            </p>
          )}
        </>
      ) : (
        <>
          <div className="flex items-baseline gap-xs">
            <h2 className="font-heading text-headline-md text-on-surface">
              {value}
            </h2>
            {trend && (
              <span
                className={cn(
                  "font-label-sm text-label-sm flex items-center",
                  trendTone[trend.tone ?? "neutral"]
                )}
              >
                {trend.value}
              </span>
            )}
          </div>
          {description && (
            <p className="mt-1 text-xs text-on-surface-variant opacity-70">
              {description}
            </p>
          )}
        </>
      )}
    </div>
  );
}

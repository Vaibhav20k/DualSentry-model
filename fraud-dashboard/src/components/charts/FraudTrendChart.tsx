import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import Panel from "@/components/common/Panel";
import { sentinel } from "@/lib/chart-theme";
import { useTrend } from "@/hooks/useTrend";

interface TooltipEntry {
  dataKey?: string | number;
  name?: string;
  value?: number;
  color?: string;
}

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipEntry[];
  label?: string | number;
}) {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest px-sm py-xs shadow-soft">
      <p className="font-label-sm text-on-surface-variant">
        {label}
      </p>

      {payload.map((p) => (
        <p
          key={String(p.dataKey)}
          className="font-label-sm text-on-surface flex items-center gap-xs"
        >
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: p.color }}
          />

          <span className="text-on-surface-variant">
            {p.name}
          </span>

          <span className="font-bold text-on-surface ml-1">
            {p.value}
          </span>
        </p>
      ))}
    </div>
  );
}
type TrendPoint = {
  time: string;
  count: number;
};

export default function FraudTrendChart() {
  const { data, isLoading, error } = useTrend();

  const trendData = (Array.isArray(data) ? data : []).map(
    (item: TrendPoint) => ({
      hour: item.time,
      confirmed: item.count,
      predicted: item.count,
    })
  );

  if (isLoading) {
    return (
      <Panel
        title="Suspicious Activity Forecast"
        subtitle="Real-time predictive trend analysis"
        className="lg:col-span-8"
      >
        <div className="flex items-center justify-center h-[320px]">
          Loading trend...
        </div>
      </Panel>
    );
  }

  if (error) {
    return (
      <Panel
        title="Suspicious Activity Forecast"
        subtitle="Real-time predictive trend analysis"
        className="lg:col-span-8"
      >
        <div className="flex items-center justify-center h-[320px] text-red-500">
          Failed to load trend.
        </div>
      </Panel>
    );
  }

  return (
    <Panel
      title="Suspicious Activity Forecast"
      subtitle="Real-time predictive trend analysis (24h window)"
      className="lg:col-span-8 overflow-hidden relative"
      bodyClassName="p-lg"
      action={
        <div className="flex gap-sm">
          <span className="px-sm py-xs bg-surface-container-high rounded text-label-sm font-label-sm">
            Day
          </span>
          <span className="px-sm py-xs bg-primary text-on-primary rounded text-label-sm font-label-sm">
            Week
          </span>
        </div>
      }
    >
      <div className="relative h-[300px] w-full rounded-lg overflow-hidden bg-surface-container-low border border-outline-variant/20">
        {/* Legend */}
        <div className="absolute top-4 right-4 flex gap-md z-10">
          <div className="flex items-center gap-xs">
            <span className="w-3 h-0.5 bg-primary" />
            <span className="font-label-sm text-on-surface-variant">
              Confirmed Fraud
            </span>
          </div>

          <div className="flex items-center gap-xs">
            <span className="w-3 h-0.5 border-t border-dashed border-outline" />
            <span className="font-label-sm text-on-surface-variant">
              Predictions
            </span>
          </div>
        </div>

        <div className="absolute inset-0 opacity-10 dotted-grid" />

        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={trendData}
            margin={{ top: 28, right: 16, bottom: 4, left: 0 }}
          >
            <defs>
              <linearGradient
                id="confirmedFill"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="0%"
                  stopColor={sentinel.primary}
                  stopOpacity={0.12}
                />
                <stop
                  offset="100%"
                  stopColor={sentinel.primary}
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <XAxis
              dataKey="hour"
              axisLine={false}
              tickLine={false}
              interval={0}
              tick={{
                fontSize: 10,
                fill: sentinel.onSurfaceVariant,
                opacity: 0.5,
              }}
            />

            <YAxis hide />

            <Tooltip
              content={<ChartTooltip />}
              cursor={{
                stroke: sentinel.outlineVariant,
                strokeWidth: 1,
              }}
            />

            <Area
              type="monotone"
              dataKey="confirmed"
              stroke="none"
              fill="url(#confirmedFill)"
              isAnimationActive={false}
            />

            <Line
              type="monotone"
              dataKey="predicted"
              name="Predictions"
              stroke={sentinel.outline}
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
              opacity={0.6}
              isAnimationActive={false}
            />

            <Line
              type="monotone"
              dataKey="confirmed"
              name="Confirmed Fraud"
              stroke={sentinel.primary}
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
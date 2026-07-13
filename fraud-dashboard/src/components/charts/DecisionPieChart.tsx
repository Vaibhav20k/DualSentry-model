import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

import Panel from "@/components/common/Panel";
import { sentinel } from "@/lib/chart-theme";
import { cn } from "@/lib/utils";
import { useDecisionStats } from "@/hooks/useDecisionStats";



const histogram = [
  { h: "h-[10%]", c: "bg-tertiary-container/20" },
  { h: "h-[20%]", c: "bg-tertiary-container/20" },
  { h: "h-[40%]", c: "bg-tertiary-container/40" },
  { h: "h-[70%]", c: "bg-tertiary-container/60" },
  { h: "h-[90%]", c: "bg-tertiary-container" },
  { h: "h-[60%]", c: "bg-tertiary-container/60" },
  { h: "h-[30%]", c: "bg-tertiary-container/40" },
  { h: "h-[15%]", c: "bg-error/40" },
  { h: "h-[25%]", c: "bg-error/60" },
  { h: "h-[45%]", c: "bg-error" },
];

export default function DecisionPieChart() {
  const { stats } = useDecisionStats();

  const pieData = [
    {
      name: "Allow",
      count: stats.allow,
      value: Number(stats.allowPercent.toFixed(1)),
      color: sentinel.secondary,
    },
    {
      name: "Review",
      count: stats.review,
      value: Number(stats.reviewPercent.toFixed(1)),
      color: sentinel.tertiaryContainer,
    },
    {
      name: "Block",
      count: stats.block,
      value: Number(stats.blockPercent.toFixed(1)),
      color: sentinel.error,
    },
  ];

  if (stats.total === 0) {
    return (
      <Panel
        title="Decision Distribution"
        subtitle="Current volume by action type"
        className="lg:col-span-4"
      >
        <div className="flex items-center justify-center h-64 text-on-surface-variant">
          No prediction data available.
        </div>
      </Panel>
    );
}

  return (
    <Panel
      title="Decision Distribution"
      subtitle="Current volume by action type"
      className="lg:col-span-4"
      bodyClassName="p-lg flex flex-col"
    >
      <div className="flex items-center gap-lg mb-xl">
        <div className="relative w-32 h-32 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                innerRadius={52}
                outerRadius={64}
                paddingAngle={2}
                stroke="none"
                startAngle={90}
                endAngle={-270}
                isAnimationActive={false}
              >
                {pieData.map((e) => (
                  <Cell key={e.name} fill={e.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-lg font-bold font-label-md text-on-surface">
              {stats.total}
            </span>
            <span className="text-[8px] text-on-surface-variant uppercase">
              Total
            </span>
          </div>
        </div>

        <div className="space-y-2 flex-1">
          {pieData.map((e) => (
            <div
              key={e.name}
              className="flex justify-between items-center text-label-sm"
            >
              <span className="flex items-center gap-sm">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: e.color }}
                />
                {e.name}
              </span>
              <span className="font-bold text-on-surface">
                {e.count} ({e.value.toFixed(1)}%)
              </span>
            </div>
          ))}
        </div>
      </div>

            


      {/* Score histogram */}
      <div className="space-y-sm mt-auto">
        <div className="text-[10px] text-on-surface-variant font-label-sm uppercase tracking-wider mb-xs">
          Score Histogram
        </div>
        <div className="flex items-end gap-[2px] h-16 w-full">
          {histogram.map((bar, i) => (
            <div
              key={i}
              className={cn("w-full rounded-sm", bar.c, bar.h)}
            />
          ))}
        </div>
        <div className="flex justify-between text-[8px] text-on-surface-variant mt-xs">
          <span>LOW RISK (0.0)</span>
          <span>HIGH RISK (1.0)</span>
        </div>
      </div>
    </Panel>
  );
}

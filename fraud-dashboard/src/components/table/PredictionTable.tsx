import { Eye, ArrowRight } from "lucide-react";

import Panel from "@/components/common/Panel";
import StatusBadge from "@/components/common/StatusBadge";
import { cn } from "@/lib/utils";
import type { Prediction, Decision } from "@/types";

const COLUMNS = [
  "Transaction ID",
  "User Identifier",
  "Risk Prob.",
  "Decision",
  "Action",
];

function riskTone(p: number): "error" | "primaryContainer" | "secondary" {
  if (p >= 0.7) return "error";
  if (p >= 0.4) return "primaryContainer";
  return "secondary";
}

const barFill: Record<string, string> = {
  error: "bg-error",
  primaryContainer: "bg-primary-container",
  secondary: "bg-secondary",
};

const valueText: Record<string, string> = {
  error: "text-error",
  primaryContainer: "text-primary-container",
  secondary: "text-secondary",
};

function decisionTone(d: Decision): "allow" | "review" | "block" {
  if (d === "BLOCK") return "block";
  if (d === "REVIEW") return "review";
  return "allow";
}



interface Props {
  /** Feed from the API / WebSocket. Falls back to design mock data. */
  data?: Prediction[];
}

export default function PredictionTable({ data = [] }: Props) {
  return (
    <Panel
      title="Recent Model Predictions"
      subtitle="Live feed of high-probability scoring events"
      headerBorder
      className="lg:col-span-2"
      bodyClassName="overflow-x-auto"
      action={
        <button className="text-primary font-label-md hover:underline flex items-center gap-xs">
          View Full Queue
          <ArrowRight size={16} />
        </button>
      }
    >
      <table className="w-full text-left">
        <thead>
          <tr className="bg-surface-container-low">
            {COLUMNS.map((h) => (
              <th
                key={h}
                className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider whitespace-nowrap"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant/10">
          {data.map((row) => {
            const probability = Number(row.probability ?? 0);
            const tone = riskTone(probability);
            return (
              <tr
                key={row.id}
                className="hover:bg-surface-container-low/50 transition-colors"
              >
                <td className="px-lg py-md font-label-md text-on-surface whitespace-nowrap">
                  {row.id}
                </td>
                <td className="px-lg py-md font-label-md text-on-surface-variant whitespace-nowrap">
                  {row.user}
                </td>
                <td className="px-lg py-md">
                  <div className="flex items-center gap-sm">
                    <div className="w-16 h-2 bg-surface-container-high rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full", barFill[tone])}
                        style={{ width: `${Math.round(probability * 100)}%` }}
                      />
                    </div>
                    <span className={cn("font-label-md", valueText[tone])}>
                      {probability.toFixed(2)}
                    </span>
                  </div>
                </td>
                <td className="px-lg py-md">
                  <StatusBadge
                    label={row.decision}
                    tone={decisionTone(row.decision)}
                  />
                </td>
                <td className="px-lg py-md text-right">
                  <button
                    type="button"
                    aria-label={`View ${row.id}`}
                    className="p-xs text-on-surface-variant hover:text-primary transition-colors"
                  >
                    <Eye size={18} />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </Panel>
  );
}

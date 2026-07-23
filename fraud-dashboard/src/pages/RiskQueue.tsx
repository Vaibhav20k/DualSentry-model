import { useMemo } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { ShieldAlert, ShieldCheck } from "lucide-react";

import Panel from "@/components/common/Panel";
import StatusBadge from "@/components/common/StatusBadge";
import { cn } from "@/lib/utils";
import { usePredictions } from "@/hooks/usePredictions";
import type { Prediction, Decision } from "@/types";

function decisionTone(d: Decision): "allow" | "review" | "block" {
  if (d === "BLOCK") return "block";
  if (d === "REVIEW") return "review";
  return "allow";
}

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

export default function RiskQueue() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const decisionParam = searchParams.get("decision") || "ALL";

  const { data: rawData = [], isLoading, error } = usePredictions();

  const riskItems: Prediction[] = useMemo(() => {
    return rawData
      .map((p) => ({
        id: p.transactionID,
        user: p.userID,
        probability: p.fraudProbability,
        decision: p.decision as Decision,
        riskFlags: p.riskFlags ?? [],
      }))
      .filter((item) => item.decision === "REVIEW" || item.decision === "BLOCK");
  }, [rawData]);

  const filteredItems = useMemo(() => {
    if (decisionParam === "ALL") return riskItems;
    return riskItems.filter((item) => item.decision === decisionParam);
  }, [riskItems, decisionParam]);

  return (
    <div className="space-y-lg">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-md">
        <div>
          <div className="flex items-center gap-sm">
            <ShieldAlert size={28} className="text-error" />
            <h1 className="font-heading text-headline-md font-bold text-on-surface">
              High Risk & Review Queue
            </h1>
          </div>
          <p className="font-body text-body-md text-on-surface-variant">
            Transactions flagged for manual analyst review or automated block enforcement
          </p>
        </div>

        {/* Tab filters */}
        <div className="flex bg-surface-container-low p-xs rounded-lg border border-outline-variant/20">
          <button
            onClick={() => setSearchParams({})}
            className={cn(
              "px-md py-xs rounded font-label-md text-label-sm transition-all cursor-pointer",
              decisionParam === "ALL"
                ? "bg-primary-container text-on-primary-container font-bold"
                : "text-on-surface-variant hover:text-on-surface"
            )}
          >
            All Risk ({riskItems.length})
          </button>
          <button
            onClick={() => setSearchParams({ decision: "REVIEW" })}
            className={cn(
              "px-md py-xs rounded font-label-md text-label-sm transition-all cursor-pointer",
              decisionParam === "REVIEW"
                ? "bg-tertiary-container text-on-tertiary-container font-bold"
                : "text-on-surface-variant hover:text-on-surface"
            )}
          >
            Review ({riskItems.filter((i) => i.decision === "REVIEW").length})
          </button>
          <button
            onClick={() => setSearchParams({ decision: "BLOCK" })}
            className={cn(
              "px-md py-xs rounded font-label-md text-label-sm transition-all cursor-pointer",
              decisionParam === "BLOCK"
                ? "bg-error/20 text-error font-bold"
                : "text-on-surface-variant hover:text-on-surface"
            )}
          >
            Block ({riskItems.filter((i) => i.decision === "BLOCK").length})
          </button>
        </div>
      </div>

      <Panel headerBorder bodyClassName="overflow-x-auto">
        {isLoading ? (
          <div className="p-xl text-center text-on-surface-variant">Loading risk queue...</div>
        ) : error ? (
          <div className="p-xl text-center text-red-500">Failed to load risk queue.</div>
        ) : filteredItems.length === 0 ? (
          <div className="p-xl text-center text-on-surface-variant flex flex-col items-center gap-sm">
            <ShieldCheck size={40} className="text-secondary opacity-60" />
            <p className="font-label-md text-label-md">No flagged transactions in this queue.</p>
          </div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="bg-surface-container-low">
                <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Transaction ID
                </th>
                <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  User Identifier
                </th>
                <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Decision
                </th>
                <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Risk Flags
                </th>
                <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider text-right">
                  Analyst Action
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filteredItems.map((row) => {
                const probability = Number(row.probability ?? 0);
                const tone = riskTone(probability);
                return (
                  <tr key={row.id} className="hover:bg-surface-container-low/50 transition-colors">
                    <td className="px-lg py-md font-label-md text-on-surface whitespace-nowrap">
                      {row.id}
                    </td>
                    <td className="px-lg py-md font-label-md text-on-surface-variant whitespace-nowrap">
                      {row.user}
                    </td>
                    <td className="px-lg py-md">
                      <div className="flex items-center gap-sm">
                        <div className="w-20 h-2.5 bg-surface-container-high rounded-full overflow-hidden">
                          <div
                            className={cn("h-full rounded-full", barFill[tone])}
                            style={{ width: `${Math.round(probability * 100)}%` }}
                          />
                        </div>
                        <span className={cn("font-bold text-label-md", valueText[tone])}>
                          {(probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-lg py-md">
                      <StatusBadge label={row.decision} tone={decisionTone(row.decision)} />
                    </td>
                    <td className="px-lg py-md">
                      <div className="flex flex-wrap gap-1 max-w-[260px]">
                        {row.riskFlags?.length ? (
                          row.riskFlags.map((flag) => (
                            <span
                              key={flag}
                              className="px-2 py-1 rounded-full text-[10px] font-semibold bg-error/10 text-error"
                            >
                              {flag}
                            </span>
                          ))
                        ) : (
                          <span className="text-on-surface-variant text-xs">Unflagged</span>
                        )}
                      </div>
                    </td>
                    <td className="px-lg py-md text-right">
                      <button
                        type="button"
                        onClick={() => navigate(`/investigation/new?id=${row.id}`)}
                        className="px-md py-xs bg-primary text-on-primary font-label-sm text-label-sm rounded-lg hover:opacity-90 transition-all shadow-soft cursor-pointer"
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  );
}

import KPICard from "@/components/cards/KPICard";
import FraudTrendChart from "@/components/charts/FraudTrendChart";
import DecisionPieChart from "@/components/charts/DecisionPieChart";
import PredictionTable from "@/components/table/PredictionTable";
import LiveLogs from "@/components/logs/LiveLogs";
import type { KpiMetric, Prediction, LogEntry } from "@/types";

import { useDashboard } from "../hooks/useDashboard";
import { usePredictions } from "../hooks/usePredictions";

const logs: LogEntry[] = [
  { id: "l1", time: "6:57:41 PM", message: "DATA_INGEST: Batch #2747 received", level: "info" },
  { id: "l2", time: "6:57:33 PM", message: "DATA_INGEST: Batch #72 received", level: "info" },
  { id: "l3", time: "6:57:25 PM", message: "DATA_INGEST: Batch #1441 received", level: "info" },
  { id: "l4", time: "6:57:17 PM", message: "DATA_INGEST: Batch #6973 received", level: "info" },
  { id: "l5", time: "6:57:09 PM", message: "HEARTBEAT: Health Check Green", level: "success" },
  { id: "l6", time: "12:45:01 UTC", message: "MODEL_INIT_SUCCESS: XGBoost v1.0.4 loaded.", level: "success" },
  { id: "l7", time: "12:44:58 UTC", message: "THRESHOLD_ALERT: Risk Score > 0.90 detected.", level: "alert", detail: "Ref: TX-9421-B flagged for immediate block." },
  { id: "l8", time: "12:44:30 UTC", message: "DB_SYNC: Transaction batch 4022 processed.", level: "info" },
  { id: "l9", time: "12:44:15 UTC", message: "HEARTBEAT: System health normal. Latency: 22ms.", level: "info" },
  { id: "l10", time: "12:43:55 UTC", message: "QUEUE_UPDATE: Review queue increased (+4).", level: "warning" },
  { id: "l11", time: "12:43:10 UTC", message: "AUDIT_LOG: User 'Analyst 402' logged in.", level: "muted" },
];

export default function Dashboard() {
  const { data, isLoading, error } = useDashboard();

  const {
    data: predictionData,
    isLoading: predictionLoading,
  } = usePredictions();

  const predictions: Prediction[] =
    predictionData?.map((p) => ({
      id: p.transactionID,
      user: p.userID,
      probability: p.fraudProbability,
      decision: p.decision as Prediction["decision"],
    })) ?? [];

  const kpis: KpiMetric[] = [
    {
      title: "Total Trans.",
      value: isLoading ? "..." : String(data?.totalTransactions ?? 0),
      trend: { value: "+4.2%", tone: "positive" },
    },
    {
      title: "Fraudulent",
      value: isLoading ? "..." : String(data?.fraudulent ?? 0),
      trend: { value: "+12", tone: "negative" },
      variant: "danger",
    },
    {
      title: "Review Queue",
      value: isLoading ? "..." : String(data?.review ?? 0),
      trend: { value: "Active", tone: "neutral" },
    },
    {
      title: "Fraud Rate",
      value: isLoading
        ? "..."
        : `${(data?.fraudRate ?? 0).toFixed(2)}%`,
      trend: { value: "-0.3%", tone: "positive" },
    },
    {
      title: "Allowed",
      value: isLoading ? "..." : String(data?.allowed ?? 0),
      trend: { value: "Live", tone: "positive" },
    },
    {
      title: "Active Model",
      value: "XGBoost v1.0.4",
      description: "Last Update: 2h ago",
      variant: "model",
    },
  ];

  if (error) {
    return (
      <div className="text-red-500">
        Failed to load dashboard summary.
      </div>
    );
  }

  return (
    <div className="space-y-lg">
      {/* KPI grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-md">
        {kpis.map((k) => (
          <KPICard key={k.title} {...k} />
        ))}
      </div>

      {/* Visual analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-lg">
        <FraudTrendChart />
        <DecisionPieChart />
      </div>

      {/* Predictions + live logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-lg">
        <PredictionTable
          data={predictionLoading ? [] : predictions}
        />
        <LiveLogs logs={logs} />
      </div>
    </div>
  );
}
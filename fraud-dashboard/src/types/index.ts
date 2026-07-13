import type { LucideIcon } from "lucide-react";

/** Model decision rendered in the predictions table / badges. */
export type Decision = "ALLOW" | "REVIEW" | "BLOCK";

export interface NavItem {
  icon: LucideIcon;
  label: string;
  active?: boolean;
  href?: string;
}

export interface KpiTrend {
  value: string;
  direction?: "up" | "down" | "neutral";
  tone?: "positive" | "negative" | "neutral";
}

export interface KpiMetric {
  title: string;
  value: string;
  trend?: KpiTrend;
  description?: string;
  icon?: LucideIcon;
  /** Visual accent variant for the card surface. */
  variant?: "default" | "danger" | "model";
}

export interface Prediction {
  id: string;
  user: string;
  /** Risk probability in the range 0..1. */
  probability: number;
  decision: Decision;
  time?: string;
}

export type LogLevel = "info" | "success" | "warning" | "alert" | "muted";

export interface LogEntry {
  id: string;
  time: string;
  message: string;
  level: LogLevel;
  detail?: string;
}

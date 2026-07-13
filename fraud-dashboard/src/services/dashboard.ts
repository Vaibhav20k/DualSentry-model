import api from "./api";

export interface DashboardSummary {
  totalTransactions: number;
  fraudulent: number;
  review: number;
  allowed: number;
  fraudRate: number;
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await api.get("/dashboard/summary");
  return response.data;
}
import { useQuery } from "@tanstack/react-query";
import { getDashboardSummary } from "../services/dashboard";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: getDashboardSummary,
    refetchInterval: 5000,
  });
}
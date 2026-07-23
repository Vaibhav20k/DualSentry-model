import { useQuery } from "@tanstack/react-query";
import { getDashboardSummary } from "../services/dashboard";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: getDashboardSummary,
    staleTime: 5000,
    refetchOnWindowFocus: false,
    retry: 2,
  });
}
import { useQuery } from "@tanstack/react-query";
import { getFraudTrend } from "../services/trends.ts";

export function useTrend() {
  return useQuery({
    queryKey: ["fraudTrend"],
    queryFn: getFraudTrend,
    refetchInterval: 5000,
  });
}
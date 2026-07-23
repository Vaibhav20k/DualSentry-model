import { useQuery } from "@tanstack/react-query";
import { getPredictions } from "../services/predictions";

export function usePredictions() {
  return useQuery({
    queryKey: ["predictions"],
    queryFn: getPredictions,
    refetchInterval: 5000,
    staleTime: 5000
  });
}
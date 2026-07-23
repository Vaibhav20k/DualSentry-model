import { useMemo } from "react";
import { usePredictions } from "./usePredictions";
import type { Prediction } from "../services/predictions";

export function useDecisionStats() {
  const { data = [], ...rest } = usePredictions();

  const stats = useMemo(() => {
    let allow = 0;
    let review = 0;
    let block = 0;

    data.forEach((p: Prediction) => {
      switch (p.decision) {
        case "ALLOW":
          allow++;
          break;
        case "REVIEW":
          review++;
          break;
        case "BLOCK":
          block++;
          break;
      }
    });

    const total = allow + review + block;

    return {
      allow,
      review,
      block,
      total,
      allowPercent: total ? (allow / total) * 100 : 0,
      reviewPercent: total ? (review / total) * 100 : 0,
      blockPercent: total ? (block / total) * 100 : 0,
    };
  }, [data]);

  return {
    stats,
    ...rest,
  };
}
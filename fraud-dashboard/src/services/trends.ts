import api from "./api";

export interface TrendPoint {
  time: string;
  count: number;
}

export const getFraudTrend = async (): Promise<TrendPoint[]> => {
  const { data } = await api.get("/dashboard/trend");
  return data;
};
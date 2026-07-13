import api from "./api";

export interface Prediction {
  transactionID: string;
  userID: string;
  fraudProbability: number;
  prediction: boolean;
  decision: string;
  threshold: number;
  modelVersion: string;
}

export async function getPredictions(): Promise<Prediction[]> {
  const response = await api.get("/predictions");
  return response.data;
}
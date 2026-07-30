# Section 4: Modeling & Benchmark Roadmap

## Modeling Strategy
1. **Unsupervised Baseline**: Isolation Forest trained on clean/normal transactions.
2. **Supervised Model**: XGBoost / LightGBM with scale_pos_weight tuning for high class imbalance.
3. **Threshold Calibration**: Precision-Recall curve tuning to maximize detection rate while bounding operational investigation cost.

/**
 * Phase 2 — k6 Load Test: Dashboard APIs (read-only)
 * Targets:
 *   GET /api/predictions          (paginated DB read)
 *   GET /api/dashboard/summary    (aggregation query)
 *   GET /api/dashboard/trend      (time-series query)
 *
 * Loads: 10, 25, 50, 100 VUs for 30s each
 * Includes X-Forwarded-For IP rotation for multi-client concurrency.
 */
import http from "k6/http";
import { check, group, sleep } from "k6";
import { Trend, Rate, Counter } from "k6/metrics";

const BASE_URL = "http://localhost:8080";

const trendPredictions = new Trend("latency_predictions_ms", true);
const trendSummary     = new Trend("latency_summary_ms",     true);
const trendTrend       = new Trend("latency_trend_ms",       true);
const errorRate        = new Rate("api_errors");
const requestCount     = new Counter("api_requests_total");

export const options = {
  scenarios: {
    load_10: {
      executor: "constant-vus",
      vus: 10,
      duration: "30s",
      startTime: "0s",
      gracefulStop: "5s",
      tags: { load: "10vu" },
    },
    load_25: {
      executor: "constant-vus",
      vus: 25,
      duration: "30s",
      startTime: "40s",
      gracefulStop: "5s",
      tags: { load: "25vu" },
    },
    load_50: {
      executor: "constant-vus",
      vus: 50,
      duration: "30s",
      startTime: "85s",
      gracefulStop: "5s",
      tags: { load: "50vu" },
    },
    load_100: {
      executor: "constant-vus",
      vus: 100,
      duration: "30s",
      startTime: "130s",
      gracefulStop: "5s",
      tags: { load: "100vu" },
    },
  },
  thresholds: {},
};

export default function () {
  const clientIp = `10.${__VU}.${__ITER % 250}.${Math.floor(Math.random() * 250)}`;
  const params = {
    headers: { "X-Forwarded-For": clientIp },
    timeout: "10s",
  };

  group("predictions", () => {
    const res = http.get(`${BASE_URL}/api/predictions?limit=20&page=1`, params);
    const ok = check(res, { "predictions 200": (r) => r.status === 200 });
    trendPredictions.add(res.timings.duration);
    errorRate.add(!ok);
    requestCount.add(1);
  });

  sleep(0.05);

  group("summary", () => {
    const res = http.get(`${BASE_URL}/api/dashboard/summary`, params);
    const ok = check(res, { "summary 200": (r) => r.status === 200 });
    trendSummary.add(res.timings.duration);
    errorRate.add(!ok);
    requestCount.add(1);
  });

  sleep(0.05);

  group("trend", () => {
    const res = http.get(`${BASE_URL}/api/dashboard/trend`, params);
    const ok = check(res, { "trend 200": (r) => r.status === 200 });
    trendTrend.add(res.timings.duration);
    errorRate.add(!ok);
    requestCount.add(1);
  });

  sleep(0.1);
}

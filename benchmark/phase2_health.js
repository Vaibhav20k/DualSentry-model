/**
 * Phase 2 — k6 Load Test: Gateway Health Endpoint
 * Target: GET /health
 * Loads: 10, 25, 50, 100 VUs for 30s each
 * Includes X-Forwarded-For IP rotation to benchmark concurrent throughput beyond single-IP 100 req/min bucket.
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate, Counter } from "k6/metrics";

const BASE_URL = "http://localhost:8080";

const latency   = new Trend("health_latency_ms", true);
const errorRate = new Rate("health_errors");
const requests  = new Counter("health_requests_total");

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
  thresholds: {
    health_latency_ms: ["p(95)<200", "p(99)<500"],
    health_errors: ["rate<0.05"],
  },
};

export default function () {
  const clientIp = `10.${__VU}.${__ITER % 250}.${Math.floor(Math.random() * 250)}`;

  const res = http.get(`${BASE_URL}/health`, {
    headers: {
      "X-Forwarded-For": clientIp,
    },
    timeout: "5s",
  });

  const ok = check(res, {
    "status 200": (r) => r.status === 200,
  });

  latency.add(res.timings.duration);
  errorRate.add(!ok);
  requests.add(1);

  sleep(0.01);
}

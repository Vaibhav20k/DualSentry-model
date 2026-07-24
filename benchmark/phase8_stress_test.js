/**
 * Phase 8 — Stress Test
 * Progressive load: 25 → 50 → 100 → 250 → 500 VUs
 * Targets: POST /api/transactions (full pipeline)
 * Measures throughput, latency, and error rate at each level.
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate, Counter } from "k6/metrics";

const BASE_URL = "http://localhost:8080";

const latency   = new Trend("txn_latency_ms", true);
const errorRate = new Rate("txn_errors");
const reqCount  = new Counter("txn_requests_total");

const PAYMENT_METHODS = ["UPI", "CARD", "NET_BANKING", "WALLET"];
const LOCATIONS = ["US-NY", "US-CA", "IN-MH", "IN-DL", "GB-LON"];
const MERCHANTS = ["Amazon", "Flipkart", "Walmart", "Target", "BestBuy", "Uber", "Airbnb", "Stripe"];

export const options = {
  scenarios: {
    stress_25: {
      executor: "constant-vus",
      vus: 25,
      duration: "30s",
      startTime: "0s",
      gracefulStop: "5s",
      tags: { load: "25vu" },
    },
    stress_50: {
      executor: "constant-vus",
      vus: 50,
      duration: "30s",
      startTime: "80s",
      gracefulStop: "5s",
      tags: { load: "50vu" },
    },
    stress_100: {
      executor: "constant-vus",
      vus: 100,
      duration: "30s",
      startTime: "120s",
      gracefulStop: "5s",
      tags: { load: "100vu" },
    },
    stress_250: {
      executor: "constant-vus",
      vus: 250,
      duration: "30s",
      startTime: "160s",
      gracefulStop: "5s",
      tags: { load: "250vu" },
    },
    stress_500: {
      executor: "constant-vus",
      vus: 500,
      duration: "30s",
      startTime: "200s",
      gracefulStop: "10s",
      tags: { load: "500vu" },
    },
  },
};

function randomUUID() {
  const hex = "0123456789abcdef";
  let uuid = "";
  for (let i = 0; i < 36; i++) {
    if (i === 8 || i === 13 || i === 18 || i === 23) {
      uuid += "-";
    } else {
      uuid += hex[Math.floor(Math.random() * 16)];
    }
  }
  uuid = uuid.substring(0, 14) + "4" + uuid.substring(15);
  uuid = uuid.substring(0, 19) + "8" + uuid.substring(20);
  return uuid;
}

function generatePayload() {
  return JSON.stringify({
    user_id: randomUUID(),
    amount: parseFloat((Math.random() * 1500 + 10).toFixed(2)),
    currency: "INR",
    payment_method: PAYMENT_METHODS[Math.floor(Math.random() * PAYMENT_METHODS.length)],
    payment_identifier: `txn_${Math.floor(Math.random() * 999999)}`,
    merchant: MERCHANTS[Math.floor(Math.random() * MERCHANTS.length)],
    merchant_category: "RETAIL",
    receiver_account: randomUUID(),
    location: LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)],
    ip_address: `${10 + Math.floor(Math.random() * 240)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${1 + Math.floor(Math.random() * 254)}`,
    device_id: `DEV-${Math.floor(Math.random() * 1000)}`,
    timestamp: new Date().toISOString(),
  });
}

export default function () {
  const clientIp = `10.${__VU % 250}.${__ITER % 250}.${Math.floor(Math.random() * 250)}`;

  const payload = generatePayload();
  const params = {
    headers: {
      "Content-Type": "application/json",
      "X-Forwarded-For": clientIp,
    },
    timeout: "30s",
  };

  const res = http.post(`${BASE_URL}/api/transactions`, payload, params);

  const ok = check(res, {
    "status 200 or 201": (r) => r.status === 200 || r.status === 201,
    "status not 500": (r) => r.status !== 500,
  });

  latency.add(res.timings.duration);
  errorRate.add(!ok);
  reqCount.add(1);

  sleep(0.02);
}

/**
 * Phase 2 — k6 Load Test: Full Ingestion Pipeline
 * Target: POST /api/transactions
 *
 * Schema constraints (from PostgreSQL):
 *   - user_id: UUID
 *   - payment_method: UPI | CARD | NET_BANKING | WALLET
 *   - amount: numeric(12,2), > 0
 *   - ip_address: inet
 *
 * Loads: 10, 25, 50, 100 VUs for 30s each
 * Includes X-Forwarded-For header rotation for multi-client concurrency.
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
    txn_latency_ms: ["p(95)<3000", "p(99)<5000"],
    txn_errors: ["rate<0.05"],
  },
};

function randomUUID() {
  // Generate valid v4 UUID
  const hex = "0123456789abcdef";
  let uuid = "";
  for (let i = 0; i < 36; i++) {
    if (i === 8 || i === 13 || i === 18 || i === 23) {
      uuid += "-";
    } else {
      uuid += hex[Math.floor(Math.random() * 16)];
    }
  }
  // Set version 4 and variant bits
  uuid = uuid.substring(0, 14) + "4" + uuid.substring(15);
  uuid = uuid.substring(0, 19) + "8" + uuid.substring(20);
  return uuid;
}

function generateTransaction(id) {
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
  // Rotate IP in header so each VU simulates a different client
  const clientIp = `192.168.${__VU % 250}.${__ITER % 250}`;

  const payload = generateTransaction(__VU * 100000 + __ITER);
  const params = {
    headers: {
      "Content-Type": "application/json",
      "X-Forwarded-For": clientIp,
    },
    timeout: "10s",
  };

  const res = http.post(`${BASE_URL}/api/transactions`, payload, params);

  const ok = check(res, {
    "status 200 or 201": (r) => r.status === 200 || r.status === 201,
  });

  latency.add(res.timings.duration);
  errorRate.add(!ok);
  reqCount.add(1);

  sleep(0.02);
}

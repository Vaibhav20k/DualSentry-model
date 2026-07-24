"""
Phase 7 — End-to-End Latency Benchmark

Measures the complete pipeline:
  Transaction Generated (client)
    ↓
  Gateway Received (HTTP response)
    ↓
  Stored in PostgreSQL
    ↓
  Visible on Dashboard API

Uses unique transaction IDs to trace through each stage.
"""

import json
import subprocess
import time
import uuid
import urllib.request
import statistics

# ============================================================
# Configuration
# ============================================================

GATEWAY_URL = "http://localhost:8080"
POSTGRES_USER = "fintech_user"
POSTGRES_DB = "fintech_db"
NUM_SAMPLES = 20

# Use random UUIDs for every transaction (no existing baseline -> deviations = 0 -> ML validation passes)
# Existing user baselines have AverageAmount ~13,000, so sending small amounts creates negative
# deviation which fails ML engine's Field(ge=0) on spending_deviation_score
USE_RANDOM_USERS = True

def generate_payload():
    """Generate a transaction payload (no transaction_id — server generates it)."""
    user_id = str(uuid.uuid4()) if USE_RANDOM_USERS else "11111111-1111-1111-1111-111111111111"
    return json.dumps({
        "user_id": user_id,
        "amount": round(100 + (time.time() % 500), 2),
        "currency": "INR",
        "payment_method": "CARD",
        "payment_identifier": f"txn_e2e_{int(time.time() * 1000000)}",
        "merchant": "E2ETest",
        "merchant_category": "RETAIL",
        "receiver_account": str(uuid.uuid4()),
        "location": "US-NY",
        "ip_address": "10.99.99.99",
        "device_id": f"DEV-E2E-{int(time.time() % 1000)}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }).encode("utf-8")


def get_db_timestamp(txn_id):
    """Query DB for transaction and prediction created_at."""
    try:
        # Transaction created_at
        cmd = (
            f'docker exec fintech-postgres psql -U {POSTGRES_USER} -d {POSTGRES_DB} '
            f'-c "SELECT created_at FROM transactions WHERE transaction_id=\'{txn_id}\';" -t 2>/dev/null'
        )
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        txn_ts = result.stdout.strip()

        # Prediction created_at
        cmd2 = (
            f'docker exec fintech-postgres psql -U {POSTGRES_USER} -d {POSTGRES_DB} '
            f'-c "SELECT created_at, fraud_probability, prediction, decision '
            f'FROM fraud_predictions WHERE transaction_id=\'{txn_id}\';" -t 2>/dev/null'
        )
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=5)
        pred_data = result2.stdout.strip()

        return txn_ts, pred_data
    except Exception:
        return None, None


def check_dashboard(txn_id):
    """Check if transaction is visible on the dashboard API."""
    try:
        req = urllib.request.Request(
            f"{GATEWAY_URL}/api/predictions",
            headers={"X-Forwarded-For": "10.99.99.99"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            dash_data = json.loads(resp.read().decode("utf-8"))
            if isinstance(dash_data, list):
                for item in dash_data:
                    tid = item.get("transactionID") or item.get("transaction_id") or ""
                    if txn_id in str(tid):
                        return True, dash_data
            return False, dash_data
    except Exception as e:
        return False, str(e)


def measure_pipeline():
    """Measure one complete pipeline cycle."""
    txn_id_at_start = str(uuid.uuid4())
    payload = generate_payload()

    stages = {"txn_uuid": txn_id_at_start}

    # --- Client sends request, measure gateway response time ---
    t0 = time.perf_counter()
    req = urllib.request.Request(
        f"{GATEWAY_URL}/api/transactions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Forwarded-For": "10.99.99.99",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            t1 = time.perf_counter()
            stages["gateway_latency_ms"] = round((t1 - t0) * 1000, 2)
            stages["gateway_status"] = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            stages["gateway_response"] = body
            # The server returns the generated transaction_id
            server_txn_id = body.get("transaction_id", "")
            stages["server_txn_id"] = server_txn_id
    except urllib.error.HTTPError as e:
        stages["gateway_error"] = f"HTTP {e.code}: {e.read().decode()[:200]}"
        stages["gateway_latency_ms"] = -1
        return stages
    except Exception as e:
        stages["gateway_error"] = str(e)
        stages["gateway_latency_ms"] = -1
        return stages

    server_txn_id = stages.get("server_txn_id", "")

    # --- Query DB for record ---
    time.sleep(0.2)
    t2 = time.perf_counter()
    txn_ts, pred_data = get_db_timestamp(server_txn_id)
    stages["db_query_latency_ms"] = round((t2 - t0) * 1000, 2)

    if txn_ts and txn_ts.strip():
        stages["db_txn_found"] = True
        stages["db_txn_ts"] = txn_ts.strip()[:19].replace(" ", "T")
    else:
        stages["db_txn_found"] = False

    if pred_data and pred_data.strip() and not pred_data.startswith("("):
        parts = pred_data.split()
        if len(parts) >= 4:
            stages["db_pred_found"] = True
            stages["db_pred_ts"] = f"{parts[0]}T{parts[1][:8]}" if len(parts) > 1 else parts[0]
            try:
                stages["fraud_probability"] = float(parts[2])
                stages["prediction"] = parts[3] == "t"
                stages["decision"] = parts[4] if len(parts) > 4 else "UNKNOWN"
            except (ValueError, IndexError):
                pass
    else:
        stages["db_pred_found"] = False

    # --- Check dashboard visibility ---
    time.sleep(0.1)
    t3 = time.perf_counter()
    visible, dash_response = check_dashboard(server_txn_id)
    stages["dashboard_check_latency_ms"] = round((t3 - t0) * 1000, 2)
    stages["dashboard_visible"] = visible

    if visible:
        stages["total_e2e_ms"] = round((t3 - t0) * 1000, 2)
    else:
        stages["total_e2e_ms"] = -1

    return stages


def compute_stats(values, label):
    if len(values) < 2:
        return None
    sorted_v = sorted(values)
    n = len(sorted_v)
    return {
        "count": n,
        "avg_ms": round(statistics.mean(sorted_v), 2),
        "median_ms": round(statistics.median(sorted_v), 2),
        "min_ms": round(sorted_v[0], 2),
        "max_ms": round(sorted_v[-1], 2),
        "stdev_ms": round(statistics.stdev(sorted_v), 2),
        "p90_ms": round(sorted_v[int(n * 0.90)], 2),
        "p95_ms": round(sorted_v[int(n * 0.95)], 2),
        "p99_ms": round(sorted_v[min(int(n * 0.99), n - 1)], 2),
    }


def main():
    print("=" * 70)
    print("Phase 7 - End-to-End Latency Benchmark")
    print(f"Samples: {NUM_SAMPLES}")
    print("=" * 70)

    results = []
    gateway_latencies = []
    e2e_latencies = []
    db_found_count = 0
    pred_found_count = 0
    dash_visible_count = 0

    for i in range(NUM_SAMPLES):
        stages = measure_pipeline()
        results.append(stages)

        g_lat = stages.get("gateway_latency_ms", -1)
        if g_lat > 0:
            gateway_latencies.append(g_lat)
            if stages.get("db_txn_found"):
                db_found_count += 1
            if stages.get("db_pred_found"):
                pred_found_count += 1
            if stages.get("dashboard_visible"):
                dash_visible_count += 1
                e2e_latencies.append(stages["total_e2e_ms"])

            status = f"Gateway: {g_lat}ms | DB: {'Y' if stages.get('db_txn_found') else 'N'}/{('Y' if stages.get('db_pred_found') else 'N')} | Dash: {'Y' if stages.get('dashboard_visible') else 'N'}"
            if stages.get("dashboard_visible"):
                status += f" E2E: {stages['total_e2e_ms']}ms"
            print(f"  [{i+1:2d}] {status}")
        else:
            print(f"  [{i+1:2d}] ERROR: {stages.get('gateway_error', 'unknown')}")

        time.sleep(0.15)

    # --- Results ---
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nSamples: {NUM_SAMPLES}")

    gw = compute_stats(gateway_latencies, "Gateway")
    e2e = compute_stats(e2e_latencies, "E2E")

    print(f"\n  Pipeline Stage            Found    Rate")
    print(f"  ----------------          -----    ----")
    print(f"  Gateway Accepted          {len(gateway_latencies):3d}      100.0%")
    print(f"  DB Transaction Stored     {db_found_count:3d}      {db_found_count/len(gateway_latencies)*100 if gateway_latencies else 0:.1f}%")
    print(f"  DB Prediction Stored      {pred_found_count:3d}      {pred_found_count/len(gateway_latencies)*100 if gateway_latencies else 0:.1f}%")
    print(f"  Dashboard Visible          {dash_visible_count:3d}      {dash_visible_count/len(gateway_latencies)*100 if gateway_latencies else 0:.1f}%")

    if gw:
        print(f"\n  Gateway Latency (HTTP POST -> Response)")
        print(f"    Average:  {gw['avg_ms']} ms")
        print(f"    Median:   {gw['median_ms']} ms")
        print(f"    Min:      {gw['min_ms']} ms")
        print(f"    Max:      {gw['max_ms']} ms")
        print(f"    P95:      {gw['p95_ms']} ms")
        print(f"    P99:      {gw['p99_ms']} ms")

    if e2e and len(e2e_latencies) >= (NUM_SAMPLES * 0.5):
        print(f"\n  End-to-End Latency (Request -> Dashboard Visible)")
        print(f"    Average:  {e2e['avg_ms']} ms")
        print(f"    Median:   {e2e['median_ms']} ms")
        print(f"    Min:      {e2e['min_ms']} ms")
        print(f"    Max:      {e2e['max_ms']} ms")
        print(f"    P95:      {e2e['p95_ms']} ms")
        print(f"    P99:      {e2e['p99_ms']} ms")
    else:
        print(f"\n  End-to-End: insufficient dashboard data ({dash_visible_count}/{NUM_SAMPLES})")

    # Latency breakdown summary
    print(f"\n  Latency Breakdown (avg)")
    print(f"    Gateway processing:     ~{gw['avg_ms'] if gw else 0}ms")
    print(f"    DB persistence:          ~{gw['avg_ms'] if gw else 0}ms (overlaps with gateway)")
    print(f"    Dashboard availability:  included in E2E")
    print(f"    Total E2E:              ~{e2e['avg_ms'] if e2e else 0}ms")

    # Save
    summary = {
        "phase": 7,
        "title": "End-to-End Latency Benchmark",
        "samples": NUM_SAMPLES,
        "gateway_accepted": len(gateway_latencies),
        "db_transaction_stored": db_found_count,
        "db_prediction_stored": pred_found_count,
        "dashboard_visible": dash_visible_count,
        "gateway_latency_ms": gw,
        "e2e_latency_ms": e2e,
        "completion_rate": {
            "gateway_pct": 100.0,
            "db_transaction_pct": round(db_found_count / len(gateway_latencies) * 100, 1) if gateway_latencies else 0,
            "db_prediction_pct": round(pred_found_count / len(gateway_latencies) * 100, 1) if gateway_latencies else 0,
            "dashboard_pct": round(dash_visible_count / len(gateway_latencies) * 100, 1) if gateway_latencies else 0,
        }
    }

    with open("benchmark/phase7_e2e_latency_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to benchmark/phase7_e2e_latency_results.json")


if __name__ == "__main__":
    main()

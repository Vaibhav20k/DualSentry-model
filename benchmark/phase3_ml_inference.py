"""
Phase 3 — ML Inference Benchmark
Target: POST http://localhost:8000/predict
Measures: 2000 predictions with detailed latency statistics.
"""

import json
import time
import statistics
import urllib.request
import urllib.error
import random

# ============================================================
# Configuration
# ============================================================

ML_URL = "http://localhost:8000/predict"
NUM_REQUESTS = 2000
WARMUP_REQUESTS = 50

PAYMENT_CHANNELS = ["CARD", "UPI", "NET_BANKING", "WALLET"]

def generate_payload():
    """Generate a realistic prediction request payload."""
    return {
        "amount": round(random.uniform(10, 5000), 2),
        "payment_channel": random.choice(PAYMENT_CHANNELS),
        "time_since_last_transaction": round(random.uniform(0, 86400), 2),
        "velocity_score": round(random.uniform(0, 100), 2),
        "spending_deviation_score": round(random.uniform(0, 50), 2),
        "is_first_transaction": random.choice([0, 1]),
        "hour": random.randint(0, 23),
        "day_of_week": random.randint(0, 6),
        "month": random.randint(1, 12),
        "is_weekend": random.choice([0, 1]),
        "is_cross_bank_transfer": random.choice([0, 1]),
        "is_cross_currency_transfer": random.choice([0, 1]),
        "is_new_receiver": random.choice([0, 1]),
        "is_new_bank": random.choice([0, 1]),
        "is_new_payment_format": random.choice([0, 1]),
    }

def send_prediction(payload):
    """Send a single prediction request and return (latency_ms, success, response)."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ML_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            latency_ms = (time.perf_counter() - start) * 1000
            return latency_ms, True, json.loads(body)
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return latency_ms, False, str(e)

def compute_stats(latencies):
    """Compute comprehensive latency statistics."""
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    return {
        "count": n,
        "avg_ms": round(statistics.mean(sorted_lat), 2),
        "median_ms": round(statistics.median(sorted_lat), 2),
        "min_ms": round(sorted_lat[0], 2),
        "max_ms": round(sorted_lat[-1], 2),
        "stdev_ms": round(statistics.stdev(sorted_lat), 2) if n > 1 else 0,
        "p50_ms": round(sorted_lat[int(n * 0.50)], 2),
        "p90_ms": round(sorted_lat[int(n * 0.90)], 2),
        "p95_ms": round(sorted_lat[int(n * 0.95)], 2),
        "p99_ms": round(sorted_lat[int(n * 0.99)], 2),
        "p999_ms": round(sorted_lat[min(int(n * 0.999), n - 1)], 2),
    }

# ============================================================
# Main Benchmark
# ============================================================

def main():
    print("=" * 60)
    print("Phase 3 — ML Inference Benchmark")
    print(f"Target: {ML_URL}")
    print(f"Requests: {NUM_REQUESTS} (+ {WARMUP_REQUESTS} warmup)")
    print("=" * 60)

    # --- Warmup ---
    print(f"\n[1/3] Warmup ({WARMUP_REQUESTS} requests)...")
    for i in range(WARMUP_REQUESTS):
        payload = generate_payload()
        send_prediction(payload)
        if (i + 1) % 10 == 0:
            print(f"  Warmup: {i + 1}/{WARMUP_REQUESTS}")
    print("  Warmup complete.")

    # --- Benchmark ---
    print(f"\n[2/3] Benchmark ({NUM_REQUESTS} requests)...")
    latencies = []
    successes = 0
    failures = 0
    fraud_count = 0
    non_fraud_count = 0
    error_messages = []

    wall_start = time.perf_counter()

    for i in range(NUM_REQUESTS):
        payload = generate_payload()
        latency_ms, success, resp = send_prediction(payload)
        latencies.append(latency_ms)

        if success:
            successes += 1
            if resp.get("prediction"):
                fraud_count += 1
            else:
                non_fraud_count += 1
        else:
            failures += 1
            error_messages.append(resp)

        if (i + 1) % 500 == 0:
            current_avg = statistics.mean(latencies)
            print(f"  Progress: {i + 1}/{NUM_REQUESTS} | Avg: {current_avg:.2f}ms | Errors: {failures}")

    wall_elapsed = time.perf_counter() - wall_start

    # --- Results ---
    print(f"\n[3/3] Computing results...")
    stats = compute_stats(latencies)
    throughput = NUM_REQUESTS / wall_elapsed

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"  Total Requests:    {stats['count']}")
    print(f"  Successes:         {successes}")
    print(f"  Failures:          {failures}")
    print(f"  Fraud Predictions: {fraud_count}")
    print(f"  Non-Fraud:         {non_fraud_count}")
    print(f"  Wall Time:         {wall_elapsed:.2f}s")
    print()
    print("  Latency Statistics:")
    print(f"    Average:         {stats['avg_ms']} ms")
    print(f"    Median (P50):    {stats['median_ms']} ms")
    print(f"    Min:             {stats['min_ms']} ms")
    print(f"    Max:             {stats['max_ms']} ms")
    print(f"    Std Dev:         {stats['stdev_ms']} ms")
    print(f"    P90:             {stats['p90_ms']} ms")
    print(f"    P95:             {stats['p95_ms']} ms")
    print(f"    P99:             {stats['p99_ms']} ms")
    print(f"    P99.9:           {stats['p999_ms']} ms")
    print()
    print(f"  Throughput:        {throughput:.2f} predictions/sec")
    print("=" * 60)

    if failures > 0:
        print(f"\n  Errors ({failures}):")
        unique_errors = list(set(error_messages))[:5]
        for err in unique_errors:
            print(f"    - {err}")

    # --- Save results ---
    results = {
        "phase": 3,
        "title": "ML Inference Benchmark",
        "endpoint": ML_URL,
        "total_requests": NUM_REQUESTS,
        "warmup_requests": WARMUP_REQUESTS,
        "wall_time_seconds": round(wall_elapsed, 2),
        "successes": successes,
        "failures": failures,
        "fraud_count": fraud_count,
        "non_fraud_count": non_fraud_count,
        "throughput_per_sec": round(throughput, 2),
        "latency": stats,
    }

    output_path = "benchmark/phase3_ml_inference_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import multiprocessing
import random
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from excel_data_envs.environment import ExcelDataEnvironment


def _random_session_id() -> str:
    return "test-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


def _run_actions_in_session(session_id: str, scenario_id: str, action_count: int) -> dict:
    env = ExcelDataEnvironment()
    try:
        env.create_session(session_id, scenario_id)
        
        result = env.list_raw_datasets(session_id)
        if result["data"].get("success") is False:
            return {"session_id": session_id, "error": "list_raw_datasets failed"}
        
        env.deduplicate(session_id, "sales_raw", "transaction_id")
        env.fill_missing(session_id, "sales_raw")
        env.create_pivot_category_region(session_id)
        env.create_pivot_salesperson(session_id)
        env.create_pivot_city(session_id)
        env.create_bar_chart(session_id, "chart1", "Sales by Category", "category", "sales_amount")
        env.create_pie_chart(session_id, "chart2", "Sales by Region", "region", "sales_amount")
        env.create_total_revenue(session_id)
        env.create_average_order_value(session_id)
        env.create_total_transactions(session_id)
        
        summary = env.session_summary(session_id)
        evaluation = env.evaluate_session(session_id)
        
        return {
            "session_id": session_id,
            "action_count": len(summary.get("actions", [])),
            "pivot_count": summary.get("pivot_count", 0),
            "chart_count": summary.get("chart_count", 0),
            "formula_count": summary.get("formula_count", 0),
            "overall_score": evaluation.get("overall_score", 0.0),
        }
    except Exception as exc:
        return {"session_id": session_id, "error": str(exc)}


def test_session_isolation() -> dict:
    print("=" * 60)
    print("TEST: Session Isolation")
    print("=" * 60)
    
    scenario_id = "sales_data_processing"
    session1_id = _random_session_id()
    session2_id = _random_session_id()
    
    print(f"Creating session 1: {session1_id}")
    print(f"Creating session 2: {session2_id}")
    
    env = ExcelDataEnvironment()
    env.create_session(session1_id, scenario_id)
    env.create_session(session2_id, scenario_id)
    
    env.deduplicate(session1_id, "sales_raw", "transaction_id")
    env.deduplicate(session2_id, "sales_raw", "transaction_id")
    env.fill_missing(session1_id, "sales_raw")
    env.create_pivot_category_region(session1_id)
    
    session1_data = env.session_summary(session1_id)
    session2_data = env.session_summary(session2_id)
    
    session1_pivots = session1_data.get("pivot_count", 0)
    session2_pivots = session2_data.get("pivot_count", 0)
    
    print(f"\nSession 1 pivots: {session1_pivots}")
    print(f"Session 2 pivots: {session2_pivots}")
    
    isolation_ok = session1_pivots == 1 and session2_pivots == 0
    
    print(f"\nIsolation test: {'PASS' if isolation_ok else 'FAIL'}")
    
    return {
        "test": "session_isolation",
        "passed": isolation_ok,
        "details": {
            "session1_pivots": session1_pivots,
            "session2_pivots": session2_pivots,
        }
    }


def test_concurrent_sessions() -> dict:
    print("\n" + "=" * 60)
    print("TEST: Concurrent Sessions")
    print("=" * 60)
    
    scenario_id = "sales_data_processing"
    num_sessions = 5
    sessions = [_random_session_id() for _ in range(num_sessions)]
    
    print(f"Creating {num_sessions} sessions concurrently...")
    
    def create_and_process(session_id: str) -> dict:
        return _run_actions_in_session(session_id, scenario_id, 10)
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = {executor.submit(create_and_process, sid): sid for sid in sessions}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"  Completed: {result.get('session_id', 'unknown')}")
    
    elapsed = time.time() - start_time
    
    successful = sum(1 for r in results if "error" not in r)
    pivot_counts = [r.get("pivot_count", 0) for r in results]
    chart_counts = [r.get("chart_count", 0) for r in results]
    
    print(f"\nTotal time: {elapsed:.2f}s")
    print(f"Successful sessions: {successful}/{num_sessions}")
    print(f"Min pivots: {min(pivot_counts)}, Max pivots: {max(pivot_counts)}")
    print(f"Min charts: {min(chart_counts)}, Max charts: {max(chart_counts)}")
    
    concurrent_ok = successful == num_sessions and all(p >= 3 for p in pivot_counts) and all(c >= 2 for c in chart_counts)
    
    print(f"\nConcurrent test: {'PASS' if concurrent_ok else 'FAIL'}")
    
    return {
        "test": "concurrent_sessions",
        "passed": concurrent_ok,
        "details": {
            "num_sessions": num_sessions,
            "successful": successful,
            "pivot_counts": pivot_counts,
            "chart_counts": chart_counts,
            "elapsed_seconds": elapsed,
        }
    }


def test_lock_contention() -> dict:
    print("\n" + "=" * 60)
    print("TEST: Lock Contention")
    print("=" * 60)
    
    scenario_id = "sales_data_processing"
    session_id = _random_session_id()
    
    print(f"Creating session: {session_id}")
    env = ExcelDataEnvironment()
    env.create_session(session_id, scenario_id)
    
    num_threads = 3
    actions_per_thread = 5
    
    def rapid_fire_actions(thread_id: int) -> dict:
        thread_env = ExcelDataEnvironment()
        results = []
        for i in range(actions_per_thread):
            try:
                if i % 3 == 0:
                    result = thread_env.list_raw_datasets(session_id)
                elif i % 3 == 1:
                    result = thread_env.deduplicate(session_id, "sales_raw", "transaction_id")
                else:
                    result = thread_env.create_pivot_salesperson(session_id)
                results.append({"thread": thread_id, "action": i, "success": True})
            except Exception as exc:
                results.append({"thread": thread_id, "action": i, "success": False, "error": str(exc)})
        return results
    
    print(f"Running {num_threads} threads with {actions_per_thread} actions each...")
    
    all_results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(rapid_fire_actions, i) for i in range(num_threads)]
        for future in as_completed(futures):
            all_results.extend(future.result())
    
    elapsed = time.time() - start_time
    
    successful = sum(1 for r in all_results if r.get("success", False))
    total = len(all_results)
    
    print(f"\nTotal actions: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Time: {elapsed:.2f}s")
    
    lock_ok = successful == total
    
    print(f"\nLock contention test: {'PASS' if lock_ok else 'FAIL'}")
    
    return {
        "test": "lock_contention",
        "passed": lock_ok,
        "details": {
            "total_actions": total,
            "successful": successful,
            "failed": total - successful,
            "elapsed_seconds": elapsed,
        }
    }


def main() -> int:
    print("Excel Data Environment - Concurrency Test Suite")
    print("=" * 60)
    
    test_results = []
    
    test_results.append(test_session_isolation())
    test_results.append(test_concurrent_sessions())
    test_results.append(test_lock_contention())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for result in test_results:
        status = "PASS" if result["passed"] else "FAIL"
        all_passed = all_passed and result["passed"]
        print(f"  {result['test']}: {status}")
    
    print("\n" + "=" * 60)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 60)
    
    output = {
        "timestamp": time.time(),
        "results": test_results,
        "all_passed": all_passed,
    }
    
    output_file = Path(__file__).parent / "concurrency_test_results.json"
    output_file.write_text(json.dumps(output, indent=2))
    print(f"\nResults written to: {output_file}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

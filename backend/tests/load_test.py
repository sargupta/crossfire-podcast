"""
Load Testing Script for Production Deployment
Tests concurrent debate handling and system performance
"""

import asyncio
import time
import websockets
import json
from typing import List, Dict
import statistics


class LoadTester:
    """Load testing for CROSSFIRE production"""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []

    async def simulate_debate(self, debate_id: int, topic: str = None) -> Dict:
        """Simulate a single debate session"""

        start_time = time.time()
        events_received = 0
        success = False
        error_message = None

        if topic is None:
            topic = f"Load Test Topic {debate_id}"

        try:
            uri = f"{self.base_url}/api/debate/stream-production"
            async with websockets.connect(uri) as websocket:
                # Send request
                await websocket.send(json.dumps({"topic": topic, "turns": 4}))

                # Receive events
                async for message in websocket:
                    data = json.loads(message)
                    events_received += 1

                    if data.get("type") == "complete":
                        success = True
                        break

                    if data.get("type") == "error":
                        error_message = data.get("message", "Unknown error")
                        break

        except Exception as e:
            error_message = str(e)

        duration = time.time() - start_time

        return {
            "debate_id": debate_id,
            "success": success,
            "duration": duration,
            "events_received": events_received,
            "error": error_message,
        }

    async def run_load_test(
        self, concurrent_debates: int = 10, total_debates: int = None
    ):
        """
        Run load test with specified concurrency.

        Args:
            concurrent_debates: Number of concurrent debates
            total_debates: Total debates to run (default: same as concurrent)
        """

        if total_debates is None:
            total_debates = concurrent_debates

        print(f"=" * 70)
        print(f"CROSSFIRE LOAD TEST")
        print(f"=" * 70)
        print(f"Concurrent Debates: {concurrent_debates}")
        print(f"Total Debates: {total_debates}")
        print(f"Target: {self.base_url}")
        print(f"=" * 70)
        print()

        overall_start = time.time()

        # Run debates in batches
        for batch_start in range(0, total_debates, concurrent_debates):
            batch_end = min(batch_start + concurrent_debates, total_debates)
            batch_size = batch_end - batch_start

            print(
                f"Running batch {batch_start//concurrent_debates + 1}: debates {batch_start+1}-{batch_end}"
            )

            tasks = [self.simulate_debate(i) for i in range(batch_start, batch_end)]

            batch_results = await asyncio.gather(*tasks)
            self.results.extend(batch_results)

            # Show progress
            successful = sum(1 for r in batch_results if r["success"])
            print(f"  Batch complete: {successful}/{batch_size} successful\n")

        overall_duration = time.time() - overall_start

        # Print results
        self.print_results(overall_duration)

    def print_results(self, total_duration: float):
        """Print detailed test results"""

        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]

        print("\n" + "=" * 70)
        print("LOAD TEST RESULTS")
        print("=" * 70)

        print(f"\n📊 Overall Stats:")
        print(f"  Total Debates: {len(self.results)}")
        print(
            f"  Successful: {len(successful)} ({len(successful)/len(self.results)*100:.1f}%)"
        )
        print(f"  Failed: {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")
        print(f"  Total Duration: {total_duration:.2f}s")
        print(f"  Throughput: {len(self.results)/total_duration:.2f} debates/sec")

        if successful:
            durations = [r["duration"] for r in successful]
            events = [r["events_received"] for r in successful]

            print(f"\n⏱️  Performance Metrics:")
            print(f"  Average Duration: {statistics.mean(durations):.2f}s")
            print(f"  Median Duration: {statistics.median(durations):.2f}s")
            print(f"  Min Duration: {min(durations):.2f}s")
            print(f"  Max Duration: {max(durations):.2f}s")
            print(f"  Average Events/Debate: {statistics.mean(events):.1f}")

        if failed:
            print(f"\n❌ Failures:")
            error_counts = {}
            for r in failed:
                error = r["error"] or "Unknown"
                error_counts[error] = error_counts.get(error, 0) + 1

            for error, count in error_counts.items():
                print(f"  - {error}: {count} occurrences")

        print("\n" + "=" * 70)

        # Pass/fail criteria
        success_rate = len(successful) / len(self.results)
        avg_duration = (
            statistics.mean([r["duration"] for r in successful]) if successful else 0
        )

        print(f"\n✅ Success Criteria:")
        print(f"  Success Rate: {success_rate*100:.1f}% (target: >95%)")
        print(f"  Avg Duration: {avg_duration:.2f}s (target: <10s)")

        if success_rate >= 0.95 and avg_duration < 10:
            print(f"\n🎉 LOAD TEST PASSED!")
        else:
            print(f"\n⚠️  LOAD TEST NEEDS IMPROVEMENT")

        print("=" * 70)


async def main():
    """Run load test"""

    import sys

    # Configuration
    concurrent = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    total = int(sys.argv[2]) if len(sys.argv) > 2 else concurrent
    url = sys.argv[3] if len(sys.argv) > 3 else "ws://localhost:8000"

    tester = LoadTester(base_url=url)
    await tester.run_load_test(concurrent_debates=concurrent, total_debates=total)


if __name__ == "__main__":
    print("CROSSFIRE Load Testing Tool\n")
    print("Usage: python load_test.py [concurrent] [total] [url]")
    print("  concurrent: Number of concurrent debates (default: 10)")
    print("  total: Total debates to run (default: same as concurrent)")
    print("  url: WebSocket base URL (default: ws://localhost:8000)")
    print()

    asyncio.run(main())

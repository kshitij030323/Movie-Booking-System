"""
Stress Test / Performance Evaluation for Movie Booking System

Tests:
  1. Concurrent booking  - multiple clients book at the same time
  2. Response time        - average time per request
  3. Throughput           - requests handled per second
  4. Double-booking check - same seat booked by many clients simultaneously
  5. Scalability          - increasing number of clients

Usage:
  python stress_test.py
"""

import socket
import ssl
import threading
import time
import statistics

HOST = "127.0.0.1"
PORT = 6000


def create_connection():
    context = ssl._create_unverified_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure = context.wrap_socket(sock)
    secure.connect((HOST, PORT))
    return secure


def send_command(conn, cmd):
    conn.send(cmd.encode())
    return conn.recv(1024).decode()


# ──────────────────────────────────────────────
# Test 1: Double Booking Prevention
# ──────────────────────────────────────────────
def test_double_booking():
    print("\n" + "=" * 50)
    print("TEST 1: Double Booking Prevention")
    print("=" * 50)
    print("10 clients try to book Seat 1 at the same time...")

    results = []
    barrier = threading.Barrier(10)

    def try_book(client_id):
        conn = create_connection()
        barrier.wait()  # all clients fire at once
        resp = send_command(conn, f"BOOK 1 Client{client_id}")
        results.append(resp.strip())
        send_command(conn, "EXIT")
        conn.close()

    threads = [threading.Thread(target=try_book, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success = sum(1 for r in results if r.startswith("SUCCESS"))
    failed = sum(1 for r in results if r.startswith("FAILED"))

    print(f"  SUCCESS responses: {success}")
    print(f"  FAILED responses:  {failed}")
    print(f"  Result: {'PASS - Only 1 booking succeeded' if success == 1 else 'FAIL'}")


# ──────────────────────────────────────────────
# Test 2: Response Time Measurement
# ──────────────────────────────────────────────
def test_response_time():
    print("\n" + "=" * 50)
    print("TEST 2: Response Time Measurement")
    print("=" * 50)

    conn = create_connection()
    times = []

    for i in range(50):
        start = time.time()
        send_command(conn, "VIEW")
        elapsed = (time.time() - start) * 1000  # ms
        times.append(elapsed)

    send_command(conn, "EXIT")
    conn.close()

    print(f"  Requests sent: 50")
    print(f"  Avg response time: {statistics.mean(times):.2f} ms")
    print(f"  Min response time: {min(times):.2f} ms")
    print(f"  Max response time: {max(times):.2f} ms")
    print(f"  Std deviation:     {statistics.stdev(times):.2f} ms")


# ──────────────────────────────────────────────
# Test 3: Throughput Under Load
# ──────────────────────────────────────────────
def test_throughput():
    print("\n" + "=" * 50)
    print("TEST 3: Throughput (Requests/Second)")
    print("=" * 50)

    total_requests = 200
    num_clients = 10
    per_client = total_requests // num_clients
    counter = {"done": 0}
    lock = threading.Lock()

    def client_work():
        conn = create_connection()
        for _ in range(per_client):
            send_command(conn, "VIEW")
            with lock:
                counter["done"] += 1
        send_command(conn, "EXIT")
        conn.close()

    start = time.time()
    threads = [threading.Thread(target=client_work) for _ in range(num_clients)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    print(f"  Clients:          {num_clients}")
    print(f"  Total requests:   {counter['done']}")
    print(f"  Time taken:       {elapsed:.2f} s")
    print(f"  Throughput:       {counter['done'] / elapsed:.1f} req/s")


# ──────────────────────────────────────────────
# Test 4: Scalability (increasing clients)
# ──────────────────────────────────────────────
def test_scalability():
    print("\n" + "=" * 50)
    print("TEST 4: Scalability (Increasing Clients)")
    print("=" * 50)

    for num_clients in [1, 5, 10, 20]:
        requests_per = 20
        counter = {"done": 0}
        lock = threading.Lock()

        def client_work():
            conn = create_connection()
            for _ in range(requests_per):
                send_command(conn, "VIEW")
                with lock:
                    counter["done"] += 1
            send_command(conn, "EXIT")
            conn.close()

        start = time.time()
        threads = [threading.Thread(target=client_work) for _ in range(num_clients)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.time() - start

        total = counter["done"]
        print(f"  {num_clients:2d} clients x {requests_per} reqs = {total:4d} total | "
              f"{elapsed:.2f}s | {total / elapsed:.1f} req/s")


# ──────────────────────────────────────────────
# Test 5: Connection handling (connect/disconnect)
# ──────────────────────────────────────────────
def test_connection_handling():
    print("\n" + "=" * 50)
    print("TEST 5: Rapid Connect/Disconnect")
    print("=" * 50)

    success = 0
    fail = 0

    for i in range(30):
        try:
            conn = create_connection()
            send_command(conn, "VIEW")
            send_command(conn, "EXIT")
            conn.close()
            success += 1
        except Exception as e:
            fail += 1

    print(f"  Connections attempted: 30")
    print(f"  Successful: {success}")
    print(f"  Failed:     {fail}")


# ──────────────────────────────────────────────
# Run all tests
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  MOVIE BOOKING SYSTEM - STRESS TEST")
    print("  Make sure server.py is running first!")
    print("=" * 50)

    test_double_booking()
    test_response_time()
    test_throughput()
    test_scalability()
    test_connection_handling()

    print("\n" + "=" * 50)
    print("  ALL TESTS COMPLETED")
    print("=" * 50)

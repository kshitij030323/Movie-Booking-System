# Movie Seat Booking System

A distributed reservation system built with Python socket programming, featuring SSL/TLS encryption, concurrency control, and double-booking prevention.

## Architecture

```
┌──────────┐     SSL/TLS (TCP)     ┌──────────────┐
│ Client 1 │ ───────────────────── │              │
├──────────┤                       │   Server     │
│ Client 2 │ ───────────────────── │  (Threaded)  │
├──────────┤                       │              │
│ Client N │ ───────────────────── │  Lock-based  │
└──────────┘                       │  Concurrency │
                                   └──────────────┘
```

- **Transport**: TCP sockets with SSL/TLS encryption
- **Concurrency**: One thread per client, `threading.Lock` protects shared seat data
- **Protocol**: Custom text-based request-response over TCP

## Protocol Design

### Requests (Client → Server)
| Command | Format | Description |
|---------|--------|-------------|
| BOOK    | `BOOK <seat> <name>` | Book a seat |
| CANCEL  | `CANCEL <seat> <name>` | Cancel a booking |
| VIEW    | `VIEW` | View all seat statuses |
| EXIT    | `EXIT` | Disconnect from server |

### Responses (Server → Client)
| Response | Meaning |
|----------|---------|
| `SUCCESS ...` | Operation completed |
| `FAILED ...`  | Operation denied (seat taken, wrong user, etc.) |
| `ERROR ...`   | Invalid request |
| `BYE`         | Connection closing |

## Setup

### 1. Generate SSL Certificates (if not present)
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

### 2. Run Server
```bash
python server.py
```

### 3. Run Client (in separate terminal)
```bash
python client.py
```

### 4. Run Stress Test (server must be running)
```bash
python stress_test.py
```

## Features

- **SSL/TLS Encryption**: All communication encrypted using self-signed certificates
- **Concurrent Clients**: Multi-threaded server handles multiple clients simultaneously
- **Double-Booking Prevention**: Thread lock ensures only one client can book a seat at a time
- **Cancel Booking**: Users can cancel their own bookings
- **Graceful Shutdown**: Server handles Ctrl+C and notifies connected clients
- **Input Validation**: Server validates commands, client validates user input
- **Error Handling**: Handles abrupt disconnections, SSL failures, invalid commands

## Concurrency Control

The server uses a **lock-based** approach:

```python
lock = threading.Lock()

with lock:
    if seats[seat] is None:
        seats[seat] = user        # atomic book
    else:
        # seat already taken      # reject
```

This prevents race conditions where two clients try to book the same seat simultaneously. The lock ensures the check-and-book operation is **atomic**.

## Performance Testing

The `stress_test.py` script runs 5 tests:

| Test | What it measures |
|------|-----------------|
| Double Booking | 10 clients book same seat simultaneously → only 1 succeeds |
| Response Time | Average, min, max latency over 50 requests |
| Throughput | Requests/second with 10 concurrent clients |
| Scalability | Performance with 1, 5, 10, 20 clients |
| Connection Handling | 30 rapid connect/disconnect cycles |

## Files

| File | Description |
|------|-------------|
| `server.py` | Multi-threaded SSL server with booking logic |
| `client.py` | Interactive CLI client |
| `stress_test.py` | Performance and stress testing script |
| `cert.pem` | SSL certificate |
| `key.pem` | SSL private key |
| `README.md` | Documentation |

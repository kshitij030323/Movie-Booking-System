# Movie Seat Booking System

A distributed reservation system built with Python socket programming, featuring SSL/TLS encryption, concurrency control, double-booking prevention, and a Tkinter GUI client.

## Architecture

```
┌──────────────┐     SSL/TLS (TCP)     ┌──────────────┐
│  CLI Client  │ ───────────────────── │              │
├──────────────┤                       │   Server     │
│  GUI Client  │ ───────────────────── │  (Threaded)  │
│  (Tkinter)   │                       │              │
├──────────────┤                       │  Lock-based  │
│  Client N    │ ───────────────────── │  Concurrency │
└──────────────┘                       └──────────────┘
```

- **Transport**: TCP sockets with SSL/TLS encryption
- **Concurrency**: One thread per client, `threading.Lock` protects shared seat data
- **Protocol**: Custom text-based request-response over TCP
- **Seats**: 100 seats (configurable in server)

## Protocol Design

### Requests (Client → Server)
| Command | Format | Description |
|---------|--------|-------------|
| BOOK    | `BOOK <seat> <name>` | Book a seat (1-100) |
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
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes \
  -addext "subjectAltName=IP:0.0.0.0,IP:127.0.0.1,DNS:localhost"
```

### 2. Run Server
```bash
python server.py
```
The server prints its LAN IP address at startup so remote clients know what to connect to.

Custom port:
```bash
python server.py 9999
```

### 3. Run Client

**Terminal client:**
```bash
python client.py                          # localhost, default port
python client.py 192.168.1.5              # remote server
python client.py 192.168.1.5 9999         # remote server, custom port
```

**GUI client (Tkinter):**
```bash
python client_gui.py                      # opens connection window
python client_gui.py 192.168.1.5 9999     # pre-fills server IP and port
```

### 4. Run Stress Test (server must be running)
```bash
python stress_test.py                     # localhost, default port
python stress_test.py 192.168.1.5 9999    # remote server, custom port
```

## GUI Client

The Tkinter GUI (`client_gui.py`) provides a visual interface for booking seats:

- **Connection screen**: Enter server IP, port, and your name
- **10x10 seat grid** with color-coded seats:
  - **Green** — Available
  - **Red** — Booked by someone else
  - **Blue** — Booked by you
  - **Yellow** — Currently selected
- **Select-then-act workflow**: Click a seat to select it, then use the **Book** or **Cancel** button
- **Refresh** button to sync seat status from the server

## Connecting from Another PC

1. Start the server — it will print the LAN IP:
   ```
   [*] Reservation Server running on 0.0.0.0:65432 (SSL enabled)
   [*] Local clients:  python client.py 127.0.0.1 65432
   [*] Remote clients: python client.py 192.168.1.5 65432
   ```
2. Copy `client.py` (or `client_gui.py`) to the other PC
3. Run the client with the server's IP:
   ```bash
   python client_gui.py 192.168.1.5 65432
   ```
4. **Firewall**: On macOS, allow incoming connections when the firewall popup appears. On Windows, allow Python through Windows Firewall.

## Features

- **SSL/TLS Encryption**: All communication encrypted using self-signed certificates
- **Concurrent Clients**: Multi-threaded server handles multiple clients simultaneously
- **Double-Booking Prevention**: Thread lock ensures only one client can book a seat at a time
- **100 Seats**: Large seat capacity with a visual grid in the GUI
- **Cancel Booking**: Users can cancel their own bookings
- **Graceful Shutdown**: Server handles Ctrl+C and notifies connected clients
- **GUI + CLI**: Both graphical (Tkinter) and terminal clients available
- **Remote Connections**: Server binds to all interfaces (`0.0.0.0`) and displays LAN IP for easy remote access
- **Connection Timeout**: Clients timeout after 10 seconds with clear error messages
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
| `server.py` | Multi-threaded SSL server with booking logic (100 seats) |
| `client.py` | Interactive terminal client |
| `client_gui.py` | Tkinter GUI client with visual seat grid |
| `stress_test.py` | Performance and stress testing script |
| `cert.pem` | SSL certificate |
| `key.pem` | SSL private key |
| `README.md` | Documentation |

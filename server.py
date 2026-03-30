import socket
import ssl
import threading
import signal
import sys
import time

HOST = '0.0.0.0'
DEFAULT_PORT = 65432

# seat database
seats = {
    "1": None,
    "2": None,
    "3": None,
    "4": None,
    "5": None
}

lock = threading.Lock()
active_clients = []
server_running = True


def get_local_ip():
    """Get the machine's LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    active_clients.append(conn)

    try:
        while server_running:
            data = conn.recv(1024).decode()

            if not data:
                break

            parts = data.strip().split()
            if not parts:
                conn.send(b"ERROR Invalid request\n")
                continue

            command = parts[0].upper()

            if command == "BOOK":
                if len(parts) < 3:
                    conn.send(b"ERROR Usage: BOOK <seat> <name>\n")
                    continue

                seat = parts[1]
                user = parts[2]

                with lock:
                    if seat not in seats:
                        conn.send(b"ERROR Seat does not exist\n")
                    elif seats[seat] is None:
                        seats[seat] = user
                        conn.send(f"SUCCESS Seat {seat} booked for {user}\n".encode())
                    else:
                        conn.send(f"FAILED Seat {seat} already booked by {seats[seat]}\n".encode())

            elif command == "CANCEL":
                if len(parts) < 3:
                    conn.send(b"ERROR Usage: CANCEL <seat> <name>\n")
                    continue

                seat = parts[1]
                user = parts[2]

                with lock:
                    if seat not in seats:
                        conn.send(b"ERROR Seat does not exist\n")
                    elif seats[seat] is None:
                        conn.send(b"FAILED Seat is not booked\n")
                    elif seats[seat] != user:
                        conn.send(b"FAILED You did not book this seat\n")
                    else:
                        seats[seat] = None
                        conn.send(f"SUCCESS Seat {seat} cancelled\n".encode())

            elif command == "VIEW":
                with lock:
                    lines = []
                    for s, u in seats.items():
                        status = f"Booked by {u}" if u else "Available"
                        lines.append(f"  Seat {s}: {status}")
                    result = "\n".join(lines) + "\n"
                conn.send(result.encode())

            elif command == "EXIT":
                conn.send(b"BYE\n")
                break

            else:
                conn.send(b"ERROR Unknown command\n")

    except (ConnectionResetError, BrokenPipeError):
        print(f"[-] Client {addr} disconnected abruptly")
    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        if conn in active_clients:
            active_clients.remove(conn)
        conn.close()
        print(f"[-] Disconnected: {addr}")


def shutdown_server(sig, frame):
    global server_running
    print("\n[*] Shutting down server...")
    server_running = False

    for conn in active_clients:
        try:
            conn.send(b"SERVER_SHUTDOWN\n")
            conn.close()
        except:
            pass

    sys.exit(0)


def start_server():
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    signal.signal(signal.SIGINT, shutdown_server)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen(5)

    local_ip = get_local_ip()
    print(f"[*] Reservation Server running on {HOST}:{port} (SSL enabled)")
    print(f"[*] Local clients:  python client.py 127.0.0.1 {port}")
    print(f"[*] Remote clients: python client.py {local_ip} {port}")

    try:
        while server_running:
            client_socket, addr = server.accept()

            try:
                secure_conn = context.wrap_socket(client_socket, server_side=True)
            except ssl.SSLError as e:
                print(f"[!] SSL handshake failed from {addr}: {e}")
                client_socket.close()
                continue

            thread = threading.Thread(
                target=handle_client,
                args=(secure_conn, addr),
                daemon=True
            )
            thread.start()

    except Exception as e:
        if server_running:
            print(f"[!] Server error: {e}")
    finally:
        server.close()
        print("[*] Server stopped")


start_server()

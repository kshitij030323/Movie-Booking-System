import socket
import ssl
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 65432


def connect_to_server(host, port):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host, port))
    secure_socket = context.wrap_socket(sock, server_hostname=host)
    secure_socket.settimeout(None)
    return secure_socket


def main():
    host = DEFAULT_HOST
    port = DEFAULT_PORT

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    try:
        secure_socket = connect_to_server(host, port)
    except ConnectionRefusedError:
        print(f"Error: Server is not running at {host}:{port}. Start the server first.")
        return
    except (socket.timeout, TimeoutError):
        print(f"Error: Connection timed out to {host}:{port}.")
        print("  - Check that the server IP is correct")
        print("  - Check that both machines are on the same network")
        print(f"  - Check that port {port} is not blocked by firewall")
        return
    except OSError as e:
        print(f"Error: Could not connect to server at {host}:{port} - {e}")
        return

    print(f"Connected to Movie Reservation Server at {host}:{port} (Secure)")

    while True:
        print("\n===== Movie Seat Booking =====")
        print("1. Book a Seat")
        print("2. Cancel Booking")
        print("3. View All Seats")
        print("4. Exit")
        print("==============================")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            seat = input("Enter seat number (1-100): ").strip()
            name = input("Enter your name: ").strip()

            if not seat or not name:
                print("Seat number and name cannot be empty.")
                continue
            if " " in name:
                print("Name cannot contain spaces.")
                continue

            secure_socket.send(f"BOOK {seat} {name}".encode())
            response = secure_socket.recv(4096).decode()
            print(f"\nServer: {response}")

        elif choice == "2":
            seat = input("Enter seat number to cancel (1-100): ").strip()
            name = input("Enter your name: ").strip()

            if not seat or not name:
                print("Seat number and name cannot be empty.")
                continue

            secure_socket.send(f"CANCEL {seat} {name}".encode())
            response = secure_socket.recv(4096).decode()
            print(f"\nServer: {response}")

        elif choice == "3":
            secure_socket.send(b"VIEW")
            response = secure_socket.recv(4096).decode()
            print(f"\nCurrent Seat Status:\n{response}")

        elif choice == "4":
            secure_socket.send(b"EXIT")
            print("Disconnected from server.")
            break

        else:
            print("Invalid choice. Please enter 1-4.")

    secure_socket.close()


if __name__ == "__main__":
    main()

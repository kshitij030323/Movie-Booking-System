import socket
import ssl
import sys

DEFAULT_HOST = "127.0.0.1"
PORT = 6000


def connect_to_server(host):
    context = ssl._create_unverified_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_socket = context.wrap_socket(sock)
    secure_socket.connect((host, PORT))
    return secure_socket


def main():
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = input(f"Enter server IP address (default: {DEFAULT_HOST}): ").strip()
        if not host:
            host = DEFAULT_HOST

    try:
        secure_socket = connect_to_server(host)
    except ConnectionRefusedError:
        print(f"Error: Server is not running at {host}:{PORT}. Start the server first.")
        return
    except (socket.timeout, OSError) as e:
        print(f"Error: Could not connect to server at {host}:{PORT} - {e}")
        return

    print("Connected to Movie Reservation Server (Secure)")

    while True:
        print("\n===== Movie Seat Booking =====")
        print("1. Book a Seat")
        print("2. Cancel Booking")
        print("3. View All Seats")
        print("4. Exit")
        print("==============================")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            seat = input("Enter seat number (1-5): ").strip()
            name = input("Enter your name: ").strip()

            if not seat or not name:
                print("Seat number and name cannot be empty.")
                continue
            if " " in name:
                print("Name cannot contain spaces.")
                continue

            secure_socket.send(f"BOOK {seat} {name}".encode())
            response = secure_socket.recv(1024).decode()
            print(f"\nServer: {response}")

        elif choice == "2":
            seat = input("Enter seat number to cancel (1-5): ").strip()
            name = input("Enter your name: ").strip()

            if not seat or not name:
                print("Seat number and name cannot be empty.")
                continue

            secure_socket.send(f"CANCEL {seat} {name}".encode())
            response = secure_socket.recv(1024).decode()
            print(f"\nServer: {response}")

        elif choice == "3":
            secure_socket.send(b"VIEW")
            response = secure_socket.recv(1024).decode()
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

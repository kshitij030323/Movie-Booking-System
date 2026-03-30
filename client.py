import socket
import ssl

HOST = "127.0.0.1"
PORT = 6000

# Create SSL context without certificate verification
context = ssl._create_unverified_context()

# Create TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Wrap socket with SSL
secure_socket = context.wrap_socket(sock)

# Connect to server
secure_socket.connect((HOST, PORT))

print("Connected to reservation server")

while True:

    print("\n1. Book Seat")
    print("2. View Seats")
    print("3. Exit")

    choice = input("Enter choice: ")

    if choice == "1":

        seat = input("Seat number: ")
        user = input("Your name: ")

        msg = f"BOOK {seat} {user}"
        secure_socket.send(msg.encode())

        response = secure_socket.recv(1024)
        print(response.decode())

    elif choice == "2":

        secure_socket.send(b"VIEW")

        response = secure_socket.recv(1024)
        print(response.decode())

    elif choice == "3":

        secure_socket.send(b"EXIT")
        break

    else:
        print("Invalid choice")

secure_socket.close()
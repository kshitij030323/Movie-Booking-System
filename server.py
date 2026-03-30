import socket
import ssl
import threading

HOST = '127.0.0.1'
PORT = 6000

# seat database
seats = {
    "1": None,
    "2": None,
    "3": None,
    "4": None,
    "5": None
}

lock = threading.Lock()


def handle_client(conn, addr):
    print(f"Connected: {addr}")

    try:
        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            parts = data.split()

            command = parts[0]

            if command == "BOOK":

                seat = parts[1]
                user = parts[2]

                with lock:

                    if seat not in seats:
                        conn.send(b"ERROR Seat does not exist\n")

                    elif seats[seat] is None:
                        seats[seat] = user
                        conn.send(f"SUCCESS Seat {seat} booked\n".encode())

                    else:
                        conn.send(b"FAILED Seat already booked\n")

            elif command == "VIEW":

                result = str(seats)
                conn.send(result.encode())

            elif command == "EXIT":
                break

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()
        print("Disconnected:", addr)


def start_server():

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print("Reservation Server Running...")

    while True:

        client_socket, addr = server.accept()

        secure_conn = context.wrap_socket(client_socket, server_side=True)

        thread = threading.Thread(
            target=handle_client,
            args=(secure_conn, addr)
        )

        thread.start()


start_server()

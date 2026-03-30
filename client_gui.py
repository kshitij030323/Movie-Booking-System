import socket
import ssl
import sys
import threading
import tkinter as tk
from tkinter import messagebox

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 65432

TOTAL_SEATS = 100
COLS = 10


class ConnectWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Booking - Connect")
        self.root.resizable(False, False)

        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Movie Seat Booking System", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(frame, text="Server IP:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.host_entry = tk.Entry(frame, font=("Arial", 12), width=20)
        self.host_entry.insert(0, DEFAULT_HOST)
        self.host_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Port:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.port_entry = tk.Entry(frame, font=("Arial", 12), width=20)
        self.port_entry.insert(0, str(DEFAULT_PORT))
        self.port_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Your Name:", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = tk.Entry(frame, font=("Arial", 12), width=20)
        self.name_entry.grid(row=3, column=1, padx=5, pady=5)

        self.connect_btn = tk.Button(frame, text="Connect", font=("Arial", 12, "bold"),
                                     bg="#4CAF50", fg="white", width=15, command=self.connect)
        self.connect_btn.grid(row=4, column=0, columnspan=2, pady=15)

        self.status_label = tk.Label(frame, text="", font=("Arial", 10), fg="red")
        self.status_label.grid(row=5, column=0, columnspan=2)

        # Handle command-line args
        if len(sys.argv) > 1:
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, sys.argv[1])
        if len(sys.argv) > 2:
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, sys.argv[2])

    def connect(self):
        host = self.host_entry.get().strip()
        name = self.name_entry.get().strip()

        if not name:
            self.status_label.config(text="Please enter your name")
            return
        if " " in name:
            self.status_label.config(text="Name cannot contain spaces")
            return

        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            self.status_label.config(text="Port must be a number")
            return

        self.connect_btn.config(state="disabled", text="Connecting...")
        self.status_label.config(text="", fg="red")
        self.root.update()

        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            secure_socket = context.wrap_socket(sock, server_hostname=host)
            secure_socket.settimeout(None)
        except ConnectionRefusedError:
            self.status_label.config(text=f"Server not running at {host}:{port}")
            self.connect_btn.config(state="normal", text="Connect")
            return
        except (socket.timeout, TimeoutError):
            self.status_label.config(text=f"Connection timed out to {host}:{port}")
            self.connect_btn.config(state="normal", text="Connect")
            return
        except OSError as e:
            self.status_label.config(text=f"Connection failed: {e}")
            self.connect_btn.config(state="normal", text="Connect")
            return

        self.root.destroy()
        open_booking_window(secure_socket, name, host, port)


class BookingWindow:
    def __init__(self, root, sock, username, host, port):
        self.root = root
        self.sock = sock
        self.username = username
        self.root.title(f"Movie Booking - {username} @ {host}:{port}")

        # Top bar
        top = tk.Frame(root, bg="#333", padx=10, pady=8)
        top.pack(fill="x")
        tk.Label(top, text=f"User: {username}", font=("Arial", 11, "bold"),
                 bg="#333", fg="white").pack(side="left")
        tk.Label(top, text=f"Server: {host}:{port}", font=("Arial", 10),
                 bg="#333", fg="#aaa").pack(side="left", padx=20)
        tk.Button(top, text="Refresh", font=("Arial", 10), command=self.refresh_seats).pack(side="right", padx=5)
        tk.Button(top, text="Disconnect", font=("Arial", 10), bg="#f44336", fg="white",
                  command=self.disconnect).pack(side="right", padx=5)

        # Legend
        legend = tk.Frame(root, pady=5)
        legend.pack(fill="x", padx=10)
        tk.Label(legend, text="  ", bg="#4CAF50", width=2).pack(side="left", padx=(10, 3))
        tk.Label(legend, text="Available", font=("Arial", 9)).pack(side="left", padx=(0, 15))
        tk.Label(legend, text="  ", bg="#f44336", width=2).pack(side="left", padx=(0, 3))
        tk.Label(legend, text="Booked by others", font=("Arial", 9)).pack(side="left", padx=(0, 15))
        tk.Label(legend, text="  ", bg="#2196F3", width=2).pack(side="left", padx=(0, 3))
        tk.Label(legend, text="Your booking", font=("Arial", 9)).pack(side="left")

        # Screen label
        screen_frame = tk.Frame(root, pady=5)
        screen_frame.pack(fill="x", padx=40)
        tk.Label(screen_frame, text="SCREEN", font=("Arial", 12, "bold"), bg="#555", fg="white",
                 pady=4).pack(fill="x")

        # Seat grid
        self.seat_frame = tk.Frame(root, padx=10, pady=10)
        self.seat_frame.pack(fill="both", expand=True)

        self.seat_buttons = {}
        self.seat_status = {}

        for i in range(1, TOTAL_SEATS + 1):
            row = (i - 1) // COLS
            col = (i - 1) % COLS
            btn = tk.Button(self.seat_frame, text=str(i), width=5, height=2,
                            font=("Arial", 9), relief="raised",
                            command=lambda s=str(i): self.on_seat_click(s))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.seat_buttons[str(i)] = btn
            self.seat_status[str(i)] = None

        # Status bar
        self.status_var = tk.StringVar(value="Loading seats...")
        tk.Label(root, textvariable=self.status_var, font=("Arial", 10), fg="#555",
                 anchor="w", padx=10, pady=5).pack(fill="x", side="bottom")

        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)
        self.refresh_seats()

    def send_command(self, cmd):
        try:
            self.sock.send(cmd.encode())
            return self.sock.recv(4096).decode()
        except Exception as e:
            return f"ERROR Connection lost: {e}"

    def refresh_seats(self):
        self.status_var.set("Refreshing...")
        self.root.update()

        response = self.send_command("VIEW")
        if response.startswith("ERROR Connection lost"):
            messagebox.showerror("Connection Lost", "Lost connection to server.")
            self.root.destroy()
            return

        booked_count = 0
        for line in response.strip().split("\n"):
            line = line.strip()
            if not line.startswith("Seat "):
                continue
            parts = line.split(":")
            seat_num = parts[0].replace("Seat ", "").strip()
            status_text = parts[1].strip() if len(parts) > 1 else ""

            if seat_num not in self.seat_buttons:
                continue

            btn = self.seat_buttons[seat_num]
            if status_text == "Available":
                self.seat_status[seat_num] = None
                btn.config(bg="#4CAF50", fg="white", activebackground="#45a049")
            elif f"Booked by {self.username}" == status_text:
                self.seat_status[seat_num] = self.username
                btn.config(bg="#2196F3", fg="white", activebackground="#1976D2")
                booked_count += 1
            else:
                booker = status_text.replace("Booked by ", "")
                self.seat_status[seat_num] = booker
                btn.config(bg="#f44336", fg="white", activebackground="#d32f2f")
                booked_count += 1

        available = TOTAL_SEATS - booked_count
        self.status_var.set(f"Available: {available} | Booked: {booked_count} | Total: {TOTAL_SEATS}")

    def on_seat_click(self, seat_num):
        current = self.seat_status.get(seat_num)

        if current is None:
            # Book it
            response = self.send_command(f"BOOK {seat_num} {self.username}")
            if "SUCCESS" in response:
                self.status_var.set(f"Booked seat {seat_num}")
            else:
                messagebox.showwarning("Booking Failed", response.strip())
            self.refresh_seats()

        elif current == self.username:
            # Cancel own booking
            if messagebox.askyesno("Cancel Booking", f"Cancel your booking for Seat {seat_num}?"):
                response = self.send_command(f"CANCEL {seat_num} {self.username}")
                if "SUCCESS" in response:
                    self.status_var.set(f"Cancelled seat {seat_num}")
                else:
                    messagebox.showwarning("Cancel Failed", response.strip())
                self.refresh_seats()

        else:
            # Someone else's seat
            messagebox.showinfo("Seat Taken", f"Seat {seat_num} is booked by {current}")

    def disconnect(self):
        try:
            self.sock.send(b"EXIT")
            self.sock.close()
        except Exception:
            pass
        self.root.destroy()


def open_booking_window(sock, username, host, port):
    root = tk.Tk()
    root.geometry("620x700")
    BookingWindow(root, sock, username, host, port)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x280")
    ConnectWindow(root)
    root.mainloop()

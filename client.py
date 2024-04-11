#!/usr/bin/env python3
import sys
import socket
import threading
import json
from textView import InputApp
from lib import gen_word_packet, close_socket

app_lock = threading.Lock()

"""
    Function Name:  receive_thread
    Description:    Handles the reception of messages from the server.
    Parameters:     sock - The client socket.
                    app - The InputApp instance for message handling.
    Returns:        None
"""


def receive_thread(sock, app):
    try:
        while True:
            combined_data = sock.recv(4096)
            if not combined_data:
                print("NO message")
                break

            data_length = int.from_bytes(combined_data[:2], byteorder='big')
            json_data = combined_data[2:2+data_length].decode('utf-8')
            received_tuple = tuple(json.loads(json_data))
            with app_lock:
                app.append_message(received_tuple)
            print(f"Received word: {received_tuple}")
    except Exception as e:
        print(f"Error receiving word packet: {e}")
        return None


"""
    Function Name:  run_client
    Description:    Establishes a connection to the server and starts the client application.
    Parameters:     server_address - The IP address of the server.
                    server_port - The port number of the server.
    Returns:        None
"""


def run_client(server_address, server_port):
    try:
        c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_sock.connect((server_address, server_port))
        print(f"Connected to server at {server_address}:{server_port}")
        app = InputApp(c_sock)
        run_thread = threading.Thread(
            target=receive_thread, args=(c_sock, app,))
        run_thread.start()
        app.run()
        run_thread.join()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        close_socket(c_sock)
        print("Client socket closed.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./client.py <server_address> <server_port>")
        sys.exit(1)

    try:
        server_address = socket.gethostbyname(sys.argv[1])
        server_port = int(sys.argv[2])
        if not (10000 < server_port < 65535):
            raise ValueError("Port should be between 10000 and 65535.")
    except Exception as e:
        print(f"Error: {e}")
    except ValueError:
        print("Invalid port number. Please provide a valid port between 10000 and 65535.")
        sys.exit(1)

    run_client(server_address, server_port)

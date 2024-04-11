#!/usr/bin/env python3
import sys
import socket
import time
import threading
import json
import signal
import os
import logging
from lib import gen_word_packet, close_socket
from queue import Queue

clients_lock = threading.Lock()
buffer_lock = threading.Lock()
clients = []
buffer = Queue()
shutting_down = False
temp = 0
server_socket = None

logging.basicConfig(filename='server_log.txt',
                    level=logging.INFO, format='%(asctime)s - %(message)s')

"""
    Function Name:  print_log
    Description:    Logs a message and prints it to the console.
    Parameters:     message - The message to be logged and printed.
                    level - The logging level (default: INFO).
    Returns:        None
"""


def print_log(message, level=logging.INFO):
    logging.log(level, message)
    print(message)


"""
    Function Name:  send_messages
    Description:    Sends a message to all connected clients.
    Parameters:     message - The message to be sent.
    Returns:        None
"""


def send_messages(client_sender, message):
    word_pkt = gen_word_packet(message)
    with clients_lock:
        for client in clients:
            if client[1] != client_sender:
                client[1].sendall(word_pkt)


"""
    Function Name:  send_message
    Description:    Sends a message to a specific client.
    Parameters:     client - The client socket.
                    message - The message to be sent.
    Returns:        None
"""


def send_message(client, message):
    word_pkt = gen_word_packet(message)
    client.sendall(word_pkt)


"""
    Function Name:  approve_client
    Description:    Handles the approval process for a new client.
    Parameters:     client - The client socket.
    Returns:        None
"""


def approve_client(client):
    name = None
    while True:
        combined_data = client.recv(4096)
        if not combined_data:
            clients[:] = [tup for tup in clients if tup[1] != client]
            print_log(f"Connection closed by {client.getpeername()}")
            break

        data_length = int.from_bytes(combined_data[:2], byteorder='big')
        json_data = combined_data[2:2+data_length].decode('utf-8')
        received_tuple = json.loads(json_data)['message']
        name = received_tuple
        print_log(f"ID: {name}, Message: {received_tuple[0]}")
        continue_while = False
        with clients_lock:
            for existing_name, _ in clients:
                if name == existing_name and "CHAT APP":
                    send_message(client, ("CHAT APP", "Unavailable Username"))
                    continue_while = True
                    break
        if not continue_while:  # Continue to the next iteration of the while loop
            break
    if name:
        clients.append((name, client))
        send_message(
            client, ("CHAT APP", f"Congratulations! {name}, You can now send and receive messages"))
        print_log(
            f"CONNECTED - ID: {name}, IP Address: {client.getpeername()}")
        receive_thread = threading.Thread(
            target=handle_message, args=(client,))
        receive_thread.start()


"""
    Function Name:  handle_message
    Description:    Handles receiving messages from a client.
    Parameters:     client - The client socket.
    Returns:        None
"""


def handle_message(client):
    while True:
        combined_data = client.recv(4096)
        if not combined_data:
            clients[:] = [tup for tup in clients if tup[1] != client]
            print_log(f"DISCONNECTED - IP Address: {client.getpeername()}")
            break
        client_name = [name for name, elt in clients if elt == client]
        data_length = int.from_bytes(combined_data[:2], byteorder='big')
        json_data = combined_data[2:2+data_length].decode('utf-8')
        received_message = json.loads(json_data)
        send_thread = threading.Thread(target=send_messages, args=(
            client, (client_name[0], received_message['message']),))
        send_thread.start()
        with buffer_lock:
            buffer.put_nowait(received_message)
            print_log(f"ID: {client_name}, Message: {received_message}")
            print(f"Received message: {buffer}")


"""
    Function Name:  receive_messages
    Description:    Initiates the approval process for a new client.
    Parameters:     client - The client socket.
    Returns:        None
"""


def receive_messages(client):
    try:
        approve_thread = threading.Thread(
            target=approve_client, args=(client,))
        approve_thread.start()

    except Exception as e:
        print(f"Error receiving message: {e}")


"""
    Function Name:  accept_clients
    Description:    Accepts incoming client connections.
    Parameters:     s_sock - The server socket.
    Returns:        None
"""


def accept_clients(s_sock):
    try:
        while True:
            client, addr = s_sock.accept()
            if client:
                time.sleep(.1)  # Hello message will not display if omitted
                send_message(
                    client, ("CHAT APP", "Hello,Please Enter Username"))
                receive_messages(client)
                print_log(f"Accepted connection from {addr}")
    except KeyboardInterrupt:
        print("\nServer was interrupted. Closing server socket...")
    except Exception as e:
        print(f"Error receiving message: {e}")
    finally:
        with clients_lock:
            for elt in clients:
                elt[1].close()
            clients.clear()
        s_sock.close()
        print("Server socket closed.")
        sys.exit(1)


"""
    Function Name:  run_server
    Description:    Initializes and runs the server.
    Parameters:     port - The port number.
    Returns:        None
"""


def run_server(port):
    global server_socket
    try:
        s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_sock.bind(("", port))
        s_sock.listen(5)
        server_socket = s_sock
        print(f"Server is listening on port {port}...")
        accept_thread = threading.Thread(target=accept_clients, args=(s_sock,))
        accept_thread.start()
        accept_thread.join()
        # Wait for the accept thread to finish (this will never happen in this example)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing server.")


shutting_down = False

"""
    Function Name:  signal_handler
    Description:    Handles signals (e.g., Ctrl+C) to gracefully shut down the server.
    Parameters:     sig - The signal number.
                    frame - The current stack frame.
    Returns:        None
"""


def signal_handler(sig, frame):
    global shutting_down, shutdown_flag, server_socket
    if not shutting_down:
        shutting_down = True
        print("\nServer is shutting down. Notifying clients...")
        # Send a shutdown message to all clients
        shutdown_message = "Server is shutting down. Closing in 10 seconds"
        try:
            send_thread = threading.Thread(
                target=send_messages, args=(shutdown_message,))
            send_thread.start()
            send_thread.join()
            print(clients)
        except Exception as e:
            print(f"An error occurred: {e}")
        # Wait for some time before closing
        time.sleep(2)
        print("Closing server gracefully.")
        with clients_lock:
            for elt in clients:
                elt[1].close()
            clients.clear()
        print(clients)
        server_socket.close()
        os._exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./server <port>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        if not (10000 < port < 65535):
            raise ValueError("Port should be between 10000 and 65535.")
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except ValueError:
        print("Invalid port number. Please provide a valid port between 10000 and 65535.")
        sys.exit(1)
    run_server(port)

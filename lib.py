import json


"""
Function Name:  close_socket
Parameters:     word: The word to be serialized.
Returns:        combined_data - Combined binary data
"""


def gen_word_packet(word):
    try:
        json_data = json.dumps(word)
        combined_data = len(json_data).to_bytes(
            2, byteorder='big') + json_data.encode('utf-8')
        return combined_data
    except Exception as e:
        print(f"An error occurred: {e}")


"""
Function Name:  close_socket
Parameters:     sock - the socket being closed.
Returns:        none
"""


def close_socket(sock):
    try:
        sock.close()
    except Exception as e:
        print(f"Error closing socket: {e}")

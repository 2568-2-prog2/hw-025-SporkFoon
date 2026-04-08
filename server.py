import socket
import json
from dice_logic import process_request
from config import HOST, PORT


def parse_http_request(request_str):
    """
    Parses a raw HTTP request string and extracts the method, path, and body.

    Parameters:
        request_str (str): The raw HTTP request.

    Returns:
        tuple: (method, path, body_str)
    """
    lines = request_str.split('\r\n')
    if not lines:
        return None, None, None

    # Parse request line
    request_line = lines[0].split(' ')
    if len(request_line) < 2:
        return None, None, None

    method = request_line[0]
    path = request_line[1]

    # Find body (after the empty line)
    body = ""
    empty_line_found = False
    for line in lines:
        if empty_line_found:
            body += line
        if line == "":
            empty_line_found = True

    return method, path, body


def build_http_response(status_code, body_dict):
    """
    Builds a raw HTTP response string with JSON content.

    Parameters:
        status_code (int): HTTP status code.
        body_dict (dict): The response body as a dictionary.

    Returns:
        str: The raw HTTP response string.
    """
    status_messages = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed"
    }
    status_text = status_messages.get(status_code, "Unknown")
    response_json = json.dumps(body_dict)
    response = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(response_json)}\r\n"
        f"\r\n"
        f"{response_json}"
    )
    return response


def handle_request(request_str):
    """
    Handles a full HTTP request and returns an HTTP response string.

    Parameters:
        request_str (str): The raw HTTP request.

    Returns:
        str: The raw HTTP response string.
    """
    method, path, body = parse_http_request(request_str)

    if method is None:
        return build_http_response(400, {"status": "error", "message": "Malformed request."})

    if path != "/roll_dice":
        return build_http_response(404, {"status": "error", "message": "Endpoint not found."})

    if method != "GET":
        return build_http_response(405, {"status": "error", "message": "Method not allowed. Use GET."})

    # Parse the JSON body
    try:
        payload = json.loads(body) if body.strip() else {}
    except json.JSONDecodeError:
        return build_http_response(400, {"status": "error", "message": "Invalid JSON in request body."})

    response_dict, status_code = process_request(payload)
    return build_http_response(status_code, response_dict)


def run_server():
    """
    Starts the HTTP server using Python's socket library.
    Listens for incoming connections and dispatches requests to the handler.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server is listening on {HOST}:{PORT}...")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address} established.")

            request = client_socket.recv(4096).decode('utf-8')
            print(f"Request received ({len(request)}):")
            print("*" * 50)
            print(request)
            print("*" * 50)

            response = handle_request(request)
            client_socket.sendall(response.encode('utf-8'))
            client_socket.close()

            print("Waiting for the next TCP request...")
        except KeyboardInterrupt:
            print("\nShutting down server.")
            break
        except Exception as e:
            print(f"Error handling request: {e}")
            try:
                client_socket.close()
            except Exception:
                pass

    server_socket.close()


if __name__ == "__main__":
    run_server()

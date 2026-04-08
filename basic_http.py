import socket
import json

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server socket to an IP address and port
server_socket.bind(('localhost', 8081))

# Start listening for incoming connections
server_socket.listen(1)
print("Server is listening on port 8081...")

# Accept incoming client connections
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")
    
    # Receive the HTTP request from the client
    request = client_socket.recv(1024).decode('utf-8')
    print(f"Request received ({len(request)}):")
    print("*"*50)
    print(request)
    print("*"*50)

    # Check if the request is a GET request
    if request.startswith("GET /myjson"):
        response_data = {
            "status": "success",
            "message": "Hello, KU!"
        } # JSON response example

        # Convert dictionary to JSON string
        response_json = json.dumps(response_data)

        # HTTP response with JSON content
        response = f"""HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{response_json}"""
    elif request.startswith("GET"):
        # Prepare an HTTP response (basic HTML)
        response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                        <html><body><h1>Hello, World!</h1><hr>{request}</body></html>"""
    else:
        # Respond with a 405 Method Not Allowed if not a GET request
        response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    client_socket.sendall(response.encode('utf-8')) # Send the HTTP response to the client

    client_socket.close() # Close the client connection
    
    print("Waiting for the next TCP request...")
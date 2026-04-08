import unittest
import threading
import socket
import json
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from server import handle_request


class TestHTTPRequestHandling(unittest.TestCase):
    """
    Integration tests that test the HTTP server's request handling.
    These tests call handle_request() directly to verify HTTP parsing,
    routing, and response formatting without needing a live server.
    """

    def _build_get_request(self, path, body_dict=None):
        """Helper to build a raw HTTP GET request string."""
        body = json.dumps(body_dict) if body_dict else ""
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: 127.0.0.1:8080\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"\r\n"
            f"{body}"
        )
        return request

    def _build_post_request(self, path, body_dict=None):
        """Helper to build a raw HTTP POST request string."""
        body = json.dumps(body_dict) if body_dict else ""
        request = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: 127.0.0.1:8080\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"\r\n"
            f"{body}"
        )
        return request

    def _parse_response(self, response_str):
        """Helper to parse a raw HTTP response into status code and body dict."""
        parts = response_str.split('\r\n\r\n', 1)
        header_line = parts[0].split('\r\n')[0]
        status_code = int(header_line.split(' ')[1])
        body = json.loads(parts[1]) if len(parts) > 1 and parts[1] else {}
        return status_code, body

    # --- Correctly receives and parses incoming HTTP requests ---

    def test_valid_get_request(self):
        """Valid GET /roll_dice with proper JSON should return 200."""
        payload = {
            "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
            "number_of_random": 5
        }
        request = self._build_get_request("/roll_dice", payload)
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "success")
        self.assertEqual(len(body["dices"]), 5)

    # --- Returns valid JSON responses ---

    def test_response_is_valid_json(self):
        """Response body should always be valid JSON."""
        payload = {
            "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
            "number_of_random": 3
        }
        request = self._build_get_request("/roll_dice", payload)
        response = handle_request(request)
        parts = response.split('\r\n\r\n', 1)
        # Should not raise JSONDecodeError
        body = json.loads(parts[1])
        self.assertIsInstance(body, dict)

    def test_error_response_is_valid_json(self):
        """Error responses should also be valid JSON."""
        request = self._build_get_request("/roll_dice", {"bad": "data"})
        response = handle_request(request)
        parts = response.split('\r\n\r\n', 1)
        body = json.loads(parts[1])
        self.assertEqual(body["status"], "error")

    # --- Responds with appropriate HTTP status codes ---

    def test_wrong_endpoint_returns_404(self):
        """Request to unknown endpoint should return 404."""
        request = self._build_get_request("/unknown")
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertEqual(status, 404)

    def test_post_method_returns_405(self):
        """POST request should return 405 Method Not Allowed."""
        payload = {
            "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
            "number_of_random": 5
        }
        request = self._build_post_request("/roll_dice", payload)
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertEqual(status, 405)

    def test_invalid_json_body_returns_400(self):
        """Malformed JSON body should return 400."""
        request = (
            "GET /roll_dice HTTP/1.1\r\n"
            "Host: 127.0.0.1:8080\r\n"
            "\r\n"
            "{this is not valid json}"
        )
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertEqual(status, 400)

    def test_invalid_probabilities_returns_400(self):
        """Invalid probabilities should return 400."""
        payload = {
            "probabilities": [0.5, 0.5],  # wrong count
            "number_of_random": 5
        }
        request = self._build_get_request("/roll_dice", payload)
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertEqual(status, 400)

    def test_missing_fields_returns_400(self):
        """Missing required fields should return 400."""
        request = self._build_get_request("/roll_dice", {})
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertEqual(status, 400)

    # --- Properly connects request handling to weighted random logic ---

    def test_dice_values_in_range(self):
        """Dice values in the response must be between 1 and 6."""
        payload = {
            "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
            "number_of_random": 100
        }
        request = self._build_get_request("/roll_dice", payload)
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertEqual(status, 200)
        for val in body["dices"]:
            self.assertIn(val, [1, 2, 3, 4, 5, 6])

    def test_response_contains_expected_fields(self):
        """Successful response should contain status, probabilities, and dices."""
        payload = {
            "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
            "number_of_random": 5
        }
        request = self._build_get_request("/roll_dice", payload)
        response = handle_request(request)
        status, body = self._parse_response(response)
        self.assertIn("status", body)
        self.assertIn("probabilities", body)
        self.assertIn("dices", body)

    def test_content_type_is_json(self):
        """Response headers should include Content-Type: application/json."""
        payload = {
            "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
            "number_of_random": 5
        }
        request = self._build_get_request("/roll_dice", payload)
        response = handle_request(request)
        self.assertIn("Content-Type: application/json", response)


class TestServerSocketIntegration(unittest.TestCase):
    """
    Integration tests that start an actual server on a socket and
    communicate with it via raw TCP to verify end-to-end behavior.
    """

    @classmethod
    def setUpClass(cls):
        """Start the server in a background thread."""
        cls.host = 'localhost'
        cls.port = 9999  # Use a different port to avoid conflicts

        cls.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cls.server_socket.bind((cls.host, cls.port))
        cls.server_socket.listen(5)
        cls.server_socket.settimeout(5)

        cls.running = True

        def server_loop():
            while cls.running:
                try:
                    client_sock, addr = cls.server_socket.accept()
                    request = client_sock.recv(4096).decode('utf-8')
                    response = handle_request(request)
                    client_sock.sendall(response.encode('utf-8'))
                    client_sock.close()
                except socket.timeout:
                    continue
                except Exception:
                    break

        cls.server_thread = threading.Thread(target=server_loop, daemon=True)
        cls.server_thread.start()
        time.sleep(0.2)  # Let the server start

    @classmethod
    def tearDownClass(cls):
        """Stop the server."""
        cls.running = False
        cls.server_socket.close()
        cls.server_thread.join(timeout=3)

    def _send_raw_request(self, request_str):
        """Send a raw HTTP request to the test server and return the response."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.sendall(request_str.encode('utf-8'))
        response = sock.recv(4096).decode('utf-8')
        sock.close()
        return response

    def test_live_server_valid_request(self):
        """Send a valid request to the live server and verify response."""
        payload = {
            "probabilities": [0.1, 0.2, 0.3, 0.1, 0.2, 0.1],
            "number_of_random": 5
        }
        body = json.dumps(payload)
        request = (
            f"GET /roll_dice HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"\r\n"
            f"{body}"
        )
        response = self._send_raw_request(request)
        self.assertIn("200 OK", response)
        # Parse body
        parts = response.split('\r\n\r\n', 1)
        result = json.loads(parts[1])
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["dices"]), 5)

    def test_live_server_wrong_endpoint(self):
        """Wrong endpoint on live server should return 404."""
        request = (
            "GET /wrong HTTP/1.1\r\n"
            "Host: localhost:9999\r\n"
            "\r\n"
        )
        response = self._send_raw_request(request)
        self.assertIn("404", response)

    def test_live_server_invalid_json(self):
        """Invalid JSON body on live server should return 400."""
        request = (
            "GET /roll_dice HTTP/1.1\r\n"
            "Host: localhost:9999\r\n"
            "\r\n"
            "not json at all"
        )
        response = self._send_raw_request(request)
        self.assertIn("400", response)

    def test_live_server_multiple_requests(self):
        """Server should handle multiple sequential requests (basic load)."""
        payload = {
            "probabilities": [1/6]*6,
            "number_of_random": 3
        }
        body = json.dumps(payload)
        for i in range(5):
            request = (
                f"GET /roll_dice HTTP/1.1\r\n"
                f"Host: {self.host}:{self.port}\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"\r\n"
                f"{body}"
            )
            response = self._send_raw_request(request)
            self.assertIn("200 OK", response, f"Request {i+1} failed")


if __name__ == '__main__':
    unittest.main()

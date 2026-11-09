from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import secrets

from travel_planner import INDIAN_LOCATIONS, TripInput, build_plan_payload, normalize_location


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
USERS_FILE = BASE_DIR / "users.json"
HOST = "127.0.0.1"
PORT = int(os.environ.get("AI_TRAVELLER_PORT", "8000"))


class TravelPlannerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/locations":
            locations = sorted(location.title() for location in INDIAN_LOCATIONS)
            self.send_json({"locations": locations})
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/register":
            self.handle_register()
            return
        if self.path == "/api/login":
            self.handle_login()
            return
        if self.path != "/api/plan":
            self.send_error(404, "API route not found")
            return

        try:
            data = self.read_json_body()
            trip = self.parse_trip(data)
            self.send_json(build_plan_payload(trip))
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON request."}, status=400)

    def handle_register(self):
        try:
            data = self.read_json_body()
            name = str(data.get("name", "")).strip()
            email = str(data.get("email", "")).strip().lower()
            password = str(data.get("password", ""))

            if len(name) < 2:
                raise ValueError("Name must contain at least 2 characters.")
            if "@" not in email or "." not in email:
                raise ValueError("Please enter a valid email address.")
            if len(password) < 6:
                raise ValueError("Password must contain at least 6 characters.")

            users = self.load_users()
            if email in users:
                raise ValueError("This email is already registered.")

            users[email] = {
                "name": name,
                "email": email,
                "password": self.hash_password(password),
            }
            self.save_users(users)
            self.send_json({"message": "Registration successful.", "user": {"name": name, "email": email}})
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON request."}, status=400)

    def handle_login(self):
        try:
            data = self.read_json_body()
            email = str(data.get("email", "")).strip().lower()
            password = str(data.get("password", ""))
            users = self.load_users()
            user = users.get(email)

            if not user or not self.verify_password(password, user["password"]):
                raise ValueError("Invalid email or password.")

            self.send_json({"message": "Login successful.", "user": {"name": user["name"], "email": user["email"]}})
        except ValueError as error:
            self.send_json({"error": str(error)}, status=401)
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON request."}, status=400)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def parse_trip(self, data):
        start = normalize_location(str(data.get("start", "")))
        destination = normalize_location(str(data.get("destination", "")))
        specifications = str(data.get("specifications", "")).strip()

        try:
            days = int(data.get("days", 0))
            people = int(data.get("people", 0))
            budget = int(data.get("budget", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Days, people, and budget must be whole numbers.") from exc

        if start not in INDIAN_LOCATIONS:
            raise ValueError("Starting location must be a supported location in India.")
        if destination not in INDIAN_LOCATIONS:
            raise ValueError("Destination must be a supported location in India.")
        if days <= 0 or people <= 0 or budget <= 0:
            raise ValueError("Days, people, and budget must be positive numbers.")
        if not specifications:
            specifications = "Budget-friendly sightseeing, local food, comfortable travel"

        return TripInput(start, destination, days, people, budget, specifications)

    def send_json(self, payload, status=200):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def load_users(self):
        if not USERS_FILE.exists():
            return {}
        with USERS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save_users(self, users):
        with USERS_FILE.open("w", encoding="utf-8") as file:
            json.dump(users, file, indent=2)

    def hash_password(self, password):
        salt = secrets.token_hex(16)
        digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
        return f"{salt}:{digest}"

    def verify_password(self, password, stored_password):
        salt, digest = stored_password.split(":", 1)
        candidate = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
        return secrets.compare_digest(candidate, digest)


def main():
    if not PUBLIC_DIR.exists():
        raise SystemExit("Missing public directory.")
    server = ThreadingHTTPServer((HOST, PORT), TravelPlannerHandler)
    print(f"AI Traveller website running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

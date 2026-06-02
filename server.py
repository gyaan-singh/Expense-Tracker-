from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import sqlite3
import hashlib
from db import init_db

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class Handler(BaseHTTPRequestHandler):

    # ---------- ROUTES ----------
    def do_GET(self):
        if self.path == "/signup":
            self.send_html("templates/signup.html")

        elif self.path == "/login":
            self.send_html("templates/login.html")

        elif self.path.startswith("/dashboard"):
            self.dashboard()

        elif self.path == "/add":
            self.send_html("templates/add.html")

        else:
            self.redirect("/login")

    # ---------- POST ----------
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode()
        form = urlparse.parse_qs(data)

        if self.path == "/signup":
            self.signup(form)

        elif self.path == "/login":
            self.login(form)

        elif self.path == "/add":
            self.add_expense(form)

    # ---------- SIGNUP ----------
    def signup(self, form):
        username = form['username'][0]
        password = hash_password(form['password'][0])

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?,?)",
                      (username, password))
            conn.commit()
            self.redirect("/login")
        except:
            self.respond("User already exists")

    # ---------- LOGIN ----------
    def login(self, form):
        username = form['username'][0]
        password = hash_password(form['password'][0])

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT id FROM users WHERE username=? AND password=?",
                  (username, password))

        user = c.fetchone()

        if user:
            self.user_id = user[0]
            self.redirect(f"/dashboard?user_id={user[0]}")
        else:
            self.respond("Invalid login")

    # ---------- DASHBOARD ----------
    def dashboard(self):
        query = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(query)

        if "user_id" not in params:
            self.redirect("/login")
            return

        user_id = params["user_id"][0]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT title, amount FROM expenses WHERE user_id=?",
                  (user_id,))
        expenses = c.fetchall()

        total = sum([e[1] for e in expenses])

        html = f"""
        <h2>Dashboard</h2>
        <p>Total: ₹{total}</p>
        <a href="/add">Add Expense</a>

        <ul>
        {''.join([f"<li>{e[0]} - ₹{e[1]}</li>" for e in expenses])}
        </ul>
        """

        self.respond(html)

    # ---------- ADD EXPENSE ----------
    def add_expense(self, form):
        title = form['title'][0]
        amount = float(form['amount'][0])
        user_id = 1  # simple demo (no session system)

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("INSERT INTO expenses (user_id, title, amount) VALUES (?,?,?)",
                  (user_id, title, amount))

        conn.commit()
        self.redirect(f"/dashboard?user_id={user_id}")

    # ---------- HELPERS ----------
    def send_html(self, file):
        with open(file, "r") as f:
            content = f.read()
        self.respond(content)

    def respond(self, content):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), Handler)
    print("Running on http://localhost:8000")
    server.serve_forever()

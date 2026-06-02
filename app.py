from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create DB
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            amount REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    data = c.fetchall()
    conn.close()

    balance = sum([row[2] for row in data])

    return render_template("index.html", transactions=data, balance=balance)


@app.route("/add", methods=["POST"])
def add():
    desc = request.form["description"]
    amount = float(request.form["amount"])

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO transactions (description, amount) VALUES (?, ?)",
              (desc, amount))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

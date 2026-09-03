from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"
DB_PATH = os.path.join(os.path.dirname(__file__), "taskflow.db")


# ---------- Database Setup ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            priority TEXT NOT NULL DEFAULT 'Medium',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


# ---------- Auth Helper ----------
def login_required(f):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# ---------- Routes: Pages ----------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return render_template("register.html")

        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing:
            flash("Username or email already exists.", "error")
            conn.close()
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    status_filter = request.args.get("status", "")
    search_query = request.args.get("search", "")

    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [session["user_id"]]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        query += " AND title LIKE ?"
        params.append(f"%{search_query}%")

    query += " ORDER BY created_at DESC"
    tasks = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("dashboard.html", tasks=tasks, status_filter=status_filter, search_query=search_query)


@app.route("/task/new", methods=["GET", "POST"])
@login_required
def new_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")

        if not title:
            flash("Task title is required.", "error")
            return render_template("task_form.html", task=None)

        if len(title) > 100:
            flash("Task title must be under 100 characters.", "error")
            return render_template("task_form.html", task=None)

        conn = get_db()
        conn.execute(
            "INSERT INTO tasks (user_id, title, description, status, priority, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (session["user_id"], title, description, "Pending", priority, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

        flash("Task created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("task_form.html", task=None)


@app.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    conn = get_db()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()

    if task is None:
        conn.close()
        flash("Task not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Pending")
        priority = request.form.get("priority", "Medium")

        if not title:
            flash("Task title is required.", "error")
            conn.close()
            return render_template("task_form.html", task=task)

        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, status = ?, priority = ? WHERE id = ?",
            (title, description, status, priority, task_id)
        )
        conn.commit()
        conn.close()

        flash("Task updated successfully!", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("task_form.html", task=task)


@app.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    flash("Task deleted.", "success")
    return redirect(url_for("dashboard"))


# ---------- REST API (for Postman testing) ----------
@app.route("/api/tasks", methods=["GET"])
def api_get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(dict(task))


@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    title = data.get("title", "").strip() if data.get("title") else ""
    if not title:
        return jsonify({"error": "Title is required"}), 400

    user_id = data.get("user_id", 1)
    description = data.get("description", "")
    priority = data.get("priority", "Medium")

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (user_id, title, description, status, priority, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, title, description, "Pending", priority, datetime.now().isoformat())
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": new_id, "title": title, "status": "Pending"}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    title = data.get("title", task["title"])
    status = data.get("status", task["status"])
    priority = data.get("priority", task["priority"])
    description = data.get("description", task["description"])

    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, status = ?, priority = ? WHERE id = ?",
        (title, description, status, priority, task_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"id": task_id, "title": title, "status": status})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted"}), 200


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok", "service": "TaskFlow API"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)

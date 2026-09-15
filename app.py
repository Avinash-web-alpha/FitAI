from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "fitai_secret_key"


# ==========================
# DATABASE SETUP
# ==========================

def init_db():
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS progress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        age INTEGER,
        weight REAL,
        bmi REAL,
        score INTEGER,
        goal TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ==========================
# SAVE PROGRESS
# ==========================

def save_progress(user_id, name, age, weight, bmi, score, goal):

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO progress
    (user_id, name, age, weight, bmi, score, goal)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, age, weight, bmi, score, goal))

    conn.commit()
    conn.close()


# ==========================
# REGISTER
# ==========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return "Username already exists"

    conn.close()

    return redirect("/login")


# ==========================
# LOGIN
# ==========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = c.fetchone()
    conn.close()

    if user:
        session["user_id"] = user[0]
        return redirect("/dashboard")

    return "Invalid username or password"


# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


# ==========================
# MAIN PLANNER
# ==========================

@app.route("/", methods=["GET", "POST"])
def planner():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        age = int(request.form["age"])
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        goal = request.form["goal"]
        level = request.form["level"]
        time = int(request.form["time"])
        equipment = request.form["equipment"]

        height_m = height / 100
        bmi = weight / (height_m ** 2)

        if bmi < 18.5:
            bmi_status = "Underweight"
        elif bmi < 25:
            bmi_status = "Normal"
        elif bmi < 30:
            bmi_status = "Overweight"
        else:
            bmi_status = "Obese"

        score = 100

        if bmi < 18.5:
            score -= 15
        elif bmi > 25:
            score -= 10

        if age > 40:
            score -= 5

        score = max(score, 0)

        water = round(weight * 0.033, 1)
        calories = int(weight * 30)

        if score >= 95:
            badge = "🏆 Elite Fitness"
        elif score >= 85:
            badge = "🥇 Active Performer"
        elif score >= 70:
            badge = "🥈 Fitness Starter"
        else:
            badge = "🥉 Beginner Journey"

        workout = "Push Ups, Squats, Plank"
        diet = "Protein Rich Diet"

        save_progress(
            session["user_id"],
            name,
            age,
            weight,
            bmi,
            score,
            goal
        )

        return render_template(
            "result.html",
            name=name,
            goal=goal,
            level=level,
            equipment=equipment,
            time=time,
            bmi=round(bmi, 2),
            bmi_status=bmi_status,
            score=score,
            badge=badge,
            water=water,
            calories=calories,
            workout=workout,
            diet=diet
        )

    return render_template("index.html")


# ==========================
# HISTORY
# ==========================

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM progress WHERE user_id=?",
        (session["user_id"],)
    )

    data = c.fetchall()
    conn.close()

    return render_template("history.html", data=data)


# ==========================
# OTHER PAGES
# ==========================

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/exercises")
def exercise_library():
    return render_template("exercise_library.html")


@app.route("/coach")
def coach():
    return render_template("coach.html")


@app.route("/progress")
def progress():
    return render_template("progress.html")


@app.route("/nutrition")
def nutrition():
    return render_template("nutrition.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


# ==========================
# RUN
# ==========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
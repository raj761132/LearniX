from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import json
import random
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ----------------- MODELS -----------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    xp = db.Column(db.Integer, default=0)

    coins = db.Column(db.Integer, default=0)

    streak = db.Column(db.Integer, default=0)

    last_login = db.Column(db.Date)
    
class DailyQuest(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
class GamePlayed(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    game = db.Column(db.String(50), nullable=False)

    date = db.Column(db.Date, nullable=False)
    
# ----------------- LOAD QUESTIONS -----------------

def load_questions(subject):

    with open(f"questions/{subject}.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    random.shuffle(questions)

    return questions[:5]

# ----------------- ROUTES -----------------

@app.route("/")
def home():
    return render_template("home.html")


# ----------------- LOGIN -----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        user = User.query.filter_by(
            username=username,
            password=password,
            role=role
        ).first()

        if user:

            today = date.today()

            # FIRST LOGIN
            if user.last_login is None:
                user.streak = 1

            else:

                difference = (today - user.last_login).days

                if difference == 1:
                    user.streak += 1

                elif difference > 1:
                    user.streak = 1

                # difference == 0 → same day login → no change

            user.last_login = today

            db.session.commit()

            session["user_id"] = user.id
            session["role"] = user.role

            if role == "student":
                return redirect("/student/dashboard")

            elif role == "teacher":
                return redirect("/teacher/dashboard")

            elif role == "admin":
                return redirect("/admin")

        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ----------------- LOGOUT -----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ----------------- STUDENT DASHBOARD -----------------

@app.route("/student/dashboard")
def student_dashboard():

    if session.get("role") != "student":
        return redirect("/login")

    user = db.session.get(User, session["user_id"])

    level = user.xp // 100 + 1
    xp_current = user.xp % 100
    level_progress = (xp_current / 100) * 100

    # Fetch top 3 students
    leaderboard = User.query.filter_by(role="student")\
        .order_by(User.xp.desc())\
        .limit(3).all()

    return render_template(
        "student_dashboard.html",
        name=user.name,
        xp=user.xp,
        coins=user.coins,
        streak=user.streak,
        level=level,
        xp_current=xp_current,
        level_progress=level_progress,
        leaderboard=leaderboard
    )


# ----------------- TEACHER DASHBOARD -----------------

@app.route("/teacher/dashboard")
def teacher_dashboard():

    if session.get("role") != "teacher":
        return redirect("/login")

    return "Teacher Dashboard"


# ----------------- ADMIN PANEL -----------------

@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return redirect("/login")

    return "Admin Panel"

#----------------Navbar Button Section----------------

@app.route("/progress")
def progress():
    return "Progress Page Coming Soon"

@app.route("/courses")
def courses():
    return "Courses Page Coming Soon"

@app.route("/funzone")
def funzone():
    return "Fun Zone Coming Soon"

@app.route("/quizzes")
def quizzes():
    return "Live Quizzes Coming Soon"

@app.route("/settings")
def settings():
    return "Settings Page Coming Soon"

#-----------------GET QUESTIONS-----------------------

@app.route("/get-questions/<subject>")
def get_questions(subject):

    if session.get("role") != "student":
        return {"error":"not logged in"}

    user_id = session["user_id"]

    today = date.today()

    quest_done = DailyQuest.query.filter_by(
        user_id=user_id,
        subject=subject,
        date=today
    ).first()

    if quest_done:
        return {"completed":True}

    questions = load_questions(subject)

    return {"questions":questions}

@app.route("/complete-quest", methods=["POST"])
def complete_quest():

    user_id = session["user_id"]

    subject = request.json["subject"]

    today = date.today()

    quest = DailyQuest(
        user_id=user_id,
        subject=subject,
        date=today
    )

    db.session.add(quest)
    db.session.commit()

    return {"success":True}

@app.route("/add-xp", methods=["POST"])
def add_xp():

    if "user_id" not in session:
        return {"success": False}

    user = db.session.get(User, session["user_id"])

    user.xp += 5

    db.session.commit()

    return {"success": True, "xp": user.xp}

@app.route("/get-leaderboard")
def get_leaderboard():

    students = User.query.filter_by(role="student")\
        .order_by(User.xp.desc())\
        .all()

    data = []

    for s in students:
        data.append({
            "name": s.name,
            "xp": s.xp
        })

    return {"students": data}

@app.route("/get-rapid-questions")
def get_rapid_questions():

    if session.get("role") != "student":
        return {"error": "not logged in"}

    with open("questions/rapid_fire.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    # shuffle questions
    random.shuffle(questions)

    # pick only 5
    selected = questions[:5]

    return {"questions": selected}

@app.route("/add-points", methods=["POST"])
def add_points():

    if "user_id" not in session:
        return {"success": False}

    user_id = session["user_id"]
    game = request.json["game"]
    today = date.today()

    played = GamePlayed.query.filter_by(
        user_id=user_id,
        game=game,
        date=today
    ).first()

    if played:
        return {"success": False, "message": "Already played today"}

    user = db.session.get(User, user_id)

    user.coins += 20

    play = GamePlayed(
        user_id=user_id,
        game=game,
        date=today
    )

    db.session.add(play)
    db.session.commit()

    return {"success": True, "coins": user.coins}

# ----------------- RUN APP -----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
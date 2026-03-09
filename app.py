from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ----------------- MODELS -----------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    xp = db.Column(db.Integer, default=0)

    coins = db.Column(db.Integer, default=0)

    streak = db.Column(db.Integer, default=0)

    last_login = db.Column(db.Date)


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

    user = User.query.get(session["user_id"])

    # LEVEL CALCULATION
    level = user.xp // 100 + 1

    return render_template(
        "student_dashboard.html",
        username=user.username,
        xp=user.xp,
        coins=user.coins,
        streak=user.streak,
        level=level
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


# ----------------- CREATE DEMO USERS -----------------

@app.route("/create-users")
def create_users():

    user1 = User(
        username="student1",
        password="1234",
        role="student",
        xp=240,
        coins=120,
        streak=0
    )

    user2 = User(
        username="teacher1",
        password="1234",
        role="teacher"
    )

    user3 = User(
        username="admin",
        password="admin",
        role="admin"
    )

    db.session.add_all([user1, user2, user3])
    db.session.commit()

    return "Dummy users created!"


# ----------------- RUN APP -----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
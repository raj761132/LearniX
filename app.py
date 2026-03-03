from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"

# SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- MODELS -----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student / teacher / admin


# ----------------- ROUTES -----------------

@app.route("/")
def home():
    return render_template("home.html")


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
            session["user_id"] = user.id
            session["role"] = user.role

            if role == "student":
                return redirect("/student/dashboard")
            elif role == "teacher":
                return redirect("/teacher/dashboard")

        else:
            return render_template("login.html", error="Invalid username, password, or role.")

    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# Dummy Dashboards (for now)

@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") != "student":
        return redirect("/login")

    return render_template(
        "student_dashboard.html",
        username="student1",
        xp=240,
        level=2,
        coins=120
    )

@app.route("/teacher/dashboard")
def teacher_dashboard():
    if session.get("role") != "teacher":
        return redirect("/login")
    return "Teacher Dashboard"


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/login")
    return "Admin Panel"

@app.route("/create-users")
def create_users():
    user1 = User(username="student1", password="1234", role="student")
    user2 = User(username="teacher1", password="1234", role="teacher")
    user3 = User(username="admin", password="admin", role="admin")

    db.session.add_all([user1, user2, user3])
    db.session.commit()

    return "Dummy users created!"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv(dotenv_path=".env", override=True)

print("DEBUG DATABASE_URL =", os.getenv("DATABASE_URL"))

from flask import Flask, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Create Flask app with instance folder
app = Flask(__name__, instance_relative_config=True)

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# App configuration
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# SAFE fallback to avoid NoneType error
db_name = os.getenv("DATABASE_URL") or "learnix.db"
db_path = os.path.join(app.instance_path, db_name)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= USER MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="student")


# ================= ROUTES =================

@app.route("/")
def home():
    return "<h2>LearniX Offline App Running</h2><a href='/signup'>Signup</a> | <a href='/login'>Login</a>"

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("User already exists")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please login.")
        return redirect(url_for("login"))

    return """
        <h2>Signup</h2>
        <form method="post">
            <input name="username" placeholder="Username" required><br><br>
            <input name="password" type="password" placeholder="Password" required><br><br>
            <button type="submit">Signup</button>
        </form>
    """

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            return f"<h2>Welcome {user.username}! (Login Success)</h2>"
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))

    return """
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="Username" required><br><br>
            <input name="password" type="password" placeholder="Password" required><br><br>
            <button type="submit">Login</button>
        </form>
    """

# ================= RUN APP =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

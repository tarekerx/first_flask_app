from flask import Flask, render_template, request, redirect, url_for, flash, g, session,Blueprint
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import functools


bp = Blueprint("auth", __name__, url_prefix="/auth")


DATABASE = 'blog.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

get_db()

def login_required(func):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return wrapped_func

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form["user_name"]
        password = request.form["password"]
        email = request.form["email"]
        error = None

        if not user_name:
            error = "User name is required."
        elif not password:
            error = "Password is required."
        elif not email:
            error = "Email is required."

        if error is None:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)",
                    (user_name, generate_password_hash(password), email)
                )
                db.commit()
                db.close()
            except sqlite3.IntegrityError:
                error = f"User {user_name} is already registered."
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        error = None

        conection = get_db()
        user = conection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if not email:
            error = "Email is required."
        elif not check_password_hash(user['password'], password):
            error = "Password is incorrect."

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['user_name']
            session['email'] = user['email']
            return redirect(url_for('blog.index'))

        flash(error)

    if g.user:
        return redirect(url_for('blog.index'))

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    print("g.user:", g.user)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('blog.index'))


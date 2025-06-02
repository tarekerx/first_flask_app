from flask import Flask, render_template, request, redirect, url_for, flash, g, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from blog import bp as blog_bp
from auth import bp as auth_bp

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='oigji0pgh34ngqr0oprhqgb')

app.register_blueprint(auth_bp)
app.register_blueprint(blog_bp)


app.add_url_rule("/", endpoint="blog.index",)

if __name__ == "__main__":
    app.run(debug=True, port=5000)


from flask import Flask, render_template, request, redirect, url_for,Blueprint,g,abort, flash,session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from auth import login_required


DATABASE = 'blog.db'

bp = Blueprint("blog", __name__, url_prefix="/posts")



def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


get_db()


def get_post(post_id,check_author=True):
    post = get_db().execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    if check_author and post["auther_id"] != g.user["id"]:

        abort(403, f"Post id {post_id} doesn't belong to you.")

    return post


@bp.route("/")
def index():
    conection = get_db()
    posts = conection.execute("SELECT * FROM posts").fetchall()
    conection.close()
    return render_template("index.html", posts=posts)


@bp.route("/<int:post_id>")
def show(post_id):

    post = get_post(post_id, check_author = False)
    return render_template("show.html", post = post)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        conection = get_db()
        conection.execute("INSERT INTO posts (title, body, auther_ID) VALUES (?, ?, ?)", (title, body, g.user["Id"]))
        Id = conection.execute("SELECT last_insert_rowid()").fetchone()[0]
        conection.commit()
        conection.close()

        return redirect(url_for('blog.index'))

    return render_template("create_post.html")


@bp.route("/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update(post_id):
    post = get_post(post_id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."
        if error is not None:   
            flash(error)
        else:
            conection = get_db()
            conection.execute("UPDATE posts SET title = ?, body = ? WHERE id = ?", (title, body, post_id))
            conection.commit()
            conection.close()

            return redirect(url_for('blog.index'))

    return render_template("create_post.html", post=post)


@bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = get_post(post_id)
    conection = get_db()
    conection.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conection.commit()
    conection.close()
    return redirect(url_for('blog.index'))
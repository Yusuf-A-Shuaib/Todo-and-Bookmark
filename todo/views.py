from flask import Blueprint, render_template, redirect, url_for, abort
from todo.extensions import db

views = Blueprint('views', __name__, url_prefix='todo')

@views.route("/")
def index():
    return render_template("page.html")

@views.get("/home/<int:id>")
def index(id):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM list WHERE user_id = %s", [id])
    user = cur.fetchall()
    if user:
        return redirect(url_for('views.home'))
    return render_template("todo.html")

@views.post('/add/<int:id>')
def add(id):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM list WHERE list_id = %s", [id])
    user = cur.fetchone()
    if user:
        return redirect(url_for('views.home'))

@views.post('/delete/<int:id>')
def delete(id):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM list WHERE list_id = %s", [id])
    user = cur.fetchone()
    if user:
        cur.execute("DELETE FROM list WHERE list_id = %s", [id])
        db.connection.commit()
        cur.close()
        return redirect(url_for('views.home'))

@views.post('/report/<email>')
def report(email):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", [email])
    user = cur.fetchone()
    if user:
        return redirect(url_for('views.index'))

@views.post('/update/<int:id>')
def update(id):
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM list WHERE list_id = %s", [id])
    user = cur.fetchone()
    if user:
        cur.execute("UPDATE list SET status = 2 WHERE list_id = %s", [id])
        db.connection.commit()
        cur.close()
        return redirect(url_for('views.home'))


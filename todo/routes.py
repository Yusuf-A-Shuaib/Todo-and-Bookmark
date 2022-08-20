from flask import Blueprint, render_template

routes = Blueprint('views', __name__, url_prefix='')

@routes.route("/")
def index():
    return render_template("page.html")
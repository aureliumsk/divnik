from flask import (
    Flask, Blueprint, g, session, request, abort, render_template, redirect, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash
from logging import getLogger
from . import db, msg
import sqlite3

PERMISSION_HOMEWORK = 1
PERMISSION_LESSON = 2


Unauthorized = object()
logger = getLogger(__name__)
blueprint = Blueprint("auth", __name__, url_prefix="/auth")

class User:
    def __init__(self, login: str, permissions: int) -> None:
        self.login = login
        self.permissions = permissions

def save_user_id(user_id: int) -> None:
    session.permanent = True
    session["user_id"] = user_id

def create_user(login: str, password: str, permissions: int = 1) -> int | None:
    insert_query = 'INSERT INTO "user" ("login", "password", "permissions") VALUES (?, ?, ?) RETURNING "id"'
    hash = generate_password_hash(password)
    try:
        with db.get_db():
            cur = db.exec(insert_query, login, hash, permissions)
            user_id = cur.fetchone()[0]
    except sqlite3.IntegrityError:
        return None
    return user_id

def get_current_user() -> User:
    sql = 'SELECT "login", "permissions" FROM "user" WHERE "id" = ?'
    if "user" not in g and "user_id" in session:
        row = db.row(sql, session["user_id"])
        if row is not None:
            g.user = User(row[0], row[1])
    if "user" not in g:
        g.user = None
    return g.user

def check_user(login: str, password: str) -> int | None:
    query = 'SELECT "id", "password" FROM "user" WHERE login = ?'
    row = db.row(query, login)
    if row is None: return None
    user_id, hash = row
    if not check_password_hash(hash, password): abort(401, "Неправильный пароль!")
    return user_id

@blueprint.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("pages.index"))

@blueprint.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    login = request.form["login"]
    password = request.form["password"]
    user_id = create_user(login, password)
    if user_id is None:
        abort(409, "Этот пользователь уже зарегистрирован!")
    save_user_id(user_id)
    return "", 200

@blueprint.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    login = request.form["login"]
    password = request.form["password"]
    user_id = check_user(login, password)
    if user_id is None:
        abort(404, "Такого пользователя не существует!")
    save_user_id(user_id)
    return "", 200

# TODO: Somehow merge these functions (idk how)
def has_permissions(permissions: int) -> bool:
    user = get_current_user()
    if user is None: return False
    return user.permissions & permissions

def assert_permissions(permissions: int):
    user = get_current_user()
    if user is None: abort(401, "Войдите в аккаунт, чтобы продолжить.")
    if not user.permissions & permissions: abort(403, "У вас недостаточно прав для совершения этого действия.")

def is_logged_in():
    return get_current_user() is not None

def register_functions(app: Flask) -> None:
    @app.context_processor
    def _(): 
        return dict(has_permissions=has_permissions,
                    get_current_user=get_current_user,
                    assert_permissions=assert_permissions,
                    is_logged_in=is_logged_in)
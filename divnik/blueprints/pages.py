from flask import (
    Blueprint, Response, request, render_template, abort
)
import csv
import codecs
import logging
import sqlite3
from .. import msg
from datetime import date
from typing import (
    Iterable
)
from .. import db

WEEKDAY_NAMES = [
    "Пн",
    "Вт",
    "Ср",
    "Чт",
    "Пт",
    "Сб",
    "Вс"
]

FOREIGN_KEY_CONSTRAINT = 787 # https://sqlite.org/rescode.html#constraint_foreignkey

msg.add_messages(
    ("past", msg.Message("Этот день уже прошёл")),
    ("invalid_date", msg.Message("Поле {!r} не содержит даты", 1)),
    ("invalid_int", msg.Message("Поле {!r} не содержит целого числа", 1)),
    ("invalid_row", msg.Message("Неверный формат (строка: {})", 1)),
    ("no_row", msg.Message("Не существует записи с данным id")),
    ("mimetype", msg.Message("Указан неподдерживаемый MIME-тип для поля {!r}", 1))
)

class Homework:
    def __init__(self, desc: str, date: date, uid: int):
        self.desc = desc
        self.date = date
        self.uid = uid
    @property
    def strdate(self):
        d = WEEKDAY_NAMES[self.date.weekday()]
        return "%d/%d/%d (%s.)" % (self.date.year, self.date.day, self.date.month, d)

class Lesson:
    def __init__(self, name: str, teacher: str):
        self.name = name
        self.teacher = teacher
        self.homework: list[Homework] = []

blueprint = Blueprint("pages", __name__)
logger = logging.getLogger(__name__)
utf8reader = codecs.getreader("utf8")

def get_lessons():
    QUERY = (
        "SELECT l.id, l.name, l.teacher, h.desc, h.date, h.id FROM homework h "
        "RIGHT JOIN lesson l ON h.lesson_id = l.id AND h.date >= floor(julianday() - 1721424.5)"
    ) 
    # https://en.wikipedia.org/wiki/Rata_Die#Day_Number
    # as there is no julianday() in Python
    vals: dict[int, Lesson] = {}
    for (luid, name, teacher, desc, date, huid) in db.query(QUERY):
        if luid not in vals:
            vals[luid] = Lesson(name, teacher)
        if all((desc, date, huid)):
            vals[luid].homework.append(Homework(desc, date, huid))
    return vals


def get_lesson(uid: int):
    QUERY = (
        "SELECT l.name, l.teacher, h.desc, h.date, h.id FROM homework h "
        "RIGHT JOIN lesson l ON h.lesson_id = l.id AND h.date >= floor(julianday() - 1721424.5) "
        "WHERE l.id = ?"
    )
    lesson = None
    for (name, teacher, desc, date, huid) in db.query(QUERY, uid):
        if lesson is None:
            lesson = Lesson(name, teacher)
        if all((desc, date, huid)):
            lesson.homework.append(Homework(desc, date, huid))
    return lesson


@blueprint.route("/")
def index():
    lessons = get_lessons()
    return render_template("index.html", lessons=lessons)

def create_homework(desc: str, date: date, lesson_id: int):
    SQL = "INSERT INTO homework (desc, date, lesson_id) VALUES (?, ?, ?)"
    try:
        db.transexec(SQL, desc, date, lesson_id)
    except sqlite3.DatabaseError as e:
        if e.sqlite_errorcode != FOREIGN_KEY_CONSTRAINT:
            logger.error(f"Can't insert Homework(desc={desc!r}, date={date!r}) with {lesson_id = }", exc_info=True)
            abort(500, original_exception=e)
        abort(404, msg.message("no_row")())

@blueprint.route("/create", methods=["POST"])
def on_create_homework():
    isodate = request.form["date"]
    desc = request.form["desc"]
    lesson_id = request.form["lesson_id"]

    lesson_id = msg.should_convert(lesson_id, int, "invalid_int", "lesson_id")
    dateo = msg.should_convert(isodate, date.fromisoformat, "invalid_date", "date")

    if date.today() > dateo:
        abort(400, msg.message("past")())

    create_homework(desc, dateo, lesson_id)

    lesson = get_lesson(lesson_id)

    return render_template("lesson.html", lesson=lesson, uid=lesson_id)

def modify_homework(*args, delete: bool = False) -> int:
    if delete:
        sql = "DELETE FROM homework WHERE id = ? RETURNING lesson_id"        
    else:
        sql = "UPDATE homework SET date = ?, desc = ? WHERE id = ? RETURNING lesson_id"
    logger.info(f"Args are: {args}")
    cur = db.exec(sql, *args)
    row = cur.fetchone()
    if row is None:
        abort(404, msg.message("no_row")())
    return row[0]

@blueprint.route("/update/<int:uid>", methods=["POST"])
def on_update_homework(uid: int):
    isodate = request.form["date"]
    desc = request.form["desc"]

    dateo = msg.should_convert(isodate, date.fromisoformat, "invalid_date", "date")

    if date.today() > dateo:
        abort(400, msg.message("past")())
    
    with db.get_db():
        lid = modify_homework(dateo, desc, uid)
        lesson = get_lesson(lid)

    return render_template("lesson.html", lesson=lesson, uid=lid)

@blueprint.route("/delete/<int:uid>", methods=["POST"])
def on_delete_homework(uid: int):
    with db.get_db():
        lid = modify_homework(uid, delete=True)
        lesson = get_lesson(lid)
    
    return render_template("lesson.html", lesson=lesson, uid=lid)

def validate(reader: Iterable[list[str]]):
    for i, row in enumerate(reader):
        if len(row) != 2:
            abort(400, msg.message("invalid_row")(i + 1))
        yield row
    
@blueprint.route("/import", methods=["GET", "POST"])
def import_from_file():
    DELETE_QUERY = "DELETE FROM lesson"
    INSERT_QUERY = "INSERT INTO lesson (name, teacher) VALUES (?, ?)"
    if request.method == "GET":
        return render_template("import.html")
    else:
        rawfile = request.files["file"]
        tablestream = utf8reader(rawfile)
        con = db.get_db()
        if rawfile.content_type != "text/csv": abort(400, msg.message("mimetype")("file"))
        with con:
            cur = con.cursor()
            cur.execute(DELETE_QUERY)
            cur.executemany(INSERT_QUERY, validate(csv.reader(tablestream)))
        return "", 204
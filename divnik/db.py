from flask import current_app, g
from datetime import date
import atexit
import sqlite3
import logging
from collections.abc import Iterator, Iterable

logger = logging.getLogger(__name__)

# difference between julian day and whatever date.toordinal returns
db = None

def init_db() -> None:
    if sqlite3.threadsafety != 3:
        logger.fatal("Sqlite3 wasn't compiled for multithreading!")
        exit(3)

    global db
    db = sqlite3.connect(current_app.config["DATABASE_PATH"], check_same_thread=False, 
                         detect_types=sqlite3.PARSE_DECLTYPES)

    sqlite3.register_adapter(date, lambda d: d.toordinal())
    sqlite3.register_converter("DATE", lambda d: date.fromordinal(int(d)))

    atexit.register(db.close)
    
    cur = db.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.close()

    logger.info("Initialized the database!")


def get_db() -> sqlite3.Connection:
    if db is None:
        init_db()
    return db


def query(sql: str, *args) -> Iterator[tuple]:
    cur = get_db().cursor()
    for row in cur.execute(sql, args):
        yield row

def transexec(sql: str, *args) -> sqlite3.Cursor:
    con = get_db()
    with con:
        return exec(sql, *args)
    
def exec(sql: str, *args) -> sqlite3.Cursor:
    con = get_db()
    cur = con.cursor()
    cur.execute(sql, args)
    return cur
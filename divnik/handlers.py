from werkzeug.exceptions import HTTPException
from urllib.parse import urlencode
from flask import (
    Flask, request, redirect, url_for, render_template
)

def posterror(e: HTTPException):
    if request.method != "POST":
        return e
    
    res = e.get_response()
    res.data = urlencode({
        "code": e.code,
        "name": e.name,
        "desc": e.description   
    })
    res.content_type = "application/x-www-form-urlencoded"
    
    return res
    
def forbidden(e): 
    if request.method != "GET": return posterror(e)
    return render_template("forbidden.html")

def unauthorized(e): 
    if request.method != "GET": return posterror(e)
    return redirect(url_for("auth.login"))

def register_handlers(app: Flask) -> None:
    app.register_error_handler(HTTPException, posterror)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(401, unauthorized)
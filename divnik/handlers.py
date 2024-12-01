from flask import render_template
from werkzeug.exceptions import HTTPException
from urllib.parse import urlencode
from flask import Response, request

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
    
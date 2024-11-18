from functools import wraps
from flask import session, request, redirect

def no_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            if request.method == 'GET':
                return redirect('/')
            return "You are already logged in", 302
        return func(*args, **kwargs)
    return wrapper
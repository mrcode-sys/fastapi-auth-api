from fastapi import Depends
from app.models.model import User
from app.dependencies import validate_token
from app.main import bcrypt_context, ALGORITHM, TOKEN_EXP_TIME, SECRET_KEY
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import re
import time

login_allowed = True
login_attempts = {}

def search_user(code, session, by="name"):
    if by == "id":
        user = session.query(User).filter(User.id==int(code)).first()

    else:
        user = session.query(User).filter(User.name==code).first()

    return user

# ------- User Token ------- #
def create_token(user_id, session, exp_time=TOKEN_EXP_TIME, token_type="access",):
    user = search_user(user_id, session, "id")
    if not user:
        print(f"DEBUG: user_id: {user_id}")

    version = user.token_version
    if not version:
        version = 0
        user.token_version = version
        session.commit()

    time = re.findall(r'\d+', exp_time)
    time_format = (re.findall(r'[a-zA-Z]+', exp_time)[:1] or ["M"])[0]
    
    exp_date = datetime.now(timezone.utc)

    if time:
        time = int(time[0])

        if time_format == "D":
            exp_date = exp_date + timedelta(days=time)

        elif time_format == "H":
            exp_date = exp_date + timedelta(hours=time)

        elif time_format == "M":
            exp_date = exp_date + timedelta(minutes=time)
        
        else:
            exp_date = exp_date + timedelta(minutes=time)

    dic_info = {"sub": str(user_id), "type": token_type, "version": version , "exp": exp_date}

    return jwt.encode(dic_info, SECRET_KEY, ALGORITHM)

def up_token_ver(user_id, session):
    user = search_user(user_id, session, "id")

    if not user:
        return False, {"err": "Invalid access"}

    if not user.token_version:
        user.token_version = 0
        session.commit()

    user.token_version += 1
    session.commit()

    return True, {"msg": "Success"}

def refresh_token(user, token_type, session):
    if token_type != "refresh":
        return False, {"err": "Access denied"}

    if search_user(user, session, "id"):
        access_token = create_token(user, session)
        if access_token != False:
            return True, {
                "access_token": access_token,
                "token_type": "Bearer"
                }

        return False, {"err": "Invalid access"}

    else:
        return False, {"err": "Invalid access"}

# ------- User Auth ------- #
def rate_limit(ip):
    now = time.time()

    ip_data = login_attempts.get(ip)

    print(f"DEBUG: {ip_data}")

    if not ip_data:
        login_attempts[ip] = {"count": 1, "time": now}

        return True, login_attempts[ip].get("count")
    
    if now - ip_data["time"] > 60:
        login_attempts[ip] = {"count": 1, "time": now}

        return True, login_attempts[ip].get("count")
    
    if ip_data["count"] == 5:
        if login_allowed == True:
            ip_data["time"] = now

        return False, int(60-(now - ip_data["time"]))
    
    ip_data["count"] += 1
    return True, login_attempts[ip].get("count")

def verify_user(user, password):
    if user and bcrypt_context.verify(password, user.password):
        return True
    else:
        return False

def register_user(user_reg_schema, password, session):

    username = user_reg_schema.user
    email = user_reg_schema.email

    user = search_user(username, session)
    if user:
        return False, {"err": "User already exists"}
    else:
        new_user = User(username, password, email)
        session.add(new_user)
        session.commit()
        
        return True, {"msg": "User registred"}

def log_in_user(login_schema, ip, session):
    global login_allowed
    
    user = search_user(login_schema.user, session)

    if verify_user(user, login_schema.password) and login_allowed == True:
        access_token = create_token(user.id, session)
        refresh_token = create_token(user.id, session, "7D", "refresh")

        return True, 200, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
            }
            
    login_allowed, value = rate_limit(ip)
    if login_allowed == False:
        return False, 429, {"err": "Rate Limit", "time": value}

    print(login_allowed)
    return False, 401, {"err": "Incorrect password or user not found"}

def refresh_password(user_updt_pass_schema, user_id, session):
    user = search_user(user_id, session, "id")

    print(user)
    if verify_user(user, user_updt_pass_schema.password):
        user.password = bcrypt_context.hash(user_updt_pass_schema.new_password)
        session.commit()
        return True, {"msg": "Password updated"}
    return False, {"err": "Incorrect password"}
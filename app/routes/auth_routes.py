from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import pick_session, validate_token
from app.main import bcrypt_context
from app.services.user import register_user, log_in_user, refresh_token, refresh_password, up_token_ver
from sqlalchemy.orm import Session
from app.models.model import User
from app.schemas import User_Reg_Schema, User_Login_Schema, User_Updt_Pass_Schema
from app.resp.resp import response

auth_router = APIRouter(prefix="/auth", tags=["auth"])



@auth_router.get("/")
async def home():
    return {"mensagem": "foi acessada a home da autenticação"}

@auth_router.post("/signup") #criar conta
async def create_account(user_reg_schema: User_Reg_Schema, session: Session = Depends(pick_session)):
    encrypted_pass = bcrypt_context.hash(user_reg_schema.password)
    status, resp = register_user(user_reg_schema, encrypted_pass, session)

    return response(status, 400, resp)

@auth_router.post("/signin") #entrar na conta
async def login_account(request: Request, user_login_schema: User_Login_Schema, session: Session = Depends(pick_session)):

    ip = request.client.host

    status, status_code, resp = log_in_user(user_login_schema, ip, session)

    return response(status, status_code, resp)

@auth_router.post("/signin_form") #entrar na conta via fastapi
async def login_fastapi(request: Request, form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pick_session)):

    class schema_login_fastapi:
        def __init__(self, form):
            self.user = form.username
            self.password = form.password

    user_login_schema = schema_login_fastapi(form)

    ip = request.client.host

    status, status_code, resp = log_in_user(user_login_schema, ip, session)
    if resp.get("access_token"):
        resp["access_token"] = resp.pop("refresh_token")
    print(resp)
    return response(status, 400, resp)

@auth_router.get("/refresh")
async def token_refresh(token: dict = Depends(validate_token), session: Session = Depends(pick_session)):
    user = token.get("user_id")
    token_type = token.get("type")
    status, resp = refresh_token(user, token_type, session)


    return response(status, 400, resp)

@auth_router.post("/logout_all")
async def logout_all(token: dict = Depends(validate_token), session: Session = Depends(pick_session)):
    user = token.get("user_id")

    status, resp = up_token_ver(user, session)

    return response(status, 400, resp)

@auth_router.post("/update_password")
async def update_password(user_updt_pass_schema: User_Updt_Pass_Schema, token: dict = Depends(validate_token), session: Session = Depends(pick_session)):
    user = token.get("user_id")
    status, resp = refresh_password(user_updt_pass_schema, user, session)

    return response(status, 400, resp)
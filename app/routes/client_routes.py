from fastapi import APIRouter, Depends
from app.dependencies import pick_session, validate_token
from app.services.client import add_client, list_client, info, e_client
from sqlalchemy.orm import Session
from app.schemas import Client_Schema, Edit_Client_Schema, Info_Schema
from app.resp.resp import response

client_router = APIRouter(prefix="/clients", tags=["client"], dependencies=[Depends(validate_token)])

@client_router.get("/")
async def home():
    return {"mensagem": "foi acessada a home dos dos clientes"}

@client_router.post("/reg_client")
async def reg_client(client_schema: Client_Schema, session: Session = Depends(pick_session), token: dict = Depends(validate_token)):
    
    status, resp = add_client(client_schema, session, token)

    return response(status, 400, resp)

@client_router.post("/list")
async def list_clients(session: Session = Depends(pick_session)):
    status, resp = list_client(session)

    return response(status, 400, resp)

@client_router.post("/edit_client/")
async def edit_client(client_schema: Edit_Client_Schema, session: Session = Depends(pick_session)):
    status, resp = e_client(client_schema, session)
    
    return response(status, 400, resp)

@client_router.post("/client_info")
async def client_info(info_schema: Info_Schema, session: Session = Depends(pick_session)):
    status, resp = info(info_schema, session)

    return response(status, 400, resp)
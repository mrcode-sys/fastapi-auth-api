from app.models.model import Client
from datetime import datetime
from app.resp.ordened_resp import info_client
from app.services.user import search_user
class edited_client:
    pass

def search_client(code, session, by):
    if by == "id":
        client = session.query(Client).filter(Client.id==int(code)).first()

    elif by == "cpf":
        client = session.query(Client).filter(Client.cpf==int(code)).first()

    return client

def add_client(client_schema, session, token):
    user_id = token.get("user_id")
    user = search_user(user_id, session, "id")
    added_by = user.name

    if not search_user(user_id, session, by="id"):
        return False, {"err": f"User {added_by} not found"}

    date_time = datetime.now().astimezone()
    formated_date_time = date_time.strftime(("%d/%m/%Y %H:%M:%S"))

    new_client = Client(
        client_schema.name,
        client_schema.birth,
        client_schema.cep,
        client_schema.cpf,
        client_schema.email,
        added_by
    )
    session.add(new_client)
    session.commit()
        
    return True, {"msg": f"client added. ID: {new_client.id}"}

def list_client(session):
    return True, {"Clients": session.query(Client).all()}

def e_client(client_schema, session):
    client = search_client(client_schema.id, session, "id")

    if not client:
        return False, {"err": "Client not found"}
    
    clientb = client_schema.model_dump(exclude_unset=True)

    for key, value in clientb.items():
        setattr(client, key, value)

    session.commit()

    return True, {"msg": f"Edited client. ID: {client.id}", "client": info_client(client)}

def info(info_schema, session):
    client = search_client(info_schema.code, session, info_schema.by)
    if client:
        return True, {"Client": client, "Client":info_client(client)}
    else:
        return False, {"err": "Client not found"}
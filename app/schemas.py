from pydantic import BaseModel
from typing import Optional

class User_Reg_Schema(BaseModel):
    user: str
    password: str
    email: Optional[str]

    class Config:
        from_attributes = True

class User_Login_Schema(BaseModel):
    user: str
    password: str

    class Config:
        from_attributes = True

class User_Updt_Pass_Schema(BaseModel):
    password: str
    new_password: str

    class Config:
        from_attributes = True

class Client_Schema(BaseModel):
    name: str
    birth: str
    cep: int
    cpf: int
    email: Optional[str]

    class Config:
        from_attributes = True

class Edit_Client_Schema(Client_Schema):
    id: int

    class Config:
        from_attributes = True

class Info_Schema(BaseModel):
    code: str
    by: str

    class Config:
        from_attributes = True
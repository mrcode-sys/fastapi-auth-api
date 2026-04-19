from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base
#from sqlalchemy_utils import ChoiceType

db = create_engine("sqlite:///app/database/data.db")

Base = declarative_base()

# Usuários funcionários
class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)

    name = Column("name", String, nullable=False)
    password = Column("password", String, nullable=False)
    email = Column("email", String)
    token_version = Column("token_version", Integer)

    def __init__(self, name, password, email, token_version=0):
        self.name = name
        self.password = password
        self.email = email
        self.token_version = token_version

# Clientes
class Client(Base):
    __tablename__ = "clients"

    id = Column("id", Integer, primary_key=True, autoincrement=True)

    name = Column("name", String, nullable=False)
    birth = Column("birth", String)
    cep = Column("cep", Integer)
    cpf = Column("cpf", Integer, unique=True)
    email = Column("email", String)
    added_by = Column("added_by", ForeignKey("users.id"))

    def __init__(self, name, birth, cep, cpf, email, added_by):
        self.name = name
        self.birth = birth
        self.cep = cep
        self.cpf = cpf
        self.email = email
        self.added_by = added_by
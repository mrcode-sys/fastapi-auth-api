from fastapi import HTTPException, Depends
from app.models.model import db
from sqlalchemy.orm import sessionmaker
from app.main import SECRET_KEY, ALGORITHM, oauth2_schema
from jose import jwt, JWTError
from app.models.model import User
def pick_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def validate_token(token: str = Depends(oauth2_schema), session = Depends(pick_session)):
    from app.services.user import search_user

    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = dic_info.get("sub")
        token_type = dic_info.get("type")
        version = dic_info.get("version")
    except JWTError:
        raise HTTPException(status_code=401, detail="Access denied")
    
    user = search_user(user_id, session, "id")
    if user:
        if user.token_version == version:
            return {"user_id": user_id, "type": token_type}
        else:
            raise HTTPException(status_code=401, detail="Access denied")

    raise HTTPException(status_code=401, detail="Invalid Access")
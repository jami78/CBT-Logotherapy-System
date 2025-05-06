from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, WebSocket, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.users import Users
from app.core.config import get_settings
import logging 

logger = logging.getLogger(__name__)
# JWT Secret Key
settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

#  Hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#  Authenticate user using SQLAlchemy ORM
def authenticate_user(db: Session, username: str, password: str):
    """Fetches user from DB and verifies password."""
    user = db.query(Users).filter(Users.username == username).first()
    
    if user and verify_password(password, user.hashed_password):
        return user  
    
    return None

# Create JWT Token
def create_access_token(data: dict, expires_delta: timedelta):
    """Encodes data into a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        
        user = db.query(Users).filter(Users.username == username).first()

        if user is None:
            raise credentials_exception 
        
        return user

    except JWTError:
        raise credentials_exception
    

async def get_current_user_ws(
    websocket: WebSocket, # Pass websocket for potential closing
    token: str = Query(..., description="Authentication token from query param"), # Let FastAPI inject the token from query
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.WS_1008_POLICY_VIOLATION, # Use WebSocket close code
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # Close connection instead of raising HTTP exception for websockets
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload")
            return None # Indicate failure

        user = db.query(Users).filter(Users.username == username).first()
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return None # Indicate failure

        return user # Return the user object if valid

    except JWTError as e:
        logger.error(f"JWT Error during WS auth: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=f"Token validation error: {e}")
        return None # Indicate failure
    except Exception as e: # Catch other potential errors during auth
        logger.error(f"Unexpected error during WS auth: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error during authentication")
        return None


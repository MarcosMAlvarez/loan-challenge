"""API helper functions
"""
from collections import deque
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from db.models import AdminUser
from db.helpers import session_scope
from rest.models import Admin, TokenData
from settings import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication methods
def verify_password(plain_password, hashed_password):
    """Verify if plain and hashed passwords are equals"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str) -> Optional[Admin]:
    """If username given as parameter is an admin, return an Admin instance. Else return None"""
    with session_scope() as session:
        user = session.query(AdminUser).filter(AdminUser.username == username).first()
    if user:
        return Admin(
            username=user.username,
            password=user.password,
        )
    return None


def authenticate_user(username: str, password: str) -> Optional[Admin]:
    """Authentucate user process.

    Check if the username is in the admin database and the password is correct.
    If both conditions are correct, it returns an Admin instance; otherwise it returns None"""
    user = get_user(username)
    if not user:
        return None
    elif not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates and returns an jwt token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def check_credentials(token: str = Depends(oauth2_scheme)):
    """Check if credentials are valid else raise a HTTPError"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as error:
        raise credentials_exception from error
    else:
        user = get_user(username=token_data.username)  # type: ignore
        if user is None:
            raise credentials_exception


# Throttling constants. The API can be called up to MAX_LEN times in SECONDS seconds
MAX_LEN = 5
SECONDS = 30
deq = deque(maxlen=MAX_LEN)  # type: deque

class RateLimitException(Exception):
    pass

def rate_limit(maxlen, seconds):
    def inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            global deq
            current_time = datetime.now()
            if len(deq) != 0:
                if len(deq) == maxlen and (current_time - deq[0]).seconds < seconds:
                    raise RateLimitException()
            deq.append(current_time)
            return await func(*args, **kwargs)

        return wrapper

    return inner

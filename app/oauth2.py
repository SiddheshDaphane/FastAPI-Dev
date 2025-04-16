from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRETE_KEY = "8e6c968d039c5844c744148d77aa7c7dac43c6b26ee145a468d9a27b72d30f85"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRETE_KEY, algorithm=ALGORITHM)

    return encoded_jwt




from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from models.user import UserForm, User, UserAuthForm, UserEmail, UserByToken
from typing import Annotated
from jose import JWTError, jwt
from utils.password import verify_password, get_password_hash
from datetime import timedelta, datetime, timezone
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.token import Token, TokenData
from utils.datetime import time_at
import os
from dotenv import load_dotenv
from models.user import Role

authentication_router = APIRouter(
    prefix="/auth",
    tags=["authentication"],)


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

REFRESH_TOKEN_SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY')
ACCESS_TOKEN_SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

if ACCESS_TOKEN_EXPIRE_MINUTES is None:
    raise ValueError("La variable de entorno 'ACCESS_TOKEN_EXPIRE_MINUTES' no está definida")
else: 
    ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)


if REFRESH_TOKEN_EXPIRE_MINUTES is None:
    raise ValueError("La variable de entorno 'REFRESH_TOKEN_EXPIRE_MINUTES' no está definida")
else: 
    REFRESH_TOKEN_EXPIRE_MINUTES = int(REFRESH_TOKEN_EXPIRE_MINUTES)





oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



async def authenticate_user(email:str, password:str) -> User | bool:
    user = await User.by_email(email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user



def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def decode_token(token: str, type: str = 'access') -> TokenData | None:
    try:
        if type == 'refresh':
            payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        else:
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        id= payload.get('sub')
        if not id:
            raise JWTError("Token is missing 'sub' field")
        decoded_data = TokenData(id=id)
        return decoded_data

        
    except JWTError as exc:
        print(exc)
        return None





async def check_cookie(request: Request):
    cookie = request.cookies
    if not cookie:
        return None
    if cookie.get('refresh-Token'):
        return cookie.get('refresh-Token')



async def get_current_user(auth_token: Annotated[UserByToken, Depends(oauth2_scheme)]) -> UserByToken:
    #credentials_exception = HTTPException(
    #status_code=status.HTTP_401_UNAUTHORIZED,
    #detail="No se han podido validar las credenciales",
    #headers={"WWW-Authenticate": "Bearer"},
    #)

    if not auth_token:
        raise HTTPException(
            status_code=401,
            detail="Access Token no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    decoded_data = await decode_token(auth_token)

    if not decoded_data:

        raise HTTPException(
            status_code=401,
            detail="Access Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.get(decoded_data.id)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado para ese Access Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserByToken(id=user.id, role=user.role, full_name=user.full_name)


async def get_current_admin_user(user: Annotated[UserByToken, Depends(get_current_user)]) -> UserByToken:
    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes permisos para realizar esta acción")
    return user

async def get_current_admin_or_editor_user(user: Annotated[UserByToken, Depends(get_current_user)]) -> UserByToken:
    if user.role != Role.admin and user.role != Role.editor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes permisos para realizar esta acción")
    return user


async def authenticate_user(email: EmailStr, password: str) -> User | bool:
    user_database = await User.by_email(email)
    if not user_database:
        return False
    if user_database.active == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El usuario no está validado")
    if not verify_password(password, user_database.password):
        return False
    return user_database
    



@authentication_router.post("/validate", status_code=status.HTTP_201_CREATED)
async def create_password(user: UserAuthForm):
    if user.email and user.password and user.password_confirmation:
        if user.password != user.password_confirmation:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las contraseñas no son iguales")
        if len(user.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña debe tener 8 caracteres como mínimo")
        user_database = await User.by_email(user.email)
        if user_database:
            if user_database.active == False:
                user_database.password = get_password_hash(user.password)
                user_database.active = True
                user_database.updatedAt= time_at()
                await user_database.replace()
                return {"message" : "Validación correcta"}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya ha sido validado")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no existe")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credenciales incorrectas")
 
 

@authentication_router.post("/login", status_code=status.HTTP_200_OK)
async def login_for_access_token(user_form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    UserEmail(email=user_form_data.username)

    if user_form_data.username and user_form_data.password:
        user_database = await authenticate_user(user_form_data.username, user_form_data.password)
        if user_database:
            token = create_access_token(data={"sub": str(user_database.id)})
            token_model = Token(access_token=token, token_type="bearer")
            refresh_token = create_refresh_token(data={"sub": str(user_database.id)})            
            response = JSONResponse(token_model.model_dump(), status_code=status.HTTP_200_OK)
            response.set_cookie(key="refresh-Token", value=refresh_token, httponly=True, max_age=REFRESH_TOKEN_EXPIRE_MINUTES*60)
            return response
        else:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email o contraseña no proporcionados"
            )


@authentication_router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_token(refresh_token: str = Depends(check_cookie)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token no encontrado")
    decoded_token = await decode_token(refresh_token, type='refresh')
    if not decoded_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token inválido")
    user = await User.get(decoded_token.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado para ese Refresh Token")
    access_token = create_access_token(data={"sub": str(user.id)})
    token_model = Token(access_token=access_token, token_type="bearer")
    return token_model.model_dump()


@authentication_router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(user_form: UserForm, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):
    if user_form.email and user_form.full_name and user_form.role:
        user = await User.by_email(user_form.email)
        if user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The user already exists.")
        time_now=time_at()
        new_user = User(email=user_form.email, full_name=user_form.full_name, role=user_form.role, createdAt=time_now, updatedAt=time_now)
        await new_user.create()
        return {"message": "User created successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, full name or role not provided"
            )

@authentication_router.get("/info", status_code=status.HTTP_200_OK)
async def get_user_info(user: Annotated[UserByToken, Depends(get_current_user)]):
    return user

@authentication_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    response = JSONResponse({"message": "Session closed successfully"})
    response.delete_cookie(key="refresh-Token", httponly=True)
    return response

@authentication_router.get("/test")
async def hello(current_user: Annotated[UserByToken, Depends(get_current_user)]) -> str:
    return current_user
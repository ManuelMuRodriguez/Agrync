"""
Configuración central de fixtures para todos los tests.

Estrategia de base de datos:
  - Se utiliza mongomock-motor para emular MongoDB en memoria.
  - init_beanie se llama una vez por test para garantizar un estado limpio.
  - Se construye una mini-app FastAPI sin el lifespan de producción para
    evitar conexiones reales a MongoDB, OPC, etc.
"""
import os

# ── Variables de entorno ANTES de cualquier import del proyecto ───────────────
os.environ.setdefault("ACCESS_TOKEN_SECRET_KEY", "test_access_secret_key_32chars!!")
os.environ.setdefault("REFRESH_TOKEN_SECRET_KEY", "test_refresh_secret_key_32chars!")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
# Variables necesarias para que los módulos de tareas no fallen al importar
os.environ.setdefault("RECONNECTION_TIME", "5")
os.environ.setdefault("OPCUA_IP_PORT", "4840")
os.environ.setdefault("URL_ADMIN", "opc.tcp://localhost:{OPCUA_IP_PORT}")
os.environ.setdefault("URL", "opc.tcp://localhost:{OPCUA_IP_PORT}")
os.environ.setdefault("CERT", "certificate/my_cert.der")
os.environ.setdefault("PRIVATE_KEY", "certificate/private_key.pem")
os.environ.setdefault("CLIENT_CERT", "certificate/client_cert.der")
os.environ.setdefault("CLIENT_APP_URI", "urn:test:client")
os.environ.setdefault("USERNAME_OPC_ADMIN", "admin")
os.environ.setdefault("PASSWORD_OPC_ADMIN", "password")
os.environ.setdefault("URI", "urn:test:server")
os.environ.setdefault("LOG_CONFIG", "logging.conf")
os.environ.setdefault("LOG_MODBUS", "ModbusLogger")
os.environ.setdefault("LOG_OPC_FIWARE", "OPCtoFIWARELogger")
os.environ.setdefault("FIWARE_URL", "http://orion:1026")
os.environ.setdefault("FIWARE_SERVICE", "test")
os.environ.setdefault("FIWARE_SERVICE_PATH", "/test")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "fake_token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "0")
os.environ.setdefault("ALERT_INTERVAL", "60")

import pytest
import pytest_asyncio
import mongomock_motor
from beanie import init_beanie
from fastapi import FastAPI, Depends
from httpx import AsyncClient, ASGITransport
from typing import Annotated

from pydantic import ValidationError
from fastapi import Request
from fastapi.responses import JSONResponse
from models.user import User, Role
from models.task import Task, NameTask, State
from models.modbus import ModbusDevice
from models.generic import GenericDevice, HistoricalVariable, LastVariable
from utils.password import get_password_hash
from utils.datetime import time_at
from routers.auth import (
    authentication_router,
    get_current_user,
    get_current_admin_user,
    get_current_admin_or_editor_user,
)
from routers.user import users_router
from routers.task import tasks_router
from routers.modbus import modbus_router
from routers.generic import generic_router

_DOCUMENT_MODELS = [
    User, Task, ModbusDevice, GenericDevice, HistoricalVariable, LastVariable
]


def build_test_app() -> FastAPI:
    """App mínima sin lifespan para tests (sin conexión a MongoDB real ni OPC)."""
    app = FastAPI()

    # Replica el handler de ValidationError de main.py
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": [{"msg": err["msg"], "type": err["type"]} for err in exc.errors()]},
        )

    # modbus_router requiere admin al igual que en main.py
    app.include_router(authentication_router)
    app.include_router(users_router)
    app.include_router(tasks_router)
    app.include_router(modbus_router, dependencies=[Depends(get_current_admin_user)])
    app.include_router(generic_router)
    return app


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    """Base de datos limpia en memoria para cada test."""
    client = mongomock_motor.AsyncMongoMockClient()
    await init_beanie(database=client.test_agrync, document_models=_DOCUMENT_MODELS)


@pytest_asyncio.fixture
async def http_client(init_db):
    """Cliente HTTP apuntando a la app de test."""
    app = build_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── Fixtures de usuarios ──────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def admin_user(init_db) -> User:
    user = User(
        email="admin@example.com",
        full_name="Admin Test",
        role=Role.admin,
        password=get_password_hash("AdminPass123"),
        active=True,
        createdAt=time_at(),
        updatedAt=time_at(),
    )
    await user.create()
    return user


@pytest_asyncio.fixture
async def editor_user(init_db) -> User:
    user = User(
        email="editor@example.com",
        full_name="Editor Test",
        role=Role.editor,
        password=get_password_hash("EditorPass123"),
        active=True,
        createdAt=time_at(),
        updatedAt=time_at(),
    )
    await user.create()
    return user


@pytest_asyncio.fixture
async def inactive_user(init_db) -> User:
    user = User(
        email="inactive@example.com",
        full_name="Inactive User",
        role=Role.viewer,
        active=False,
        createdAt=time_at(),
        updatedAt=time_at(),
    )
    await user.create()
    return user


@pytest_asyncio.fixture
async def admin_token(http_client, admin_user) -> str:
    """Devuelve un access token JWT válido para el usuario admin."""
    resp = await http_client.post(
        "/auth/login",
        data={"username": admin_user.email, "password": "AdminPass123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def editor_token(http_client, editor_user) -> str:
    resp = await http_client.post(
        "/auth/login",
        data={"username": editor_user.email, "password": "EditorPass123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── Fixtures de tareas ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def stopped_modbus_task(init_db) -> Task:
    return await Task.create_task(NameTask.modbus)


@pytest_asyncio.fixture
async def running_modbus_task(init_db) -> Task:
    task = await Task.create_task(NameTask.modbus)
    await task.start_task(pid=99999)
    return task

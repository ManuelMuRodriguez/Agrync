from contextlib import asynccontextmanager
import uvicorn
import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Request, HTTPException, status, Depends
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware
from routers.auth import authentication_router, get_current_admin_user
from routers.user import users_router, create_initial_admin
from routers.modbus import modbus_router
from routers.task import tasks_router, init_tasks, stop_all_tasks
from routers.generic import generic_router
from routers.fiware import fiware_router
from routers.opc import opc_router
from models.user import User
from models.modbus import ModbusDevice
from models.task import Task
from models.generic import GenericDevice, HistoricalVariable, LastVariable
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import time


DESCRIPTION = """
API for collecting values from various IFAPA IoT devices using multiple communication protocols

"""


@asynccontextmanager
async def lifespan(app: FastAPI): 
    """ODM and database initialization"""
    #app.db = AsyncIOMotorClient("mongodb://localhost:27017").agrync 
    app.db = AsyncIOMotorClient("mongodb://mongodb:27017").agrync 
    await init_beanie(app.db, document_models=[User, ModbusDevice, Task, GenericDevice, HistoricalVariable, LastVariable])
    await init_tasks()
    await create_initial_admin()
    print("Startup complete")
    yield
    await stop_all_tasks()
    print("Shutdown complete")
 



origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]
 

app = FastAPI(
    title="APYNC",
    description=DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Juan Javier León Ibáñez",
        "email": "jli301@inlumine.ual.es",
    },
    lifespan=lifespan,
    root_path="/api/v1"

)



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(authentication_router)
app.include_router(users_router)
app.include_router(modbus_router, dependencies=[Depends(get_current_admin_user)])
app.include_router(tasks_router)
app.include_router(generic_router)
app.include_router(fiware_router)
app.include_router(opc_router)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB



@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {"loc": error["loc"], "message": error["msg"], "type": error["type"]}
                for error in exc.errors()
            ],
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {"loc": error["loc"], "message": error["msg"], "type": error["type"]}
                for error in exc.errors()
            ],
        },
    )
    
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
    
    return await call_next(request)

@app.middleware("http")
async def agregar_tiempo_procesamiento(request: Request, call_next):
    start = time.time()
    answer = await call_next(request)
    time_ms = (time.time() - start) * 1000
    print(f"Tiempo para procesar la solicitud y devolver la respuesta: {time_ms:.2f} ms")
    return answer

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, lifespan="on")

import sys
import os
import subprocess
import psutil
from psutil import Process
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketException, WebSocketDisconnect, Depends
from starlette.websockets import WebSocketState
from models.task import Task, State, NameTask, State, TaskState
import asyncio
from models.user import UserByToken, User
from routers.auth import get_current_admin_user, decode_token
from models.user import Role
from typing import Annotated
import json

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_script_path(name: NameTask) -> str:
    script_path = f"tasks/{name.value}.py"
    return script_path

def stop_process(process: Process):
    process.terminate()
    try:
        process.wait(timeout=3)
    except psutil.TimeoutExpired:
        process.kill()


async def search_task(name: NameTask, script_path: str) -> Task | None:

    print("Directorio actual:", os.getcwd())

    if not os.path.exists(script_path ):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Script '{script_path}' no encontrado.")

    return await Task.by_name(name.value)



def launch_process(script_path: str):
    if sys.platform == "win32":
        print("WindowsProcess")
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        print(f"Script: {script_path}")
        print(f"{type(script_path)}")
        process = subprocess.Popen(
            #sys.executable
            #[sys.executable,script_path],
            [sys.executable, "-m" ,script_path],
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True
        )

    else:
        print("LinuxProcess")
        print(f"Ejecutando script: {script_path}")
        process = subprocess.Popen(
            [sys.executable, "-m",script_path],
            start_new_session=True,
            #stdout=subprocess.PIPE,
            #stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
    
    return process


@tasks_router.post("/{name}/start")
async def start_task_endpoint(name: NameTask, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):


    script_path = get_script_path(name)

    task = await search_task(name, script_path)

    script_path = script_path.replace(".py", "").replace("/", ".")

    if task:
        
        if task.locked == False:

            try:

                if task.pid:

                    process = psutil.Process(task.pid)
                    print(process.is_running())
                    if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                        return {"message": f"Task '{name.value}' is already running"}

            except psutil.NoSuchProcess:
                pass

            #process = launch_process(script_path)
            #await task.start_task(process.pid)


            are_tasks_locked_running = await Task.any_locked_running()

            print(are_tasks_locked_running)

            if are_tasks_locked_running == False:
                tasks_locked = await Task.get_all_locked()

                for locked_task in tasks_locked:
                    script_locked_path = get_script_path(locked_task.name)
                    script_locked_path = script_locked_path.replace(".py", "").replace("/", ".")
                    try:

                        if locked_task.pid:

                            process_locked = psutil.Process(locked_task.pid)
                            if process_locked.is_running() and process_locked.status() != psutil.STATUS_ZOMBIE:
                                continue

                    except psutil.NoSuchProcess:
                        pass

                    process_locked = launch_process(script_locked_path)
                    await locked_task.start_task(process_locked.pid)

                process = launch_process(script_path)
                await task.start_task(process.pid)

                return {"message": f"Task '{name.value}' started along with its dependencies"}
            
            process = launch_process(script_path)
            await task.start_task(process.pid)

            return {"message": f"Task '{name.value}' started"}
        
        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Task '{name.value}' cannot be started directly")

    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Task '{name.value}' does not exist")

        

    



@tasks_router.post("/{name}/stop")
async def stop_task_endpoint(name: NameTask, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):
    
    script_path = get_script_path(name)

    task = await search_task(name, script_path)

    if task:

        if task.locked == False:

            try:
                process = psutil.Process(task.pid)
                if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                    stop_process(process)
                    await task.stop_task()

                    are_tasks_unlocked_running = await Task.any_unlocked_running()
 
                    if are_tasks_unlocked_running == False:
                        tasks_locked = await Task.get_all_locked()
 
                        for locked_task in tasks_locked:
                            try:
                                process_locked = psutil.Process(locked_task.pid)

                                if process_locked.is_running() and process_locked.status() != psutil.STATUS_ZOMBIE:
                                    stop_process(process_locked)
                                    await locked_task.stop_task()
                            except psutil.NoSuchProcess:
                                pass  

                        return {"message": f"Task '{name.value}' stopped along with its dependencies"}
                     
                    return {"message": f"Task '{name.value}' stopped"}
            except:
                pass
            

            if(task.state == State.stopped):
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Task '{name.value}' was already stopped")
            else:
                await task.fail_task()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Task '{name.value}' has failed")

        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Task '{name.value}' cannot be stopped directly")

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{name.value}' does not exist")
    
async def get_state(task: Task):
    process = psutil.Process(task.pid)
    if task.state == State.running:
        if not process.is_running() or process.status() == psutil.STATUS_ZOMBIE:
            task.state = State.failed
            await task.replace()
            
    return task.state

async def init_tasks():
    for name in NameTask:
        existing = await Task.by_name(name)
        if not existing:
            await Task.create_task(name)
        else:
            await existing.stop_task()


async def stop_all_tasks():
    for name in NameTask:
        existing = await Task.by_name(name)
        if existing:
            await existing.stop_task()

@tasks_router.get("/{name}/state", status_code=status.HTTP_200_OK, response_model=TaskState)
async def get_task_state(name: NameTask, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):

    task = await Task.by_name(name)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{name.value}' does not exist")
       
            
    state = await get_state(task)

    locked = task.locked
    
    return TaskState(state=state, locked=locked)
        


LOG_PATHS = {
    NameTask.modbus: "tasks/logModbus/Modbus.log",
    NameTask.opcToFiware: "tasks/logOPCtoFIWARE/OPCtoFIWARE.log",
    NameTask.serverOPC: "tasks/logServer/ServerOPC.log"
}


async def log_reader(log_file_path: str, n=5):
    log_lines = []

    
    try:
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()[-n:]
            for line in lines:
                if "ERROR" in line:
                    log_lines.append(f'<span style="color: #f87171;">{line}</span><br/>')
                elif "WARNING" in line:
                    log_lines.append(f'<span style="color: #fbbf24;">{line}</span><br/>')
                else:
                    log_lines.append(f"{line}<br/>")
    except FileNotFoundError as exc:
        print("Directorio actual:", os.getcwd())
        raise HTTPException(status_code=404, detail=f"Archivo de logs no encontrado: {log_file_path}. {exc}")
    except Exception as exc:
        print("Directorio actual:", os.getcwd())
        raise HTTPException(status_code=500, detail=f"Error interno al leer el archivo de logs. {exc}")

    return log_lines

@tasks_router.websocket("/ws/log/{log_task}")
async def websocket_endpoint_log(websocket: WebSocket, log_task: NameTask):

    #auth_header = websocket.headers.get("Authorization")
    #if not auth_header or not auth_header.startswith("Bearer "):
    #    await websocket.close(code=1008)
    #    return

    #token = auth_header[len("Bearer "):]


    #decoded_data = await decode_token(token=token)

    #user = None

    #if decoded_data:
    #    user = await User.get(decoded_data.id)
    #    if user is None:
    #        await websocket.close(code=1008)
    #        return

    #if user is None:
    #    await websocket.close(code=1008)
    #    return
            
    #if user.role != Role.admin:
    #    await websocket.close(code=1008)
    #    return



    log_file_path = LOG_PATHS.get(log_task) 

    if not log_file_path:
        raise HTTPException(status_code=404, detail="Tipo de log no encontrado")


    await websocket.accept()

    try:

        data = await websocket.receive_text()
        msg = json.loads(data)
        token = msg.get("token")
        if not token:
            await websocket.close(code=1008) 
            return

        decoded_data = await decode_token(token=token)

        user = None
        if decoded_data:
            user = await User.get(decoded_data.id)
            if user is None:
                await websocket.close(code=1008)
                return

        if user is None or user.role != Role.admin:
            await websocket.close(code=1008)
            return


        while True:
            logs = await log_reader(log_file_path, 30)
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text("".join(logs)) 

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Cliente desconectado")
    except WebSocketException as exc:
        print(f"Error relacionado con websocket: ({exc})")
    except Exception as exc:
        print(f"Error general durante la lectura de logs: ({exc})")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass
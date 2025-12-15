from beanie import Document, Indexed
from enum import Enum
from datetime import datetime
from typing import Annotated, Optional
from utils.datetime import time_at
from pydantic import Field
from utils.datetime import time_at
from pydantic import BaseModel
from beanie.operators import And

class State(str, Enum):
    running = 'running'
    stopped = 'stopped'
    failed = 'failed'

class NameTask(str, Enum):
    serverOPC = "ServerOPC"
    modbus = "Modbus"
    opcToFiware = "OPCtoFIWARE"

class Task(Document):
    name: Annotated[NameTask, Indexed(unique=True)]
    pid: int | None = None
    state: State
    locked: bool = False
    createdAt: datetime = Field(default_factory=time_at)
    updatedAt: datetime = Field(default_factory=time_at)
    
    def __repr__(self) -> str:
        return f"<Task {self.name}: {self.state}>"

    def __str__(self) -> str:
        return f"{self.name}: {self.state}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Task):
            return self.name == other.name
        return False

    @classmethod
    async def by_name(cls, name: NameTask) -> Optional["Task"]:
        """Get a task by name."""
        return await cls.find_one(cls.name == name)

    @classmethod
    async def create_task(cls, name: NameTask):

        new_task = cls(
            name=name.value,
            state=State.stopped
        )

        if name == NameTask.serverOPC or name == NameTask.opcToFiware:
            new_task.locked = True

        await new_task.create()
        return new_task

    @classmethod
    async def any_locked_running(cls) -> bool:
        return await cls.find_one(And(cls.state == State.running, cls.locked == True)) is not None

    @classmethod
    async def any_unlocked_running(cls) -> bool:
        return await cls.find_one(And(cls.state == State.running, cls.locked == False)) is not None

    @classmethod
    async def get_all_locked(cls):
        tasks = await cls.find(cls.locked == True).to_list()
        return tasks

    async def update_state(self, new_state: State, pid: int = None):
        self.state = new_state
        self.updatedAt = time_at()
        self.pid = pid
        await self.replace()

    async def stop_task(self):
        await self.update_state(State.stopped, None)
        return self
    
    async def start_task(self, pid: int = None):
        await self.update_state(State.running, pid)
        return self

    async def fail_task(self):
        await self.update_state(State.failed, None)
        return self




class TaskState(BaseModel):
    state: State
    locked: bool
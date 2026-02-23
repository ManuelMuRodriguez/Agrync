"""
Tests para los modelos de dominio (Beanie Documents y Pydantic models).
Se cubre la lógica de negocio: métodos de clase, estados de Task, validadores de Modbus, etc.
"""
import pytest
from models.task import Task, NameTask, State
from models.user import User, Role
from models.modbus import VariableUpdate
from utils.password import get_password_hash
from utils.datetime import time_at


# ── Task model ────────────────────────────────────────────────────────────────

class TestTaskModel:
    async def test_create_task_sets_stopped_state(self):
        task = await Task.create_task(NameTask.modbus)
        assert task.state == State.stopped

    async def test_create_task_modbus_is_not_locked(self):
        task = await Task.create_task(NameTask.modbus)
        assert task.locked is False

    async def test_create_task_server_opc_is_locked(self):
        task = await Task.create_task(NameTask.serverOPC)
        assert task.locked is True

    async def test_create_task_opc_to_fiware_is_locked(self):
        task = await Task.create_task(NameTask.opcToFiware)
        assert task.locked is True

    async def test_by_name_returns_correct_task(self):
        await Task.create_task(NameTask.modbus)
        found = await Task.by_name(NameTask.modbus)
        assert found is not None
        assert found.name == NameTask.modbus

    async def test_by_name_returns_none_if_not_found(self):
        result = await Task.by_name(NameTask.modbus)
        assert result is None

    async def test_start_task_sets_running_and_pid(self):
        task = await Task.create_task(NameTask.modbus)
        await task.start_task(pid=1234)
        assert task.state == State.running
        assert task.pid == 1234

    async def test_stop_task_sets_stopped_and_clears_pid(self):
        task = await Task.create_task(NameTask.modbus)
        await task.start_task(pid=1234)
        await task.stop_task()
        assert task.state == State.stopped
        assert task.pid is None

    async def test_fail_task_sets_failed_state(self):
        task = await Task.create_task(NameTask.modbus)
        await task.start_task(pid=1234)
        await task.fail_task()
        assert task.state == State.failed

    async def test_any_locked_running_false_when_none_running(self):
        await Task.create_task(NameTask.serverOPC)
        result = await Task.any_locked_running()
        assert result is False

    async def test_any_locked_running_true_when_locked_task_running(self):
        task = await Task.create_task(NameTask.serverOPC)
        await task.start_task(pid=9999)
        result = await Task.any_locked_running()
        assert result is True

    async def test_any_unlocked_running_false_when_none_running(self):
        await Task.create_task(NameTask.modbus)
        result = await Task.any_unlocked_running()
        assert result is False

    async def test_any_unlocked_running_true_when_unlocked_task_running(self):
        task = await Task.create_task(NameTask.modbus)
        await task.start_task(pid=8888)
        result = await Task.any_unlocked_running()
        assert result is True

    async def test_get_all_locked_returns_only_locked(self):
        await Task.create_task(NameTask.modbus)         # no locked
        await Task.create_task(NameTask.serverOPC)      # locked
        await Task.create_task(NameTask.opcToFiware)    # locked
        locked = await Task.get_all_locked()
        assert len(locked) == 2
        for t in locked:
            assert t.locked is True

    async def test_update_state_persists_to_db(self):
        task = await Task.create_task(NameTask.modbus)
        await task.update_state(State.running, pid=777)
        refreshed = await Task.by_name(NameTask.modbus)
        assert refreshed.state == State.running
        assert refreshed.pid == 777


# ── User model ────────────────────────────────────────────────────────────────

class TestUserModel:
    async def test_by_email_returns_user(self):
        user = User(
            email="test@example.com",
            full_name="Test User",
            role=Role.viewer,
            active=True,
            createdAt=time_at(),
            updatedAt=time_at(),
        )
        await user.create()
        found = await User.by_email("test@example.com")
        assert found is not None
        assert str(found.email) == "test@example.com"

    async def test_by_email_returns_none_if_not_found(self):
        result = await User.by_email("noexiste@example.com")
        assert result is None

    async def test_user_starts_inactive_by_default(self):
        user = User(
            email="nuevo@example.com",
            full_name="Nuevo",
            role=Role.viewer,
        )
        assert user.active is False

    async def test_find_by_device_name(self):
        user = User(
            email="device@example.com",
            full_name="Device User",
            role=Role.editor,
            active=True,
            devices=["sensor-01", "sensor-02"],
            createdAt=time_at(),
            updatedAt=time_at(),
        )
        await user.create()
        results = await User.find_by_device_name("sensor-01")
        assert len(results) == 1
        assert str(results[0].email) == "device@example.com"

    async def test_find_by_device_name_no_match(self):
        results = await User.find_by_device_name("dispositivo-inexistente")
        assert results == []


# ── VariableUpdate validator (Modbus) ─────────────────────────────────────────

class TestVariableUpdateValidator:
    def test_valid_name_accepted(self):
        v = VariableUpdate(name="Sensor_01")
        assert v.name == "Sensor_01"

    def test_name_with_spaces_becomes_underscores(self):
        v = VariableUpdate(name="  Sensor 01  ")
        assert v.name == "Sensor_01"

    def test_name_with_hyphen_raises(self):
        with pytest.raises(Exception):
            VariableUpdate(name="Sensor-01")

    def test_name_with_invalid_chars_raises(self):
        with pytest.raises(Exception):
            VariableUpdate(name="Sensor@01!")

    def test_interval_must_be_greater_than_one(self):
        with pytest.raises(Exception):
            VariableUpdate(interval=1)

    def test_interval_zero_raises(self):
        with pytest.raises(Exception):
            VariableUpdate(interval=0)

    def test_valid_interval_accepted(self):
        v = VariableUpdate(interval=5)
        assert v.interval == 5

    def test_min_greater_than_max_raises(self):
        with pytest.raises(Exception):
            VariableUpdate(min_value=100.0, max_value=10.0)

    def test_only_min_without_max_raises(self):
        with pytest.raises(Exception):
            VariableUpdate(min_value=5.0)

    def test_only_max_without_min_raises(self):
        with pytest.raises(Exception):
            VariableUpdate(max_value=100.0)

    def test_both_min_and_max_valid(self):
        v = VariableUpdate(min_value=0.0, max_value=100.0)
        assert v.min_value == 0.0
        assert v.max_value == 100.0

    def test_unit_strips_whitespace(self):
        v = VariableUpdate(unit="  ºC  ")
        assert v.unit == "ºC"

    def test_unit_empty_string_becomes_none(self):
        v = VariableUpdate(unit="   ")
        assert v.unit is None

    def test_all_none_is_valid(self):
        v = VariableUpdate()
        assert v.name is None
        assert v.interval is None

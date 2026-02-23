"""
Tests for the tasks router (/tasks).

Calls to psutil and subprocess are mocked to avoid
interactions with the real operating system.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient
from models.task import Task, NameTask, State


# ── GET /{name}/state ─────────────────────────────────────────────────────────

class TestGetTaskState:
    async def test_get_state_stopped_task(
        self, http_client: AsyncClient, admin_token, stopped_modbus_task
    ):
        resp = await http_client.get(
            f"/tasks/{NameTask.modbus.value}/state",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["state"] == State.stopped.value
        assert body["locked"] is False

    async def test_get_state_task_not_in_db_returns_404(
        self, http_client: AsyncClient, admin_token
    ):
        resp = await http_client.get(
            f"/tasks/{NameTask.modbus.value}/state",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404

    async def test_get_state_without_auth_returns_401(
        self, http_client: AsyncClient, stopped_modbus_task
    ):
        resp = await http_client.get(f"/tasks/{NameTask.modbus.value}/state")
        assert resp.status_code == 401

    async def test_get_state_running_task_with_live_process(
        self, http_client: AsyncClient, admin_token, running_modbus_task
    ):
        """If the PID exists and is running, the state should be 'running'."""
        mock_process = MagicMock()
        mock_process.is_running.return_value = True
        mock_process.status.return_value = "running"

        with patch("routers.task.psutil.Process", return_value=mock_process):
            resp = await http_client.get(
                f"/tasks/{NameTask.modbus.value}/state",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 200
        assert resp.json()["state"] == State.running.value

    @pytest.mark.xfail(
        reason="Bug #4: get_state() no captura psutil.NoSuchProcess; lanza 500 en lugar de devolver state=failed. Corregir antes de quitar este mark.",
        strict=True,
    )
    async def test_get_state_running_task_with_dead_process_becomes_failed(
        self, http_client: AsyncClient, admin_token, running_modbus_task
    ):
        """If the process no longer exists, the state should be updated to 'failed'."""
        import psutil
        with patch("routers.task.psutil.Process", side_effect=psutil.NoSuchProcess(pid=99999)):
            resp = await http_client.get(
                f"/tasks/{NameTask.modbus.value}/state",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 200
        assert resp.json()["state"] == State.failed.value

    async def test_get_state_locked_task(
        self, http_client: AsyncClient, admin_token
    ):
        task = await Task.create_task(NameTask.serverOPC)
        resp = await http_client.get(
            f"/tasks/{NameTask.serverOPC.value}/state",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["locked"] is True


# ── POST /{name}/start ────────────────────────────────────────────────────────

class TestStartTask:
    def _mock_process(self, pid: int = 12345) -> MagicMock:
        mp = MagicMock()
        mp.pid = pid
        mp.is_running.return_value = False
        mp.status.return_value = "sleeping"
        return mp

    async def test_start_stopped_task_returns_200(
        self, http_client: AsyncClient, admin_token, stopped_modbus_task
    ):
        fake_proc = self._mock_process(12345)
        with patch("routers.task.launch_process", return_value=fake_proc), \
             patch("routers.task.Task.any_locked_running", return_value=False), \
             patch("routers.task.Task.get_all_locked", return_value=[]):
            resp = await http_client.post(
                f"/tasks/{NameTask.modbus.value}/start",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 200
        assert "started" in resp.json()["message"].lower()

    async def test_start_already_running_task_returns_message(
        self, http_client: AsyncClient, admin_token, running_modbus_task
    ):
        """If the process is still alive, it should not be relaunched."""
        mock_proc = MagicMock()
        mock_proc.is_running.return_value = True
        mock_proc.status.return_value = "running"
        with patch("routers.task.psutil.Process", return_value=mock_proc):
            resp = await http_client.post(
                f"/tasks/{NameTask.modbus.value}/start",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 200
        assert "running" in resp.json()["message"].lower()

    async def test_start_nonexistent_task_returns_406(
        self, http_client: AsyncClient, admin_token
    ):
        resp = await http_client.post(
            f"/tasks/{NameTask.modbus.value}/start",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 406

    async def test_start_locked_task_directly_returns_406(
        self, http_client: AsyncClient, admin_token
    ):
        await Task.create_task(NameTask.serverOPC)
        resp = await http_client.post(
            f"/tasks/{NameTask.serverOPC.value}/start",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 406

    async def test_start_task_without_auth_returns_401(
        self, http_client: AsyncClient, stopped_modbus_task
    ):
        resp = await http_client.post(f"/tasks/{NameTask.modbus.value}/start")
        assert resp.status_code == 401


# ── POST /{name}/stop ─────────────────────────────────────────────────────────

class TestStopTask:
    async def test_stop_running_task(
        self, http_client: AsyncClient, admin_token, running_modbus_task
    ):
        mock_proc = MagicMock()
        mock_proc.is_running.return_value = True
        mock_proc.status.return_value = "running"

        with patch("routers.task.psutil.Process", return_value=mock_proc), \
             patch("routers.task.stop_process"), \
             patch("routers.task.Task.any_unlocked_running", return_value=False), \
             patch("routers.task.Task.get_all_locked", return_value=[]):
            resp = await http_client.post(
                f"/tasks/{NameTask.modbus.value}/stop",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 200
        assert "stopped" in resp.json()["message"].lower()

    async def test_stop_already_stopped_task_returns_406(
        self, http_client: AsyncClient, admin_token, stopped_modbus_task
    ):
        import psutil
        with patch("routers.task.psutil.Process", side_effect=psutil.NoSuchProcess(pid=0)):
            resp = await http_client.post(
                f"/tasks/{NameTask.modbus.value}/stop",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 406
        assert "stopped" in resp.json()["detail"].lower()

    async def test_stop_locked_task_directly_returns_406(
        self, http_client: AsyncClient, admin_token
    ):
        await Task.create_task(NameTask.serverOPC)
        resp = await http_client.post(
            f"/tasks/{NameTask.serverOPC.value}/stop",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 406

    async def test_stop_nonexistent_task_returns_404(
        self, http_client: AsyncClient, admin_token
    ):
        resp = await http_client.post(
            f"/tasks/{NameTask.modbus.value}/stop",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404

    async def test_stop_task_without_auth_returns_401(
        self, http_client: AsyncClient, running_modbus_task
    ):
        resp = await http_client.post(f"/tasks/{NameTask.modbus.value}/stop")
        assert resp.status_code == 401

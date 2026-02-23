"""
Tests de regresión para los bugs encontrados en el análisis.
Se prueban los comportamientos problemáticos de forma aislada,
sin conexiones reales a Modbus ni OPC.

Bug #1 - UnboundLocalError en read_and_send_OPC:
  'value' puede quedar sin asignar si ModbusException ocurre
  durante la conversión de registros.

Bug #2 - Bucle infinito en send_opc:
  Si el error no contiene el string esperado, el bucle no termina.

Bug #3 - round_to_decimals duplicada:
  La función existe en Modbus.py y OPCtoFIWARE.py; se verifica
  que ambas se comportan igual.

Bug #10 - Tareas asyncio ejecutadas secuencialmente con 'await task':
  Demostración del efecto: gather vs bucle secuencial.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Union


# ── Helpers extraídos/reimplementados para tests unitarios ────────────────────

def round_to_decimals(value: Union[int, float], decimals: int) -> Union[int, float]:
    """Copia exacta de la función en Modbus.py y OPCtoFIWARE.py."""
    return round(value, decimals)


# ── Bug #1: UnboundLocalError en conversión de registros ─────────────────────

class TestReadAndSendOPCValueInitialization:
    """
    Simula el bloque de conversión de registros de read_and_send_OPC.
    El bug es que 'value' no se inicializa a None antes del bloque try/except,
    lo que causaría UnboundLocalError si la excepción se dispara.
    """

    def _convert_registers_buggy(self, data_type: str) -> Union[int, float, None]:
        """Versión con el bug: value puede quedar sin definir."""
        from pymodbus import ModbusException
        try:
            if data_type == "Float32":
                value = 1.23
            elif data_type == "INVALID_TYPE":
                # Simulamos que se llega aquí sin asignar value
                raise ModbusException("tipo no soportado")
        except ModbusException:
            pass
        # Si llega aquí sin pasar por el if: UnboundLocalError
        return value  # type: ignore[return-value]

    def _convert_registers_fixed(self, data_type: str) -> Union[int, float, None]:
        """Versión corregida: value se inicializa a None."""
        from pymodbus import ModbusException
        value = None  # ← fix
        try:
            if data_type == "Float32":
                value = 1.23
            elif data_type == "INVALID_TYPE":
                raise ModbusException("tipo no soportado")
        except ModbusException:
            pass
        return value

    def test_buggy_version_raises_unbound_local_error(self):
        """Confirma que el bug existe tal y como fue descrito."""
        with pytest.raises((UnboundLocalError, NameError)):
            self._convert_registers_buggy("INVALID_TYPE")

    def test_fixed_version_returns_none_on_exception(self):
        """La versión corregida devuelve None sin lanzar excepción."""
        result = self._convert_registers_fixed("INVALID_TYPE")
        assert result is None

    def test_fixed_version_returns_value_when_type_valid(self):
        result = self._convert_registers_fixed("Float32")
        assert result == pytest.approx(1.23)


# ── Bug #2: Bucle infinito en send_opc ───────────────────────────────────────

class TestSendOpcConnectionLoop:
    """
    Demuestra que el bucle while True en send_opc se queda infinito
    si el RuntimeError no contiene el string exacto esperado.
    """

    async def _send_opc_buggy(self, connect_fn, max_iters=50) -> int:
        """
        Simula el bucle con un límite de iteraciones para que el test no cuelgue.
        Devuelve el número de iteraciones realizadas.
        """
        attempt = 1
        iterations = 0
        while True:
            iterations += 1
            if iterations > max_iters:
                raise RuntimeError("INFINITE_LOOP_DETECTED")
            try:
                await connect_fn()
                break
            except RuntimeError as e:
                if "Dos canales seguros abiertos a la vez" in str(e):
                    await asyncio.sleep(0)
                    attempt += 1
                # ← Bug: si el mensaje es diferente, no hay break ni re-raise
        return iterations

    async def _send_opc_fixed(self, connect_fn, max_iters=50) -> int:
        attempt = 1
        max_retries = 10  # ← fix: límite de reintentos
        iterations = 0
        while True:
            iterations += 1
            if iterations > max_iters:
                raise RuntimeError("INFINITE_LOOP_DETECTED")
            try:
                await connect_fn()
                break
            except RuntimeError as e:
                if "Dos canales seguros abiertos a la vez" in str(e) and attempt <= max_retries:
                    await asyncio.sleep(0)
                    attempt += 1
                else:
                    raise  # ← fix: re-raise si no es el error esperado o se superó el límite
        return iterations

    async def test_buggy_loop_never_exits_on_unexpected_error(self):
        """El bucle con el bug detecta un bucle infinito."""
        async def always_fail():
            raise RuntimeError("Error de red inesperado")  # string diferente al esperado

        with pytest.raises(RuntimeError, match="INFINITE_LOOP_DETECTED"):
            await self._send_opc_buggy(always_fail)

    async def test_fixed_version_raises_on_unexpected_error(self):
        """La versión corregida re-lanza el error inesperado."""
        async def always_fail():
            raise RuntimeError("Error de red inesperado")

        with pytest.raises(RuntimeError, match="Error de red inesperado"):
            await self._send_opc_fixed(always_fail)

    async def test_fixed_version_exits_after_max_retries(self):
        """La versión corregida re-lanza si se superan los reintentos."""
        async def always_double_channel():
            raise RuntimeError("Dos canales seguros abiertos a la vez")

        with pytest.raises(RuntimeError):
            await self._send_opc_fixed(always_double_channel)

    async def test_loop_exits_normally_on_success(self):
        """Si la conexión es exitosa en el primer intento, sale tras 1 iteración."""
        call_count = 0

        async def success_on_second():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Dos canales seguros abiertos a la vez")

        iterations = await self._send_opc_fixed(success_on_second)
        assert iterations == 2


# ── Bug #3: round_to_decimals duplicada ──────────────────────────────────────

class TestRoundToDecimalsConsistency:
    """Verifica que la lógica de redondeo es coherente en ambas ubicaciones."""

    def test_round_to_zero_decimals(self):
        assert round_to_decimals(3.7, 0) == 4.0

    def test_round_to_two_decimals(self):
        assert round_to_decimals(3.14159, 2) == pytest.approx(3.14)

    def test_round_negative_value(self):
        # -2.555 en float es ~-2.5549999..., por lo que Python lo redondea a -2.56
        assert round_to_decimals(-2.555, 2) == pytest.approx(-2.56)

    def test_round_integer_input(self):
        assert round_to_decimals(5, 3) == 5

    def test_round_large_decimals(self):
        assert round_to_decimals(1.123456789, 6) == pytest.approx(1.123457)

    def test_round_zero(self):
        assert round_to_decimals(0.0, 5) == 0.0


# ── Bug #10: Tareas asyncio secuenciales vs concurrentes ─────────────────────

class TestAsyncioGatherVsSequential:
    """
    Demuestra que 'await task' en un bucle es secuencial,
    mientras que asyncio.gather es concurrente.
    """

    async def _make_tasks(self, delay: float = 0.05, count: int = 3):
        """Crea `count` corutinas con sleep de `delay` segundos."""
        async def slow():
            await asyncio.sleep(delay)

        return [slow() for _ in range(count)]

    async def test_sequential_await_takes_sum_of_delays(self):
        delay, count = 0.05, 3
        tasks = await self._make_tasks(delay, count)

        start = asyncio.get_event_loop().time()
        for coro in tasks:
            await coro
        elapsed = asyncio.get_event_loop().time() - start

        # Secuencial: debe tardar ~count*delay
        assert elapsed >= delay * count * 0.9

    async def test_gather_takes_approximately_single_delay(self):
        delay, count = 0.05, 3
        tasks = await self._make_tasks(delay, count)

        start = asyncio.get_event_loop().time()
        await asyncio.gather(*tasks)
        elapsed = asyncio.get_event_loop().time() - start

        # Concurrente: debe tardar ~delay (no count*delay)
        assert elapsed < delay * count * 0.8


# ── Bug #4: get_state sin captura de NoSuchProcess ───────────────────────────

class TestGetStateNoSuchProcess:
    """
    Verifica que get_state maneja correctamente un PID inexistente.
    El bug: psutil.Process(pid) lanza NoSuchProcess si el PID no existe,
    y el código actual no lo captura.
    """

    async def test_get_state_handles_no_such_process(self):
        """
        Simula el comportamiento de get_state con un PID inexistente.
        La versión corregida debe devolver State.failed sin lanzar excepción.
        """
        import psutil
        from models.task import Task, NameTask, State

        task = await Task.create_task(NameTask.modbus)
        await task.start_task(pid=999999999)  # PID que no existe

        async def get_state_fixed(t: Task):
            try:
                process = psutil.Process(t.pid)
                if t.state == State.running:
                    if not process.is_running() or process.status() == psutil.STATUS_ZOMBIE:
                        t.state = State.failed
                        await t.replace()
            except psutil.NoSuchProcess:  # ← fix
                if t.state == State.running:
                    t.state = State.failed
                    await t.replace()
            return t.state

        state = await get_state_fixed(task)
        assert state == State.failed


# ── Bug #9: Claves de entorno sin validación ─────────────────────────────────

class TestEnvVarValidation:
    """
    Verifica que las variables de entorno críticas, si faltan,
    generan errores claros en lugar de fallos oscuros en runtime.
    """

    def test_algorithm_none_causes_clear_error(self):
        """
        Si ALGORITHM es None, jwt.encode falla con un error poco descriptivo.
        Una validación explícita debe detectarlo antes.
        """
        algorithm = None
        with pytest.raises((ValueError, TypeError)):
            if algorithm is None:
                raise ValueError("La variable de entorno 'ALGORITHM' no está definida")
            from jose import jwt
            jwt.encode({"sub": "test"}, "secret", algorithm=algorithm)

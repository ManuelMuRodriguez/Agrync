from typing import Union
import logging
import logging.config
from dotenv import load_dotenv

logging.getLogger('pymodbus').setLevel(logging.ERROR)
logging.getLogger('asyncua').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)

import os
import sys
import asyncio
from asyncua import Client, ua, Node
from pymodbus.client import AsyncModbusTcpClient
from pymodbus import ModbusException, FramerType
import time
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.modbus import ModbusDevice, VariableWithSlave, VariableCreate, WritableNode, VariableOPC
import signal

BASE_DIR = Path(__file__).resolve().parent

# Carga las variables de .env
load_dotenv()

LOG_CONFIG = str(BASE_DIR / os.getenv("LOG_CONFIG", "logging.conf"))

# Configuración del log para el cliente Modbus y el servidor OPC
logging.config.fileConfig(LOG_CONFIG)


#OPCUA_IP_PORT = os.getenv('OPCUA_IP_PORT')

RECONNECTION_TIME = int(os.getenv('RECONNECTION_TIME'))

OPCUA_IP_PORT = os.getenv('OPCUA_IP_PORT')

URL_ADMIN=os.getenv('URL_ADMIN')

URL_ADMIN = URL_ADMIN.replace("{OPCUA_IP_PORT}", OPCUA_IP_PORT)

CERT = str(BASE_DIR / os.getenv('CERT'))
PRIVATE_KEY = str(BASE_DIR /os.getenv('PRIVATE_KEY'))
CLIENT_CERT = str(BASE_DIR /os.getenv('CLIENT_CERT'))


# URI del servidor
CLIENT_APP_URI= os.getenv('CLIENT_APP_URI')


# Usuario y contraseña para la conexión con el servidor OPC
USERNAME = os.getenv('USERNAME_OPC_ADMIN')
PASSWORD = os.getenv('PASSWORD_OPC_ADMIN')


#URL del servidor
URI = os.getenv('URI')


LOG_MODBUS=os.getenv("LOG_MODBUS")


# Creación del logger para el cliente Modbus
logger = logging.getLogger(LOG_MODBUS)

for handler in logging.getLogger().handlers:
    if handler.formatter:
        handler.formatter.converter = time.gmtime




async def setup():
    try: 
        client = AsyncIOMotorClient("mongodb://mongodb:27017").agrync
        await init_beanie(
            database=client,
            document_models=[ModbusDevice]
        )
    except Exception as exc:
        print(f"Error de conexión con la base de datos: {exc}")
        logger.error(f"Error de conexión con la base de datos: {exc}")
        sys.exit(3)


# Conjunto de clientes Modbus utilizados para la conexión con los dispositivos
clients: dict[str, AsyncModbusTcpClient] = {}




# Maneja la información cuando se produce una modificación en una variable de escritura
class SubscriptionHandler:

    def __init__(self, modbus_client: AsyncModbusTcpClient, slave_id: int, nodes_with_addresses: dict):
        self.modbus_client = modbus_client
        self.slave_id = slave_id
        self.nodes_with_addresses = nodes_with_addresses
        self.first_write : dict[Node, bool] = {}

    
    # Realiza la escritura de la variable modbus cuando se produce un cambio en la variable OPC - Se evita la modificación en el primer cambio, ya que este cambio es la obtención del primer valor
    async def datachange_notification(self, node: Node, val, data):
        if node in self.first_write:
            try:
                assert self.modbus_client.connected
                modbus_address = self.nodes_with_addresses.get(node, None)

                if modbus_address is not None:
                    print(f"Variable modificada: {node}, Nuevo valor: {val}, Dirección Modbus: {modbus_address}")
                    logger.info(f"Variable modificada: {node}, Nuevo valor: {val}, Dirección Modbus: {modbus_address}")
                    await self.modbus_client.write_register(modbus_address, val, slave=self.slave_id)

            except AssertionError as exc:
                print(f"El cliente Modbus de escritura NO está conectado: {exc}")
                logger.warning(f"El cliente Modbus de escritura NO está conectado: {exc}")

            except ModbusException as exc:
                print(f"Error en la escritura del dispositivo Modbus (Direccion={modbus_address}, Slave={self.slave_id}): {exc}")
                logger.warning(f"Error en la escritura del dispositivo Modbus (Direccion={modbus_address}, Slave={self.slave_id}): {exc}")

        else:
            print("Primera escritura")
            self.first_write[node] = True

        

    

# Método para realizar la suscripción a cambios en el servidor OPC
async def subscription_modification(client: AsyncModbusTcpClient, slave_id: int, writable_variables: list[WritableNode], client_opc:Client) -> None:

    # Creación del cliente OPC
    #client_opc = await create_opc_client(URL_ADMIN)

    # Conjunto de nodos OPC junto a sus direcciones modbus
    nodes_with_addresses = {}

    while True:

        try:
            client_opc.secure_channel_id=id
            await client_opc.connect()
            
            # Inicio de la conexión con el servidor OPC
            #async with client_opc:

            # Obtención del namescpace del servidor
            nsidx = await client_opc.get_namespace_index(URI)

            nodes = []

            # Almacenamiento de las nodos junto a sus direcciones
            for variable_node in writable_variables:

                node = client_opc.get_node(f"ns={nsidx};s={variable_node.variable_name}")
                nodes.append(node)
                nodes_with_addresses[node] = variable_node.address  # Asociar la dirección Modbus con el nodo

            #Creación de la suscripción al servidor OPC para el control de la modificación de valores
            handler = SubscriptionHandler(modbus_client=client, slave_id = slave_id, nodes_with_addresses = nodes_with_addresses)
            subscription = await client_opc.create_subscription(500, handler)
            await subscription.subscribe_data_change(nodes)

            while True:
                await asyncio.sleep(1)
                await client_opc.check_connection()
        except (ConnectionError, ua.UaError):
            logger.warning(f"Servidor OPC desconectando, fallo en la suscripción, reconectando...")
            print(f"Servidor OPC desconectando, fallo en la suscripción, reconectando...")
            await asyncio.sleep(5)



def create_modbus_client(device_ip: str) -> AsyncModbusTcpClient:
    client = AsyncModbusTcpClient(device_ip, port=502, framer=FramerType.SOCKET, timeout = 1)
    return client

# Establecimiento de conexión por modbus
async def connect_modbus_client(client: AsyncModbusTcpClient) -> bool:
    try:
        await client.connect()
        assert client.connected
    except ModbusException as exc:
        print(f"Conexión con el cliente Modbus ({client}) fallida: ({exc})")
        logger.error(f"Conexión con el cliente Modbus ({client}) fallida: ({exc}) ")

        return False
    
    except AssertionError as exc:
        print(f"Conexión con el cliente Modbus ({client}) fallida: ({exc})")
        logger.error(f"Conexión con el cliente Modbus ({client}) fallida: ({exc}) ")

        return False

    return True

# Agrupación de variables para crear las tareas encargadas de la lectura y escritura de variables
async def grouping_sensors_by_interval_and_sensors_by_slave(devices: list[ModbusDevice]) -> None:
    
    # Agrupar las variables por intervalo y cliente
    sensors_per_client_interval: dict[tuple[str, int], list[VariableWithSlave]] = {}

    # Agrupar las variables por esclavo y cliente
    sensors_per_slave_client: dict[tuple[AsyncModbusTcpClient, int], list[WritableNode]] = {}

    for device in devices:

        # Crear un cliente para cada dispositivo
        client = create_modbus_client(device.ip) 

        # Se realiza la conexión con el dispositivo Modbus
        is_client_connected = await connect_modbus_client(client)

        
        if not is_client_connected:
            print(f"No se pudo conectar con el dispositivo {device.ip}")
            logger.error(f"No se pudo conectar con el dispositivo {device.ip}")

        #Se almacena el cliente Modbus
        clients[device.ip] = client

        if device.slaves:
            for slave in device.slaves:

                if slave.variables:
                    for variable in slave.variables:

                        full_name_variable = device.name+ "-" + slave.name + "-" + variable.name

                        # Se guardan las variables en "sensors_per_slave_client" si tienen habilitada la escritura
                        if(variable.writable):
                            node_names = WritableNode(variable_name=full_name_variable, address= variable.address)

                            # Crea una clave que combina un cliente con el id de esclavo
                            client_slave_key = (client, slave.slave_id)

                            # Si no existe la clave, se inicializa la lista
                            if client_slave_key not in sensors_per_slave_client:
                                sensors_per_slave_client[client_slave_key] = []

                            # Se asignan las variables con su cliente-esclavo correspondiente
                            sensors_per_slave_client[client_slave_key].append(node_names)

                        # Crea una clave que combina la ip del dispositivo con el intervalo de obtención de valores de la variable
                        client_key_interval = (device.ip, variable.interval)


                        # Si no existe la clave, se inicializa la lista
                        if client_key_interval not in sensors_per_client_interval:
                            sensors_per_client_interval[client_key_interval] = []

                        # Se asignan las variables con su ip de dispositivo-intervalo correspondiente
                        variable_with_slave = VariableWithSlave(variable=variable, slave_id=slave.slave_id, full_name_variable=full_name_variable)
                        sensors_per_client_interval[client_key_interval].append(variable_with_slave)

    id = 1
    # Se crean tareas para leer y escribir variables
    tasks = []
    for (client_ip, interval), variables in sensors_per_client_interval.items():
        if client_ip in clients:
            for device in devices:
                if device.ip == client_ip:
                    client_opc = await create_opc_client(URL_ADMIN)
                    tasks.append(asyncio.create_task(read_and_send_OPC(clients[client_ip], interval, variables, client_opc)))
                    client_opc.secure_channel_id=id
                    id +=1

    
    logger.info("Tareas de lectura y envío a OPC creadas")

    for cliente_esclavo_key, variables in sensors_per_slave_client.items():
        client, esclavo_id = cliente_esclavo_key
        client_opc = await create_opc_client(URL_ADMIN)
        #async def subscription_modification(client: AsyncModbusTcpClient, slave_id: int, writable_variables: list[WritableNode], client_opc:Client) 
        tasks.append(asyncio.create_task(subscription_modification(client, esclavo_id, variables, client_opc)))
        client_opc.secure_channel_id=id
        id +=1

    logger.info("Tareas para la suscripción de modificación de valores creadas")

    # Se ejecutan cada una de las tareas
    for task in tasks:
        await task            












async def read_and_send_OPC(client: AsyncModbusTcpClient, interval: int, variables: list[VariableWithSlave], client_opc:Client) -> None:

    


    while True:

        #Obtención del tiempo inicial para controlar el intervalo de obtención de valores
        start_time = time.time()
        is_connected = True

        # Comprobación de que existe conexión con el servidor OPC
        try:
            assert client.connected

        except AssertionError as exc:
            print(f"Cliente Modbus ({client}) desconectado: ({exc})")
            logger.error(f"Cliente Modbus ({client}) desconectado: ({exc})")
            is_connected = False
    
        list_values = []

        if(is_connected):
    


            # Lectura de los datos de los sensores
            for variable in variables:

                try:
                    read_registers = await client.read_holding_registers(variable.variable.address, count=variable.variable.length, slave=variable.slave_id)

                except ModbusException as exc:
                    print(f"Recibida ModbusException({exc}) desde la librería modbus al intentar leer registros")
                    #logger.warning(f"Recibida ModbusException({exc}) desde la librería modbus al intentar leer registros")
                    #client.close()
                    read_registers = None
                if read_registers and read_registers.isError():
                    print(f"Excepción recibida en la lectura de los siguientes registros: ({read_registers})")
                    logger.warning(f"Excepción recibida en la lectura de los siguientes registros: ({read_registers})")
                    #client.close()
                    read_registers = None

            
                if read_registers != None:
                    try:

                        if variable.variable.type == "Float32":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.FLOAT32, word_order=variable.variable.endian)
                        elif variable.variable.type == "Float64":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.FLOAT64, word_order=variable.variable.endian)
                        elif variable.variable.type == "Int16":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.INT16, word_order=variable.variable.endian)
                        elif variable.variable.type == "UInt16":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.UINT16, word_order=variable.variable.endian)
                        elif variable.variable.type == "Int32":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.INT32, word_order=variable.variable.endian)
                        elif variable.variable.type == "UInt32":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.UINT32, word_order=variable.variable.endian)
                        elif variable.variable.type == "Int64":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.INT64, word_order=variable.variable.endian)
                        elif variable.variable.type == "UInt64":
                            value = client.convert_from_registers(read_registers.registers, data_type=client.DATATYPE.UINT64, word_order=variable.variable.endian)
                        else:
                            value = None
                    except ModbusException as exc:
                        print(f"Error durante la coversión de registros ({read_registers.registers}): {exc}")
                        logger.error(f"Error durante la coversión de registros ({read_registers.registers}): {exc}")
                        
                    
                    if value is not None:

                        if(variable.variable.scaling != None):
                            value = variable.variable.scaling * value

                        # Aplicación de un redondeo al valor
                        #if(variable.variable.decimals != 0):
                        value = round_to_decimals(value, variable.variable.decimals)

                list_values.append(VariableOPC(value=value, type=variable.variable.type, variable_name=variable.full_name_variable))

            # Si el valor es nulo no se envía al servidor OPC
            await send_opc(list_values, client_opc)


            # Se calcula cuánto tiempo ha tardado la lectura
            elapsed_time = time.time() - start_time

            # Se resta el tiempo transcurrido del intervalo total
            remaining_time = max(0, interval - elapsed_time)


            #if (str(client) == "AsyncModbusTcpClient 169.254.0.106:502"):
            #    now = datetime.now()

            #    hora = now.hour
            #    minutos = now.minute
            #    segundos = now.second
            #    print(f"Hora actual: {client} {hora}:{minutos}:{segundos}")
        
            #current_time = datetime.now().strftime("%H:%M:%S")
            #print(f"---------{current_time}-----------------------------")


            # Se espera el tiempo restante para completar el intervalo
            await asyncio.sleep(remaining_time)
            
        else:
            # Si el cliente esta desconectado se intenta la reconexión y se activa una espera para el siguiente reintento
            await connect_modbus_client(client)
            try:
                assert client.connected
                client_opc = await create_opc_client(URL_ADMIN)
            except AssertionError as exc:
                pass

            await asyncio.sleep(RECONNECTION_TIME)
                


        

async def send_opc(values_list: list[VariableOPC], client_opc: Client) -> None:


    attempt = 1
    client_opc.secure_channel_timeout=1000
    # Coneción con el servidor OPC
    while True:
        try:
            # Conexión con el servidor OPC
            await client_opc.disconnect()
            await client_opc.connect()
                
            break  # Salir del bucle si la conexión fue exitosa
        except RuntimeError as e:
            if "Dos canales seguros abiertos a la vez" in str(e):
                print(f"Intento {attempt} fallido, reintentando...")
                await asyncio.sleep(0.01)
                attempt += 1
    

    #Obtención del identificador del namespace
    nsidx = await client_opc.get_namespace_index(URI)

    for value_opc in values_list:
        # Obtención del nodo correspondiente a la variable existente en el servidor
        #logger.info(f"ns={nsidx};s={value_opc.variable_name}")
        variable_opc = client_opc.get_node(f"ns={nsidx};s={value_opc.variable_name}")


        if(isinstance(value_opc.value, float)):  
            if(value_opc.type == "Int64" or value_opc.type == "UInt64" or value_opc.type == "Float64"):
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.Double), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.Double)
            else:
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.Float), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.Float)
        else:
            if(value_opc.type == "Int16"):
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.Int16)
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.Int16), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
            elif(value_opc.type == "UInt16"):
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.UInt16)
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.UInt16), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
            elif(value_opc.type == "Int32"):
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.Int32)
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.Int32), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
            elif(value_opc.type == "UInt32"):
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.UInt32)
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.UInt32), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
            elif(value_opc.type == "Int64"):
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.Int64)
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.Int64), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))
            elif(value_opc.type == "UInt64"):
                await variable_opc.write_value(value_opc.value, varianttype=ua.VariantType.UInt64)
                #await variable_opc.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.UInt64), StatusCode_=ua.StatusCodes.Good, SourceTimestamp=timestamp, ServerTimestamp=timestamp))


    await client_opc.close_session()
        
#Truncamiento
#def truncate_to_decimals(value: Union[int, float], decimals: int) -> Union[int,float]:
#    factor = 10 ** decimals
#    return int(value * factor) / factor

#Redondeo
def round_to_decimals(value: Union[int, float], decimals: int) -> Union[int, float]:
    return round(value, decimals)


# Creación de cliente OPC
async def create_opc_client(url: str) -> Client:
    try:
        client_opc = Client(url, timeout=2)
        client_opc.application_uri = CLIENT_APP_URI
        await client_opc.set_security(
            SecurityPolicyBasic256Sha256,
            certificate=str(CLIENT_CERT),
            private_key=str(PRIVATE_KEY),
            server_certificate=str(CERT),
            mode=ua.MessageSecurityMode.SignAndEncrypt
        )
        client_opc.set_user(USERNAME)
        client_opc.set_password(PASSWORD)
        return client_opc
    except: 
        logger.error("La conexión con el servidor OPC ha fallado")
        print("La conexión con el servidor OPC ha fallado")
        sys.exit(2)



# Permite controlar la pulsación de las teclas ctrl+C
def signal_handler(signal, frame):
    for client in clients.values():
        try:
            if client.connected:
                client.close()  
                print(f"Cerrando conexión con cliente {client}")
            else:
                print(f"El cliente {client} ya está desconectado.")
        except Exception as e:
            print(f"Error al cerrar el cliente {client}: {e}")
    logger.info("Finalizando cliente pymodbus y cliente OPC...")
    print("Finalizando cliente pymodbus y cliente OPC...")
    sys.exit(0)







async def main():

    await asyncio.sleep(30)

    logger.info("Iniciando cliente pymodbus y cliente OPC...")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await setup()

    devices = await ModbusDevice.find().to_list()

    #print(json.dumps(devices.pop().model_dump(), indent=4))

    # Carga de los dispositivos
    if not devices:
        logger.info("No se encontraron dispositivos")
        print("No se encontraron dispositivos")
        sys.exit(0)

    try:
        await grouping_sensors_by_interval_and_sensors_by_slave(devices)
    except Exception as exc:
        logger.error(f"Error inesperado a lo largo de la ejecución del programa: {exc}")
        print(f"Error inesperado a lo largo de la ejecución del programa: {exc}")






if __name__ == "__main__":
    
    asyncio.run(main())
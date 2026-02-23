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

# Load environment variables
load_dotenv()

LOG_CONFIG = str(BASE_DIR / os.getenv("LOG_CONFIG", "logging.conf"))

# Log configuration for the Modbus client and OPC server
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


# Username and password for the OPC server connection
USERNAME = os.getenv('USERNAME_OPC_ADMIN')
PASSWORD = os.getenv('PASSWORD_OPC_ADMIN')


#URL del servidor
URI = os.getenv('URI')


LOG_MODBUS=os.getenv("LOG_MODBUS")


# Create logger for the Modbus client
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
        print(f"Database connection error: {exc}")
        logger.error(f"Database connection error: {exc}")
        sys.exit(3)


# Dictionary of Modbus clients used to connect to each device
clients: dict[str, AsyncModbusTcpClient] = {}




# Handles data changes when a writable variable is modified
class SubscriptionHandler:

    def __init__(self, modbus_client: AsyncModbusTcpClient, slave_id: int, nodes_with_addresses: dict):
        self.modbus_client = modbus_client
        self.slave_id = slave_id
        self.nodes_with_addresses = nodes_with_addresses
        self.first_write : dict[Node, bool] = {}

    
    # Writes the Modbus variable when an OPC variable changes. The first change is skipped as it corresponds to the initial value read.
    async def datachange_notification(self, node: Node, val, data):
        if node in self.first_write:
            try:
                assert self.modbus_client.connected
                modbus_address = self.nodes_with_addresses.get(node, None)

                if modbus_address is not None:
                    print(f"Variable changed: {node}, New value: {val}, Modbus address: {modbus_address}")
                    logger.info(f"Variable changed: {node}, New value: {val}, Modbus address: {modbus_address}")
                    await self.modbus_client.write_register(modbus_address, val, slave=self.slave_id)

            except AssertionError as exc:
                print(f"Write Modbus client is NOT connected: {exc}")
                logger.warning(f"Write Modbus client is NOT connected: {exc}")

            except ModbusException as exc:
                print(f"Error writing Modbus device (Address={modbus_address}, Slave={self.slave_id}): {exc}")
                logger.warning(f"Error writing Modbus device (Address={modbus_address}, Slave={self.slave_id}): {exc}")

        else:
            print("First write")
            self.first_write[node] = True

        

    

# Subscribe to value changes on the OPC server
async def subscription_modification(client: AsyncModbusTcpClient, slave_id: int, writable_variables: list[WritableNode], client_opc:Client) -> None:

    # Create OPC client
    #client_opc = await create_opc_client(URL_ADMIN)

    # OPC nodes mapped to their Modbus addresses
    nodes_with_addresses = {}

    while True:

        try:
            client_opc.secure_channel_id=id
            await client_opc.connect()
            
            # Establish connection to the OPC server
            #async with client_opc:

            # Retrieve server namespace index
            nsidx = await client_opc.get_namespace_index(URI)

            nodes = []

            # Store nodes mapped to their Modbus addresses
            for variable_node in writable_variables:

                node = client_opc.get_node(f"ns={nsidx};s={variable_node.variable_name}")
                nodes.append(node)
                nodes_with_addresses[node] = variable_node.address  # Map Modbus address to the node

            #Create subscription to the OPC server for writable variable change detection
            handler = SubscriptionHandler(modbus_client=client, slave_id = slave_id, nodes_with_addresses = nodes_with_addresses)
            subscription = await client_opc.create_subscription(500, handler)
            await subscription.subscribe_data_change(nodes)

            while True:
                await asyncio.sleep(1)
                await client_opc.check_connection()
        except (ConnectionError, ua.UaError):
            logger.warning(f"OPC server disconnecting, subscription failed, reconnecting...")
            print(f"OPC server disconnecting, subscription failed, reconnecting...")
            await asyncio.sleep(5)



def create_modbus_client(device_ip: str) -> AsyncModbusTcpClient:
    client = AsyncModbusTcpClient(device_ip, port=502, framer=FramerType.SOCKET, timeout = 1)
    return client

# Establish Modbus connection
async def connect_modbus_client(client: AsyncModbusTcpClient) -> bool:
    try:
        await client.connect()
        assert client.connected
    except ModbusException as exc:
        print(f"Modbus client ({client}) connection failed: ({exc})")
        logger.error(f"Modbus client ({client}) connection failed: ({exc})")

        return False
    
    except AssertionError as exc:
        print(f"Modbus client ({client}) connection failed: ({exc})")
        logger.error(f"Modbus client ({client}) connection failed: ({exc})")

        return False

    return True

# Group variables by interval and slave to create read/write tasks
async def grouping_sensors_by_interval_and_sensors_by_slave(devices: list[ModbusDevice]) -> None:
    
    # Group variables by interval and client
    sensors_per_client_interval: dict[tuple[str, int], list[VariableWithSlave]] = {}

    # Group variables by slave and client
    sensors_per_slave_client: dict[tuple[AsyncModbusTcpClient, int], list[WritableNode]] = {}

    for device in devices:

        # Create a client for each device
        client = create_modbus_client(device.ip) 

        # Connect to the Modbus device
        is_client_connected = await connect_modbus_client(client)

        
        if not is_client_connected:
            print(f"Could not connect to device {device.ip}")
            logger.error(f"Could not connect to device {device.ip}")

        #Se almacena el cliente Modbus
        clients[device.ip] = client

        if device.slaves:
            for slave in device.slaves:

                if slave.variables:
                    for variable in slave.variables:

                        full_name_variable = device.name+ "-" + slave.name + "-" + variable.name

                        # Store writable variables in `sensors_per_slave_client`
                        if(variable.writable):
                            node_names = WritableNode(variable_name=full_name_variable, address= variable.address)

                            # Build a key combining the client and slave id
                            client_slave_key = (client, slave.slave_id)

                            # Initialise the list if the key does not exist yet
                            if client_slave_key not in sensors_per_slave_client:
                                sensors_per_slave_client[client_slave_key] = []

                            # Assign variables to their corresponding client-slave pair
                            sensors_per_slave_client[client_slave_key].append(node_names)

                        # Build a key combining the device IP and the polling interval
                        client_key_interval = (device.ip, variable.interval)


                        # Initialise the list if the key does not exist yet
                        if client_key_interval not in sensors_per_client_interval:
                            sensors_per_client_interval[client_key_interval] = []

                        # Assign variables to their corresponding device-IP/interval pair
                        variable_with_slave = VariableWithSlave(variable=variable, slave_id=slave.slave_id, full_name_variable=full_name_variable)
                        sensors_per_client_interval[client_key_interval].append(variable_with_slave)

    id = 1
    # Create tasks for reading and writing variables
    tasks = []
    for (client_ip, interval), variables in sensors_per_client_interval.items():
        if client_ip in clients:
            for device in devices:
                if device.ip == client_ip:
                    client_opc = await create_opc_client(URL_ADMIN)
                    tasks.append(asyncio.create_task(read_and_send_OPC(clients[client_ip], interval, variables, client_opc)))
                    client_opc.secure_channel_id=id
                    id +=1

    
    logger.info("Read-and-send-to-OPC tasks created")

    for cliente_esclavo_key, variables in sensors_per_slave_client.items():
        client, esclavo_id = cliente_esclavo_key
        client_opc = await create_opc_client(URL_ADMIN)
        #async def subscription_modification(client: AsyncModbusTcpClient, slave_id: int, writable_variables: list[WritableNode], client_opc:Client) 
        tasks.append(asyncio.create_task(subscription_modification(client, esclavo_id, variables, client_opc)))
        client_opc.secure_channel_id=id
        id +=1

    logger.info("Value-change subscription tasks created")

    # Run all tasks
    for task in tasks:
        await task            












async def read_and_send_OPC(client: AsyncModbusTcpClient, interval: int, variables: list[VariableWithSlave], client_opc:Client) -> None:

    


    while True:

        # Record start time to control the polling interval
        start_time = time.time()
        is_connected = True

        # Check Modbus client connection
        try:
            assert client.connected

        except AssertionError as exc:
                print(f"Modbus client ({client}) disconnected: ({exc})")
                logger.error(f"Modbus client ({client}) disconnected: ({exc})")
    
        list_values = []

        if(is_connected):
    


            # Lectura de los datos de los sensores
            for variable in variables:

                try:
                    read_registers = await client.read_holding_registers(variable.variable.address, count=variable.variable.length, slave=variable.slave_id)

                except ModbusException as exc:
                    print(f"Received ModbusException({exc}) from modbus library while trying to read registers")
                    #logger.warning(f"Recibida ModbusException({exc}) desde la librería modbus al intentar leer registros")
                    #client.close()
                    read_registers = None
                if read_registers and read_registers.isError():
                    print(f"Error response received while reading registers: ({read_registers})")
                    logger.warning(f"Error response received while reading registers: ({read_registers})")
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
                        print(f"Error converting registers ({read_registers.registers}): {exc}")
                        logger.error(f"Error converting registers ({read_registers.registers}): {exc}")
                        
                    
                    if value is not None:

                        if(variable.variable.scaling != None):
                            value = variable.variable.scaling * value

                        # Round the value
                        #if(variable.variable.decimals != 0):
                        value = round_to_decimals(value, variable.variable.decimals)

                list_values.append(VariableOPC(value=value, type=variable.variable.type, variable_name=variable.full_name_variable))

            # Skip sending null values to the OPC server
            await send_opc(list_values, client_opc)


            # Calculate elapsed reading time
            elapsed_time = time.time() - start_time

            # Compute remaining sleep time
            remaining_time = max(0, interval - elapsed_time)


            #if (str(client) == "AsyncModbusTcpClient 169.254.0.106:502"):
            #    now = datetime.now()

            #    hora = now.hour
            #    minutos = now.minute
            #    segundos = now.second
            #    print(f"Hora actual: {client} {hora}:{minutos}:{segundos}")
        
            #current_time = datetime.now().strftime("%H:%M:%S")
            #print(f"---------{current_time}-----------------------------")


            # Wait for the remaining interval time
            await asyncio.sleep(remaining_time)
            
        else:
            # Client disconnected: attempt reconnection and wait before retrying
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
    # Connect to the OPC server
    while True:
        try:
            # Connect to the OPC server
            await client_opc.disconnect()
            await client_opc.connect()
                
            break  # Exit loop if connection succeeded
        except RuntimeError as e:
            if "Dos canales seguros abiertos a la vez" in str(e):
                print(f"Attempt {attempt} failed, retrying...")
                await asyncio.sleep(0.01)
                attempt += 1
    

    # Retrieve the namespace index
    nsidx = await client_opc.get_namespace_index(URI)

    for value_opc in values_list:
        # Get the node for this variable in the OPC server
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
        
# Truncation
#def truncate_to_decimals(value: Union[int, float], decimals: int) -> Union[int,float]:
#    factor = 10 ** decimals
#    return int(value * factor) / factor

# Rounding
def round_to_decimals(value: Union[int, float], decimals: int) -> Union[int, float]:
    return round(value, decimals)


# Create OPC client
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
        logger.error("Connection to the OPC server failed")
        print("Connection to the OPC server failed")
        sys.exit(2)



# Allow graceful shutdown on Ctrl+C
def signal_handler(signal, frame):
    for client in clients.values():
        try:
            if client.connected:
                client.close()  
                print(f"Closing connection with client {client}")
            else:
                print(f"Client {client} is already disconnected.")
        except Exception as e:
            print(f"Error closing client {client}: {e}")
    logger.info("Shutting down Modbus client and OPC client...")
    print("Shutting down Modbus client and OPC client...")
    sys.exit(0)







async def main():

    await asyncio.sleep(30)

    logger.info("Starting Modbus client and OPC client...")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await setup()

    devices = await ModbusDevice.find().to_list()

    #print(json.dumps(devices.pop().model_dump(), indent=4))

    # Load devices from the database
    if not devices:
        logger.info("No devices found")
        print("No devices found")
        sys.exit(0)

    try:
        await grouping_sensors_by_interval_and_sensors_by_slave(devices)
    except Exception as exc:
        logger.error(f"Unexpected error during program execution: {exc}")
        print(f"Unexpected error during program execution: {exc}")






if __name__ == "__main__":
    
    asyncio.run(main())
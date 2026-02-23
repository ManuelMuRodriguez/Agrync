import asyncio
from asyncua import Client, ua
import requests
from dotenv import load_dotenv
import os
from time import time, gmtime
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from pathlib import Path
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import math
from datetime import datetime, timezone
import logging
import logging.config

#logging.getLogger('asyncua').setLevel(logging.ERROR)
#logging.getLogger('asyncio').setLevel(logging.ERROR)

from models.opcToFiware import DeviceResponse, Item
from agrync_backend.models.generic import GenericDevice, DeviceType

BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

LOG_CONFIG = str(BASE_DIR / os.getenv("LOG_CONFIG", "logging.conf"))

logging.config.fileConfig(LOG_CONFIG)


OPCUA_IP_PORT = os.getenv('OPCUA_IP_PORT')

OPC_SERVER_URL = os.getenv('URL').replace("{OPCUA_IP_PORT}", OPCUA_IP_PORT)
CLIENT_APP_URI= os.getenv('CLIENT_APP_URI')
CERT = str(BASE_DIR /Path(os.getenv('CERT')))
PRIVATE_KEY = str(BASE_DIR /Path(os.getenv('PRIVATE_KEY')))
CLIENT_CERT = str(BASE_DIR /Path(os.getenv('CLIENT_CERT')))
USERNAME = os.getenv('USERNAME_OPC_ADMIN')
PASSWORD = os.getenv('PASSWORD_OPC_ADMIN')

#URL del servidor
URI = os.getenv('URI')

FIWARE_URL = os.getenv('FIWARE_URL')
FIWARE_SERVICE = os.getenv('FIWARE_SERVICE')
FIWARE_SERVICE_PATH = os.getenv('FIWARE_SERVICE_PATH')
NAMESPACE_INDEX = 2
GLOBAL_INTERVAL = 30  

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

ALERT_INTERVAL = int(os.getenv('ALERT_INTERVAL')) 

LOG_OPC_FIWARE=os.getenv("LOG_OPC_FIWARE")

logger = logging.getLogger(LOG_OPC_FIWARE)

for handler in logging.getLogger().handlers:
    if handler.formatter:
        handler.formatter.converter = gmtime

headers = {
    "Fiware-Service": FIWARE_SERVICE,
    "Fiware-ServicePath": FIWARE_SERVICE_PATH
}

headers_with_content_type = {
    **headers,
    "Content-Type": "application/json"
}


def round_to_decimals(value: int | float, decimals: int) -> int | float:
    return round(value, decimals)


def delete_all_entities():
    r = requests.get("http://orion:1026/v2/entities", headers={"Accept": "application/json", "Fiware-Service": FIWARE_SERVICE,"Fiware-ServicePath": FIWARE_SERVICE_PATH})
    for entity in r.json():
        eid = entity["id"]
        del_r = requests.delete(f"http://orion:1026/v2/entities/{eid}",headers={"Accept": "application/json", "Fiware-Service": FIWARE_SERVICE,"Fiware-ServicePath": FIWARE_SERVICE_PATH})
        print(f"Entidad eliminada {eid}: {del_r.status_code}")

def delete_all_subscriptions():
    r = requests.get("http://orion:1026/v2/subscriptions", headers={"Accept": "application/json", "Fiware-Service": FIWARE_SERVICE,"Fiware-ServicePath": FIWARE_SERVICE_PATH})
    for sub in r.json():
        sid = sub["id"]
        del_r = requests.delete(f"http://orion:1026/v2/subscriptions/{sid}", headers={"Accept": "application/json", "Fiware-Service": FIWARE_SERVICE,"Fiware-ServicePath": FIWARE_SERVICE_PATH})
        print(f"Suscripción eliminada {sid}: {del_r.status_code}")



def send_telegram_alert(device_name, delta):
    message = f"🚨 *Alarma de restraso en el envío de valores* 🚨\n\nDispositivo: `{device_name}`\nRetraso: `{delta:.2f}` segundos"
    #for chat_id in CHAT_ID:
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram: {response.text}")
            logger.error(f"Telegram: {response.text}")
    except Exception as e:
        print(f"Error enviando mensaje al bot de Telegram: {e}")
        logger.error(f"Error enviando mensaje al bot de Telegram: {e}")

def check_data_delay(device_name, date_time_str, current_time, device_alert_times):


    try:
        device_time = datetime.fromisoformat(date_time_str)
        if device_time.tzinfo is None:
            device_time = device_time.replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Fecha inválida para el dispositivo {device_name}: {date_time_str}")
        logger.error(f"Fecha inválida para el dispositivo {device_name}: {date_time_str}")
        return

    now = datetime.now(timezone.utc)
    delta = abs((now - device_time).total_seconds())

    #print(f"Delta: {delta}")
    #print(f"Now: {now}")
    #print(f"Device_time: {device_time}")

    if delta > 30:

        if device_name not in device_alert_times:
            device_alert_times[device_name] = current_time
            send_telegram_alert(device_name, delta)
            #print(f"El dispositivo {device_name} lleva {delta} segundos sin actualizar su valor en el servidor")
            #logger.error(f"El dispositivo {device_name} lleva {delta} segundos sin actualizar su valor en el servidor")
            return device_alert_times


    
        if current_time - device_alert_times[device_name] > ALERT_INTERVAL:
            send_telegram_alert(device_name, delta)
            device_alert_times[device_name] = current_time
            #print(f"El dispositivo {device_name} lleva {delta} segundos sin actualizar su valor en el servidor")
            #logger.error(f"El dispositivo {device_name} lleva {delta} segundos sin actualizar su valor en el servidor")
        #else:
            #print(f"El dispositivo {device_name} lleva {delta} segundos sin actualizar su valor en el servidor")
            #logger.error(f"El dispositivo {device_name} lleva {delta} segundos sin actualizar su valor en el servidor")

    return device_alert_times  





#{"idPattern": ".*"}
# {"id": entity_id}

async def create_fiware_subscription():
    subscription = {
        "description": "Notificar a FastAPI cuando cambie cualquier atributo",
        "subject": {
            "entities": [
                {"idPattern": ".*"}
            ],
            "condition": {
                "attrs": []  
            }
        },
        "notification": {
            "http": {
                "url": "http://backend:8000/fiware/subscription" 
            },
            "attrsFormat": "normalized"
        },
        "throttling": 0 
    }



    response = requests.post(
        "http://orion:1026/v2/subscriptions",
        headers=headers_with_content_type,
        json=subscription
    )

    if response.status_code in [201, 204]:
        print("Suscripción creada correctamente.")
        logger.info("Suscripción creada correctamente.")
    else:
        print(f"Error al crear la suscripción: {response.status_code} - {response.text}")
        logger.error(f"Error al crear la suscripción: {response.status_code} - {response.text}")





async def setup():
    try: 
        await create_fiware_subscription()
        client = AsyncIOMotorClient("mongodb://mongodb:27017").agrync
        await init_beanie(
            database=client,
            document_models=[GenericDevice]
        )
    except Exception as exc:
        print(f"Error de conexión con la base de datos: {exc}")
        logger.error(f"Error de conexión con la base de datos: {exc}")
        sys.exit(3)


#def load_config(path=PATH_FILE_CONFIGURATION):
#    with open(path, "r") as f:
#        return json.load(f)


def build_fiware_attributes(data_collected: list[Item], generical_device_name: str ) -> DeviceResponse:
    attributes = {}
    
    for item in data_collected:
        
        parts = item.full_name.rsplit('-', 1)

        variable_name = parts[1]

        attr_name = f"{variable_name}"
        attributes[attr_name] = {
            "value": item.value,
            "type": item.data_type,
            "metadata": {
                "timestamp": {
                    "type": "DateTime",
                    "value": item.date_time
                }
            }
        }
    return DeviceResponse(id=generical_device_name, type=DeviceType.modbus,  attributes=attributes)

def send_to_fiware(entity: DeviceResponse):
    
    entity_id = entity.id
    try:

        get_url = f"{FIWARE_URL}/{entity_id}"
        response = requests.get(get_url, headers=headers)

        entity_data = entity.model_dump()

        update_payload = {}

        attributes = entity_data.pop('attributes', {})  

        for attr_name, attr_value in attributes.items():
            update_payload[attr_name] = attr_value

        if response.status_code == 404:

            update_payload["id"] = entity_data["id"]
            update_payload["type"] = entity_data["type"]


            create_response = requests.post(FIWARE_URL, headers=headers_with_content_type, json=update_payload)
            print(f"[FIWARE] Entidad creada {entity_id}: {create_response.status_code}")
            print(f"[FIWARE] Respuesta: {create_response.text}")
        elif response.status_code == 200:
            update_url = f"{FIWARE_URL}/{entity_id}/attrs"

            update_response = requests.patch(update_url, headers=headers_with_content_type, json=update_payload)
            print(f"[FIWARE] Entidad actualizada {entity_id}: {update_response.status_code}")
            print(f"[FIWARE] Respuesta: {update_response.text}")
        else:
            print(f"Error en el envío en la entidad {entity_id}: {response.status_code} - {response.text}")
            logger.error(f"Error en el envío en la entidad {entity_id}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error en el envío a FIWARE - {e}")
        logger.error(f"Error en el envío a FIWARE - {e}")


async def create_opc_client(url: str) -> Client:
    try:
        client_opc = Client(url, timeout=1)
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
    except Exception as e:
        print(f"Fallo al configurar el cliente OPC UA: {e}")
        logger.error(f"Fallo al configurar el cliente OPC UA: {e}")


async def main():

    await asyncio.sleep(60)
    
    delete_all_entities()

    delete_all_subscriptions()

    logger.info(f"Entidades y suscripciones previas eliminadas")

    await setup()

    devices = await GenericDevice.find().to_list()

    client = await create_opc_client(url=OPC_SERVER_URL)
    await client.connect()
    NAMESPACE_INDEX = await client.get_namespace_index(URI)
    print("Conexión segura establecida con el servidor OPC")
    logger.info("Conexión segura establecida con el servidor OPC")

    device_alert_times = {}

    while True:
        start_time = time()
        current_time = time()
        try:
            for device in devices:
                data_collected = []

                for variable in device.variables:

                    device_checked = False

                    generical_device_name = device.name
                    full_name = device.name + "-" + variable.name

                    try:
                        nodeid_str = f"ns={NAMESPACE_INDEX};s={full_name}"
                        node = client.get_node(nodeid_str)
                        data_value = await node.read_data_value()

                        date_time = data_value.SourceTimestamp.isoformat(timespec='milliseconds')

                        data_type = data_value.Value.VariantType.name
                        value = data_value.Value.Value

                        if math.isnan(value) or math.isinf(value):
                            value = None


                        if not device_checked:
                            # Call check_data_delay only the first time a variable is processed per device
                            device_alert_times = check_data_delay(generical_device_name, date_time, current_time, device_alert_times)
                            device_checked = True
                        
                        if value is not None:
                            decimals = variable.decimals
                            if(decimals != 0):
                                value= round_to_decimals(value=value, decimals=decimals)



                        data_collected.append(Item(full_name=full_name, value=value, date_time=date_time, data_type=data_type))
                    except Exception as e:
                        print(f"Error en la variable {variable.name}: {e}")
                        logger.error(f"Error en la variable {variable.name}: {e}")

                entity = build_fiware_attributes(data_collected, generical_device_name)
                #print(f"[FIWARE] Entity to send: {json.dumps(entity, indent=4)}")
                send_to_fiware(entity)

        except Exception as e:
            print(f"Error en el envío de los datos: {e}")
            logger.error(f"Error en el envío de los datos: {e}")

        logger.info(f"Envío de los datos realizado")
        elapsed = time() - start_time
        remaining_time = max(0, GLOBAL_INTERVAL - elapsed)
        await asyncio.sleep(remaining_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        import traceback
        print("EXCEPCIÓN EN MAIN:")
        traceback.print_exc()
        logger.error(f"EXCEPCIÓN EN MAIN: {exc}", exc_info=True)
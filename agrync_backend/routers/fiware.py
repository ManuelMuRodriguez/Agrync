from fastapi import APIRouter
from models.generic import LastVariable, HistoricalVariable, ValueWithTimestamp
import asyncio
from datetime import datetime


fiware_router = APIRouter(
    prefix="/fiware",
    tags=["fiware"],)




async def save_last_variable(name: str, value: float | int , timestamp: datetime):
    last_variable = await LastVariable.find_one(LastVariable.name == name)
    
    if last_variable:
        last_variable.value = value
        last_variable.timestamp = timestamp
        await last_variable.replace()
    #else:
    #    last_variable = LastVariable(name=name, value=value, timestamp=timestamp)
    #    await last_variable.insert()

async def save_historical_variable(name: str, value: float | int , timestamp: datetime):
    
    today = timestamp.date()

    historical_variable = await HistoricalVariable.find_one(HistoricalVariable.name == name, HistoricalVariable.day == today)
    
    if historical_variable:
        historical_variable.values.append(ValueWithTimestamp(value=value, timestamp=timestamp))
        await historical_variable.replace()
    else:
        historical_variable = HistoricalVariable(
            name=name,
            values=[ValueWithTimestamp(value=value, timestamp=timestamp)],
            day=today
        )
        await historical_variable.insert()


@fiware_router.post("/subscription")
async def receive_fiware_notification(notification: dict):
    #print("Notificación recibida de FIWARE:", notification)

    for entity in notification.get("data", []):
        entity_id = entity.get("id")
        
        for attr_name, attr_value in entity.items():
            if attr_name != "id" and attr_name != "type": 
                value = attr_value["value"]
                timestamp_str = attr_value["metadata"]["timestamp"]["value"]
                
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

                await asyncio.gather(
                    save_last_variable(name=f"{entity_id}-{attr_name}", value=value, timestamp=timestamp),
                    save_historical_variable(name=f"{entity_id}-{attr_name}", value=value, timestamp=timestamp)
                )


    return {"status": "ok"}  
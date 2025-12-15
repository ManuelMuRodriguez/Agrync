from datetime import datetime, timezone

def time_at() -> datetime:
    date = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    return datetime.fromisoformat(date)


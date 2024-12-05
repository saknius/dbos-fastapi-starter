from datetime import datetime, timezone


CURRENT_TIMESTAMP = lambda: datetime.now(timezone.utc)

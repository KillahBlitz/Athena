import uuid

generate_uuid = lambda prefix="USER": f"{prefix}-{uuid.uuid4()}"
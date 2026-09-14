"""FastAPI ASGI entrypoint."""1

from itsupport_copilot.api.app import create_app

app = create_app()

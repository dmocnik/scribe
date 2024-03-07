from fastapi import FastAPI, Response, Depends
from uuid import UUID, uuid4

from api.verifier import SessionData, backend, cookie, verifier
from api.pages import login

app = FastAPI()

app.include_router(login.account)

# -------------------- test session stuff ---------------------

# @app.post("/create_session/{name}")
# async def create_session(name: str, response: Response):

#     session = uuid4()
#     data = SessionData(username=name)

#     await backend.create(session, data)
#     cookie.attach_to_response(response, session)

#     return f"created session for {name}"

# @app.get("/whoami", dependencies=[Depends(cookie)])
# async def whoami(session_data: SessionData = Depends(verifier)):
#     return session_data


# @app.post("/delete_session")
# async def del_session(response: Response, session_id: UUID = Depends(cookie)):
#     await backend.delete(session_id)
#     cookie.delete_from_response(response)
#     return "deleted session"


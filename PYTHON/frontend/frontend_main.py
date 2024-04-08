from nicegui import ui, app, Client
from middleware import ScribeAuthMiddleware
from pages import login, verify_account, reset_password, index, project
from style import style
from common import check_notifications

app.add_middleware(ScribeAuthMiddleware)

@ui.page('/')
async def _index(client: Client):
    await style()
    await check_notifications()
    await index.content(client)
    
@ui.page('/bruh')
async def _bruh():
    await style()
    await check_notifications()
    ui.image('https://www.oakland.edu/Assets/Oakland/president/graphics/headshots/oraheadshot.jpg')

@ui.page('/login')
async def _login():
    await style()
    await check_notifications()
    await login.content()

@ui.page('/verify-account')
async def _verify_account(client: Client, email: str = None, code: str = None):
    await style()
    await check_notifications()
    await verify_account.content(client, email, code)

@ui.page('/reset-password')
async def _reset_password(client: Client, email: str = None, code: str = None):
    await style()
    await check_notifications()
    await reset_password.content(client, email, code)

@ui.page('/project')
async def _project(client: Client, id: str = None, new: bool = False, name: str = None):
    await style()
    await check_notifications()
    await project.content(client, id, new, name)

ui.run(dark=True, title='Scribe', favicon='📝', storage_secret='this_is_a_secret', host='0.0.0.0', port=8080, show=False)
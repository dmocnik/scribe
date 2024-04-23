from nicegui import ui, app, Client
from middleware import ScribeAuthMiddleware
from pages import login, verify_account, reset_password, index, project
from style import style
from common import check_notifications
from fastapi.responses import RedirectResponse
import os

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
    redirect = False
    if email is not None:
        app.storage.user['email'] = email
        redirect = True
    if code is not None:
        app.storage.user['code'] = code
        redirect = True
    if redirect:
        return RedirectResponse('/verify-account')

    email = app.storage.user.pop('email', None)
    code = app.storage.user.pop('code', None)

    await style()
    await check_notifications()
    await verify_account.content(client, email, code)

@ui.page('/reset-password')
async def _reset_password(client: Client, email: str = None, code: str = None):
    redirect = False
    if email is not None:
        app.storage.user['email'] = email
        redirect = True
    if code is not None:
        app.storage.user['code'] = code
        redirect = True
    if redirect:
        return RedirectResponse('/reset-password')

    email = app.storage.user.pop('email', None)
    code = app.storage.user.pop('code', None)

    await style()
    await check_notifications()
    await reset_password.content(client, email, code)

@ui.page('/project')
async def _project(client: Client, id: str = None, new: bool = False):
    if id is None:
        return RedirectResponse('/')
    if new is True:
        app.storage.user['new'] = new
        return RedirectResponse(f'/project?id={id}')
    new = app.storage.user.pop('new', False)

    await style()
    await check_notifications()
    await project.content(client, id, new)

async def make_temp_dir():
    os.makedirs('PYTHON/frontend/temp', exist_ok=True)
    await clear_temp_dir()

async def clear_temp_dir():
    print('Clearing temp directory')
    for file in os.listdir('PYTHON/frontend/temp'):
        os.remove(f'PYTHON/frontend/temp/{file}')

ui.timer(3600, clear_temp_dir) # periodically clear temp directory (every hour)
app.on_startup(make_temp_dir)

ui.run(dark=True, title='Scribe', favicon='📝', storage_secret='this_is_a_secret', host='0.0.0.0', port=8080, show=False)
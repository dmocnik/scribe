from nicegui import ui, app
from fastapi.responses import RedirectResponse
from middleware import ScribeAuthMiddleware

import fake_backend_api

app.add_middleware(ScribeAuthMiddleware)

async def check_notifications():
    notifications = app.storage.user.pop('notifications', None)
    if notifications == 'login':
        ui.notify(f'Hello, {app.storage.user.get("username")}!', position='top-right', close_button=True, type='positive')
    if notifications == 'logout':
        ui.notify('Successfully logged out!', position='top-right', close_button=True, type='positive')
    pass

async def logout():
    app.storage.user.clear()
    app.storage.user.update({'notifications': 'logout'})
    ui.open('/login')

@ui.page('/')
async def index():
    await check_notifications()
    ui.label('This is an example main page. You should only be able to see it if you are logged in.')
    ui.label(f'You are logged in as: {app.storage.user.get("username")}')
    ui.button('Sign out', on_click=lambda: logout(), icon='logout')

@ui.page('/bruh')
async def bruh():
    await check_notifications()
    ui.image('https://www.oakland.edu/Assets/Oakland/president/graphics/headshots/oraheadshot.jpg')

@ui.page('/login')
async def login():
    await check_notifications()
    def try_login():
        username = username_input.value
        password = password_input.value
        res = fake_backend_api.login({'username': username, 'password': password})
        status_code, data = res
        if status_code == 200:
            app.storage.user.update({'username': username_input.value,
                                     'authenticated': True,
                                     'token': data['token']})
            app.storage.user['notifications'] = 'login'
            path = app.storage.user.get('referrer_path', '/')
            ui.open(path)
        elif status_code == 401:
            ui.notify('Invalid username or password', position='top-right', close_button=True, type='negative')
        else:
            ui.notify('An error occurred', position='top-right', close_button=True, type='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    
    ui.query('body').style('background-image: url("https://w.wallhaven.cc/full/m9/wallhaven-m965vm.jpg")')
    ui.query('.nicegui-content').classes('p-0')
    #ui.header(elevated=True, add_scroll_padding=False, fixed=False)
    with ui.column().classes('w-full justify-center items-center h-screen'):
        ui.label('Welcome!').style('font-size: 3.75rem; font-weight: 500;')
        ui.label('Please sign in.')
        
        with ui.card().classes('w-1/3 p-0'):
            with ui.splitter().classes('w-full') as s:
                with s.before:
                    with ui.column().classes('m-5'):
                        username_input = ui.input('Username') \
                            .props('outlined') \
                            .classes('w-full')
                        password_input = ui.input('Password', password=True, password_toggle_button=True) \
                            .props('outlined') \
                            .classes('w-full') \
                            .on('keydown.enter', try_login)
                        ui.button(text='Sign in', icon='login', on_click=try_login)
                with s.after:
                    with ui.column().classes('m-5'):
                        ui.label('Need an account?')
                        ui.button(text='Sign up', icon='person_add')
                        ui.label('Forgot your password?')
                        ui.button(text='Reset Password', icon='lock_reset')

ui.run(dark=True, title='Scribe', favicon='📝', storage_secret='this_is_a_secret')
from nicegui import ui, app
from fastapi.responses import RedirectResponse
from middleware import ScribeAuthMiddleware

import fake_backend_api

app.add_middleware(ScribeAuthMiddleware)

@ui.page('/')
def index():
    ui.label('This is an example main page. You should only be able to see it if you are logged in.')
    ui.button('Sign out', on_click=lambda: (app.storage.user.clear(), ui.open('/login')), icon='logout')

@ui.page('/bruh')
def bruh():
    ui.image('https://www.oakland.edu/Assets/Oakland/president/graphics/headshots/oraheadshot.jpg')

@ui.page('/login')
def login():
    def try_login():
        username = username_input.value
        password = password_input.value
        res = fake_backend_api.login({'username': username, 'password': password})
        status_code, data = res
        if status_code == 200:
            app.storage.user.update({'username': username_input.value,
                                     'authenticated': True,
                                     'token': data['token']})
            ui.open(app.storage.user.get('referrer_path', '/'))
        elif status_code == 401:
            ui.notify('Invalid username or password')
        else:
            ui.notify('An error occurred')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')

    ui.query('body').style('background-image: url("https://w.wallhaven.cc/full/m9/wallhaven-m965vm.jpg")')
    ui.query('.nicegui-content').classes('p-0')
    #ui.header(elevated=True, add_scroll_padding=False, fixed=False)
    with ui.column().classes('w-full justify-center items-center h-screen'):
        ui.label('Welcome!').style('font-size: 3.75rem; font-weight: 500;')
        ui.label('Please sign in.')
        with ui.card().classes('w-1/3'):
            with ui.splitter().classes('w-full') as s:
                with s.before:
                    username_input = ui.input('Username')
                    password_input = ui.input('Password')
                    ui.button(text='Sign in', on_click=try_login)
                with s.after:
                    with ui.column().classes('ml-5 mt-2.5'):
                        ui.label('Need an account?')
                        ui.button(text='sign up')
                        ui.label('Forgot your password?')
                        ui.button(text='reset')

ui.run(dark=True, title='Scribe', favicon='📝', storage_secret='this_is_a_secret')
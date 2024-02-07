from nicegui import ui, app
from fastapi.responses import RedirectResponse
from middleware import ScribeAuthMiddleware
import re

import fake_backend_api

# TODO
# Make it react to screen size changes better
# Serve the wallpaper background better (probably from local file)
# Track whether account "is disabled" in user storage
# Show web requests in Chrome DevTools

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
        sign_in_btn.props('loading')
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
        sign_in_btn.props(remove='loading')
        
    EMAIL_REGEX = r'^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$'
    DEBOUNCE_TIME = 500
    async def sign_up():
        async def try_sign_up():
            valid = [input.validate() for input in [email_input, password_input, confirm_password_input, name_input]]
            if all(valid):
                user = {
                    'email': email_input.value,
                    'password': password_input.value,
                    'name': name_input.value if name_input.value else None
                }
                sign_up_dialog.submit(user)

        with ui.dialog() as sign_up_dialog, ui.card().classes('w-1/2'):
            with ui.row().classes('w-full items-center'):
                ui.label('Sign up').classes('text-h5')
                ui.space()
                ui.button(icon='close', on_click=lambda: sign_up_dialog.close()).props('flat round text-color="white"')

            email_input = ui.input('Email address',
                validation=lambda value: 'Please enter a valid email' if not re.match(EMAIL_REGEX, value) else None) \
                .props(f'outlined debounce="{DEBOUNCE_TIME}"') \
                .classes('w-full')
            
            password_input = ui.input('Password',
                password=True,
                password_toggle_button=True, 
                validation={
                    'Password too short': lambda value: len(value) >= 8,
                    'Password must contain an uppercase letter': lambda value: re.search(r'[A-Z]', value),
                    'Password must contain a lowercase letter': lambda value: re.search(r'[a-z]', value),
                    'Password must contain a number': lambda value: re.search(r'[0-9]', value),
                    'Passwords do not match': lambda value: value == confirm_password_input.value
                }) \
                .props(f'outlined debounce="{DEBOUNCE_TIME}"') \
                .classes('w-full') \
                .tooltip('Password must be at least 8 characters long, and contain an uppercase letter, a lowercase letter, and a number.')
            
            confirm_password_input = ui.input('Confirm password',
                password=True,
                password_toggle_button=True,
                validation= lambda value: 'Passwords do not match' if not password_input.value == value else None) \
                .props(f'outlined debounce="{DEBOUNCE_TIME}"') \
                .classes('w-full')
            
            name_input = ui.input('Name (optional)', 
                validation=lambda value: 'Too long' if len(value) > 50 else None) \
                .props(f'outlined debounce="{DEBOUNCE_TIME}"') \
                .classes('w-full')
            
            with ui.row().classes('w-full'):
                ui.space()
                ui.button('Sign up', on_click=lambda: try_sign_up())

        info = await sign_up_dialog
        if info:
            ui.notify(info)
            ui.notify('Account created!', position='top-right', close_button=True, type='positive')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    
    #bg_image = "https://w.wallhaven.cc/full/m9/wallhaven-m965vm.jpg"  #This doesn't load every time for some reason, should probably be served from local file
    bg_image = "https://images5.alphacoders.com/707/707888.jpg"
    ui.query('body').style(f'''
                           background-image: url("{bg_image}");
                           background-size: cover;
                           background-repeat: no-repeat;
                           ''')
    ui.query('.nicegui-content').classes('p-0')
    with ui.column().classes('w-full justify-center items-center h-screen'):
        ui.label('Welcome!').style('font-size: 3.75rem; font-weight: 500;')
        ui.label('Please sign in.')
        
        with ui.card().classes('w-1/2 p-0 gap-0 flex-row flex-nowrap backdrop-blur-lg').style('background-color: #1d1d1dd9;'):
            with ui.column().classes('w-1/2 p-5'):
                username_input = ui.input('Email address') \
                    .props('outlined') \
                    .classes('w-full')
                password_input = ui.input('Password', password=True, password_toggle_button=True) \
                    .props('outlined') \
                    .classes('w-full') \
                    .on('keydown.enter', try_login)
                sign_in_btn = ui.button(text='Sign in', icon='login', on_click=try_login)
            with ui.column().classes('w-1/2 p-5'):
                ui.label('Need an account?')
                ui.button(text='Sign up', icon='person_add', on_click=sign_up)
                ui.label('Forgot your email address or password?')
                ui.button(text='Reset Password', icon='lock_reset')

@ui.page('/verify-account')
async def verify_account():
    async def try_verify_code():
        code = code_input.value
        if code == '123456':
            ui.notify('Account verified!', position='top-right', close_button=True, type='positive')
            ui.open('/')
        else:
            ui.notify('Invalid code.', position='top-right', close_button=True, type='negative')

    bg_image = "https://images5.alphacoders.com/707/707888.jpg"
    ui.query('body').style(f'''
                           background-image: url("{bg_image}");
                           background-size: cover;
                           background-repeat: no-repeat;
                           ''')
    ui.query('.nicegui-content').classes('p-0')
    with ui.column().classes('w-full justify-center items-center h-screen'):
        ui.label('Check your email!').style('font-size: 3.75rem; font-weight: 500;')
        ui.label('We\'ve sent you a verification code.')
        
        with ui.card().classes('w-1/2 p-0 gap-0 flex-row flex-nowrap backdrop-blur-lg').style('background-color: #1d1d1dd9;'):
            with ui.column().classes('w-1/2 p-5'):
                code_input = ui.input('Verification code') \
                    .props('outlined') \
                    .classes('w-full') \
                    .on('keydown.enter', try_verify_code)
                sign_in_btn = ui.button(text='Verify', icon='done', on_click=try_verify_code)
            with ui.column().classes('w-1/2 p-5'):
                ui.label('Didn\'t get an email? Be sure to check or spam folder. If you still don\'t see it, you can resend the email.')
                resend_btn = ui.button(text='Resend code', icon='send', 
                    on_click=lambda: (ui.notify('Code sent!', position='top-right', close_button=True, type='positive'),
                                      resend_btn.props('disabled')))

ui.run(dark=True, title='Scribe', favicon='📝', storage_secret='this_is_a_secret')
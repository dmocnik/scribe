from nicegui import ui, app
import re, httpx
from fastapi.responses import RedirectResponse

from config import DevelopmentConfig as config

#TODO 
# Add validation for sign in inputs (so they cant send empty requests)
# fix the validtion of the sign up inputs

API_URL = config.API_URL
LOGIN_URL = f'{API_URL}/login'
ACCOUNT_CREATE_URL = f'{API_URL}/account/create'
PW_RESET_REQUEST_URL = f'{API_URL}/password/reset/request'

async def content():
    async def try_login():
        sign_in_btn.props('loading')
        username = username_input.value
        password = password_input.value

        # response object, pass login url, post body, and cookies from app storage
        async with httpx.AsyncClient() as c:
            res = await c.post(LOGIN_URL, 
                            json={"email": username, "password": password}, 
                            headers={"Cookie": f"{app.storage.user.get('cookie')}"})

        if res.status_code == 200:
            # get cookie from response header
            cookie = res.headers['Set-Cookie'].split(';')[0]
            app.storage.user.update({'username': username_input.value,
                                    'authenticated': True,
                                    'cookie': cookie})
            app.storage.user['notifications'] = 'login'
            path = app.storage.user.pop('referrer_path', '/')
            ui.open(path)
        elif res.status_code == 401:
            ui.notify('Invalid username or password', position='top-right', close_button=True, type='negative')
        else:
            ui.notify('An error occurred', position='top-right', close_button=True, type='negative')
        sign_in_btn.props(remove='loading')
            
    EMAIL_REGEX = r'^[\w+.]+@[a-zA-Z_]+?\.[a-zA-Z]+$'
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
                sign_up_btn.props('loading')
                async with httpx.AsyncClient() as c:
                    res = await c.post(ACCOUNT_CREATE_URL, json=user)
                if res.status_code == 200:
                    sign_up_dialog.submit(user)
                elif res.status_code == 409:
                    ui.notify('A user with that email already exists', position='top-right', close_button=True, type='negative')
                else:
                    ui.notify('An error occurred', position='top-right', close_button=True, type='negative')
                sign_up_btn.props(remove='loading')

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
                sign_up_btn = ui.button('Sign up', on_click=lambda: try_sign_up())

        info = await sign_up_dialog
        if info:
            ui.notify('Account created! Check your email...', position='top-right', close_button=True, type='positive')

    async def forgot_pw():
        async def try_forgot_pw():
            if email_input.validate() == True:
                send_email_btn.props('loading')
                async with httpx.AsyncClient() as c:
                    res = await c.post(PW_RESET_REQUEST_URL,
                                        json={"email": email_input.value},
                                        headers={"Cookie": f"{app.storage.user.get('cookie')}"})
                if res.status_code == 200:
                    forgot_pw_dialog.submit(email_input.value)
                else:
                    ui.notify('An error occurred', position='top-right', close_button=True, type='negative')
                """ elif res.status_code == xxx: # For later
                    ui.notify('An account with that email does not exist', position='top-right', close_button=True, type='negative') """
                send_email_btn.props(remove='loading')

        with ui.dialog() as forgot_pw_dialog, ui.card().classes('w-1/2'):
            with ui.row().classes('w-full items-center'):
                ui.label('Forgot/Reset Password').classes('text-h5')
                ui.space()
                ui.button(icon='close', on_click=lambda: forgot_pw_dialog.close()).props('flat round text-color="white"')

            ui.label('If you cannot remember or wish to reset your password, please enter your email address and we will send you a link to do so.')
            email_input = ui.input('Email address',
                    validation=lambda value: 'Please enter a valid email' if not re.match(EMAIL_REGEX, value) else None) \
                    .props(f'outlined debounce="{DEBOUNCE_TIME}"') \
                    .classes('w-full')
            
            with ui.row().classes('w-full'):
                ui.space()
                send_email_btn = ui.button('Send Email', on_click=lambda: try_forgot_pw())

        email = await forgot_pw_dialog
        if email:
            ui.notify('Password reset requested. Check your email!', position='top-right', close_button=True, type='positive')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    
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
                sign_up_btn = ui.button(text='Sign up', icon='person_add', on_click=sign_up)
                ui.label('Forgot your email address or password?')
                reset_pw_btn = ui.button(text='Reset Password', icon='lock_reset', on_click=forgot_pw)
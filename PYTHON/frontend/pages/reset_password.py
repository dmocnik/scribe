from nicegui import ui, app, Client
import httpx, re
from config import DevelopmentConfig as config

API_URL = config.API_URL
ACCOUNT_LOGIN_CODE_URL = f'{API_URL}/account/login/code'
PW_RESET_URL = f'{API_URL}/password/reset'

DEBOUNCE_TIME = 500

async def content(client: Client, email: str = None, code: str = None):
    with ui.dialog().props('persistent') as spinner_dialog, ui.card().style(replace=''):
            ui.spinner(size='lg')

    async def verify_code():
        async def try_pw_change():
            change_pw_btn.props('loading')
            async with httpx.AsyncClient() as c:
                res = await c.post(PW_RESET_URL, json={'new_password': password_input.value}, headers={'Cookie': f"{app.storage.user.get('cookie')}"})
            if res.status_code == 200:
                pw_dialog.submit(True)
            else:
                ui.notify('An error occurred', position='top-right', close_button=True, type='negative')
            change_pw_btn.props(remove='loading')

        with ui.dialog().props('persistent') as pw_dialog, ui.card().classes('w-1/2').style(replace=''):
            with ui.row().classes('w-full items-center'):
                ui.label('New Password').classes('text-h5')
                ui.space()

            ui.label('Please enter your new password.')

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
                .props(f'debounce="{DEBOUNCE_TIME}"') \
                .classes('w-full') \
                .tooltip('Password must be at least 8 characters long, and contain an uppercase letter, a lowercase letter, and a number.')
            
            confirm_password_input = ui.input('Confirm password',
                password=True,
                password_toggle_button=True,
                validation= lambda value: 'Passwords do not match' if not password_input.value == value else None) \
                .props(f'debounce="{DEBOUNCE_TIME}"') \
                .classes('w-full')

            with ui.row().classes('w-full'):
                ui.space()
                change_pw_btn = ui.button('Change Password', on_click=try_pw_change)

        spinner_dialog.open()
        async with httpx.AsyncClient() as c:
            res = await c.post(ACCOUNT_LOGIN_CODE_URL, json={'email': email, 'code': code})
        if res.status_code == 200:
            cookie = res.headers['Set-Cookie'].split(';')[0]
            app.storage.user.update({'username': email,
                                    'authenticated': True,
                                    'cookie': cookie})
            result = await pw_dialog

            if result == True:
                app.storage.user['notifications'] = 'pw_change_success'
                app.storage.user['authenticated'] = False
                ui.navigate.to('/login')
                return
            
        elif res.status_code == 401:
            ui.notify('Invalid code', position='top-right', close_button=True, type='negative')
        else:
            ui.notify('An error occurred', position='top-right', close_button=True, type='negative')
        
    ui.query('.nicegui-content').classes('p-0')
    with ui.column().classes('w-full justify-center items-center h-screen'):
        ui.label('Let\'s get back into your account.').style('font-size: 3.75rem; font-weight: 600; text-shadow: 3px 3px 5px black')
        ui.label('Check your email! We\'ve sent you a verification code.').style('font-size: 20px; text-shadow: 3px 3px 3px black')
        
        with ui.card().classes('w-1/2 p-0 gap-0 flex-row flex-nowrap backdrop-blur-lg'):
            with ui.column().classes('w-1/2 p-5'):
                code_input = ui.input('Verification code') \
                    .classes('w-full') \
                    .on('keydown.enter', verify_code)
                if code:
                    code_input.value = code

                verify_btn = ui.button(text='Verify', icon='done', on_click=verify_code)
            with ui.column().classes('w-1/2 p-5'):
                ui.label('Didn\'t get an email? Be sure to check or spam folder. If you still don\'t see it, you can resend the email.')
                resend_btn = ui.button(text='Resend code', icon='send', 
                    on_click=lambda: (ui.notify('Code sent!', position='top-right', close_button=True, type='positive'),
                                        resend_btn.props('disabled')))
                
    if email is not None and code is not None:
        await client.connected()
        await verify_code()
from nicegui import ui, app
import asyncio, re, httpx
from config import DevelopmentConfig as config

API_URL = config.API_URL
ACCOUNT_LOGIN_CODE_URL = f'{API_URL}/account/login/code'
PW_RESET_URL = f'{API_URL}/password/reset'
ACCOUNT_ACTIVATE_URL = f'{API_URL}/account/activate'

DEBOUNCE_TIME = 500

#TODO Store the URL parametrs in the app storage so they can't be tampered with

async def content(email, code, intent):
    ui.add_head_html('''
            <script>
            window.onload = () => {
                emitEvent('content_loaded');
            };
            </script>
        ''')

    async def verify_code():
        with ui.dialog().props('persistent') as spinner_dialog, ui.card():
            ui.spinner(size='lg')
        
        spinner_dialog.open()
        res = await httpx.post(ACCOUNT_LOGIN_CODE_URL, json={'email': email, 'code': code}) # Do we need to pass the cookie here?
        valid_code = None
        if res.status_code == 200:
            cookie = res.headers['Set-Cookie'].split(';')[0]
            app.storage.user.update({'cookie': cookie})
            spinner_dialog.close()
            valid_code = True
        else:
            spinner_dialog.close()
            #TODO
            ui.notify('huh?', position='top-right', close_button=True, type='negative')
            return

        if valid_code == True:
            if intent == 'pw_reset':
                pw_success = await pw_dialog
                if pw_success == True:
                    ui.notify('Password changed!  Sending you back to the login page...', position='top-right', close_button=True, type='positive')
                    await asyncio.sleep(3)
                    ui.navigate.to('/login')
            elif intent == 'account_create':
                res = await httpx.post(ACCOUNT_ACTIVATE_URL, json={'email': email, 'code': code}, headers={'Cookie': f"{app.storage.user.get('cookie')}"})
                if res.status_code == 200:
                    app.storage.user.update({'authenticated': True})
                    app.storage.user['notifications'] = 'account_create_success'
                    ui.navigate.to('/')
                else:
                    # TODO
                    ui.notify('An error occurred, try again later', position='top-right', close_button=True, type='negative')
                pass
    
    async def try_pw_change():
        change_pw_btn.props('loading')
        res = await httpx.post(PW_RESET_URL, json={'new_password': password_input.value}, headers={'Cookie': f"{app.storage.user.get('cookie')}"})
        if res.status_code == 200:
            pw_dialog.submit(True)
        else:
            ui.notify('An error occurred', position='top-right', close_button=True, type='negative')
        change_pw_btn.props(remove='loading')

    with ui.dialog().props('persistent') as pw_dialog, ui.card().classes('w-1/2'):
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
            .props(f'outlined debounce="{DEBOUNCE_TIME}"') \
            .classes('w-full') \
            .tooltip('Password must be at least 8 characters long, and contain an uppercase letter, a lowercase letter, and a number.')
        
        confirm_password_input = ui.input('Confirm password',
            password=True,
            password_toggle_button=True,
            validation= lambda value: 'Passwords do not match' if not password_input.value == value else None) \
            .props(f'outlined debounce="{DEBOUNCE_TIME}"') \
            .classes('w-full')

        with ui.row().classes('w-full'):
            ui.space()
            change_pw_btn = ui.button('Change Password', on_click=try_pw_change)

    bg_image = "https://images5.alphacoders.com/707/707888.jpg"
    ui.query('body').style(f'''
                           background-image: url("{bg_image}");
                           background-size: cover;
                           background-repeat: no-repeat;
                           ''')
    ui.query('.nicegui-content').classes('p-0')
    with ui.column().classes('w-full justify-center items-center h-screen'):
        ui.label('Verify your account!').style('font-size: 3.75rem; font-weight: 500;')
        ui.label('Check your email! We\'ve sent you a verification code.')
        
        with ui.card().classes('w-1/2 p-0 gap-0 flex-row flex-nowrap backdrop-blur-lg').style('background-color: #1d1d1dd9;'):
            with ui.column().classes('w-1/2 p-5'):
                code_input = ui.input('Verification code') \
                    .props('outlined') \
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
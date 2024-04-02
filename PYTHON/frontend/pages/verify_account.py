from nicegui import ui, app, Client
import httpx
from config import DevelopmentConfig as config

API_URL = config.API_URL
ACCOUNT_ACTIVATE_URL = f'{API_URL}/account/activate'

#TODO Store the URL parametrs in the app storage so they can't be tampered with

async def content(client: Client, email: str = None, code: str = None):
    async def verify_code():
        with ui.dialog().props('persistent') as spinner_dialog, ui.card().style(replace=''):
            ui.spinner(size='lg')
        
        spinner_dialog.open()
        async with httpx.AsyncClient() as c:
            res = await c.post(ACCOUNT_ACTIVATE_URL, json={'email': email, 'code': code})
        if res.status_code == 200:
            cookie = res.headers['Set-Cookie'].split(';')[0]
            app.storage.user.update({'username': email,
                                    'authenticated': True,
                                    'cookie': cookie})
            app.storage.user['notifications'] = 'account_create_success'
            ui.navigate.to('/')
        elif res.status_code == 401:
            ui.notify('Invalid code', position='top-right', close_button=True, type='negative')
        else:
            ui.notify('An error occurred', position='top-right', close_button=True, type='negative')
        spinner_dialog.close()
        
    ui.query('.nicegui-content').classes('p-0')
    with ui.column().classes('w-full justify-center items-center h-screen'):
        ui.label('Verify your account!').style('font-size: 3.75rem; font-weight: 600;')
        ui.label('Check your email! We\'ve sent you a verification code.')
        
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
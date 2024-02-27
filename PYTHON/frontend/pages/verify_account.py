from nicegui import ui

async def content():
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
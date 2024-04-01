from nicegui import ui, app, Client
from middleware import ScribeAuthMiddleware
from pages import login, verify_account, index, project

# TODO
# Make it react to screen size changes better
# Style pass
    # Serve the wallpaper background better (probably from local file)
    # Favicon
    # Color scheme
    # font
    # default style props
# Show web requests in Chrome DevTools

app.add_middleware(ScribeAuthMiddleware)

async def check_notifications(): # TODO make this be able to handle multiple notifications instead of just one at a time
    notifications = app.storage.user.pop('notifications', None)
    if notifications == 'login':
        ui.notify(f'Hello, {app.storage.user.get("username")}!', position='top-right', close_button=True, type='positive')
    if notifications == 'logout':
        ui.notify('Successfully logged out!', position='top-right', close_button=True, type='positive')
    if notifications == 'account_create_success':
        ui.notify('Account verified successfully! You are now logged in.', position='top-right', close_button=True, type='positive')
    pass

@ui.page('/')
async def _index():
    await check_notifications()
    await index.content()
    
@ui.page('/bruh')
async def _bruh():
    await check_notifications()
    ui.image('https://www.oakland.edu/Assets/Oakland/president/graphics/headshots/oraheadshot.jpg')

@ui.page('/login')
async def _login():
    await check_notifications()
    await login.content()

@ui.page('/verify-account')
async def _verify_account(email: str = None, code: str = None, intent: str = None):
    await check_notifications()
    await verify_account.content(email, code, intent)

@ui.page('/project')
async def _project(client: Client, id: str = None, new: bool = False, name: str = None):
    await check_notifications()
    await project.content(client, id, new, name)

ui.run(dark=True, title='Scribe', favicon='📝', storage_secret='this_is_a_secret', host='0.0.0.0', port=8080, show=False)
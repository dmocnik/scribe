from nicegui import ui, app
from middleware import ScribeAuthMiddleware
from pages import login, verify_account, index

# TODO
# Make it react to screen size changes better
# Serve the wallpaper background better (probably from local file)
# Track whether account "is disabled" in user storage
# Show web requests in Chrome DevTools
# Async / await stuff properly

app.add_middleware(ScribeAuthMiddleware)

async def check_notifications():
    notifications = app.storage.user.pop('notifications', None)
    if notifications == 'login':
        ui.notify(f'Hello, {app.storage.user.get("username")}!', position='top-right', close_button=True, type='positive')
    if notifications == 'logout':
        ui.notify('Successfully logged out!', position='top-right', close_button=True, type='positive')
    pass

@ui.page('/')
async def _index():
    await check_notifications()
    await index.content()
    
@ui.page('/bruh')
async def bruh():
    await check_notifications()
    ui.image('https://www.oakland.edu/Assets/Oakland/president/graphics/headshots/oraheadshot.jpg')

@ui.page('/login')
async def _login():
    await check_notifications()
    await login.content()

@ui.page('/verify-account')
async def _verify_account():
    await check_notifications()
    await verify_account.content()

ui.run(dark=True, title='Scribe', favicon='📝', storage_secret='this_is_a_secret', host='0.0.0.0', port=8080, show=False)
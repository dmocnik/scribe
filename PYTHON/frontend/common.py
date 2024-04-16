from nicegui import app, ui

async def logout():
    app.storage.user.clear()
    app.storage.user.update({'notifications': 'logout'})
    ui.open('/login')

async def check_notifications(): # TODO make this be able to handle multiple notifications instead of just one at a time
    notifications = app.storage.user.pop('notifications', None)
    if notifications == 'login':
        ui.notify(f'Hello, {app.storage.user.get("username")}!', position='top-right', close_button=True, type='positive')
    if notifications == 'logout':
        ui.notify('Successfully logged out!', position='top-right', close_button=True, type='positive')
    if notifications == 'account_create_success':
        ui.notify('Account verified successfully! Please login again.', position='top-right', close_button=True, type='positive')
    if notifications == 'pw_change_success':
        ui.notify('Password changed successfully! Please login again.', position='top-right', close_button=True, type='positive')
    pass
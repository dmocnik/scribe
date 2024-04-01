from nicegui import ui, app, events

editing = False

async def logout():
    app.storage.user.update({'authenticated': False})
    app.storage.user.update({'notifications': 'logout'})
    ui.open('/login')

async def content(client, id, new):
    async def upload_file():
        async def handle_upload(e: events.UploadEventArguments):
            filename = e.name
            length = len(e.content.read())
            mb = (length / 1024) / 1024
            ui.notify(f'Filename: {filename}')
            ui.notify(f'Size: {mb:.2f}MB')
            upload_dialog.submit(True)

        with ui.dialog().props('persistent') as upload_dialog, ui.card().classes('w-1/2'): # Create a dialog for the file upload
            with ui.row().classes('w-full items-center'):
                ui.label('Upload Source Video').classes('text-h5')
                ui.space()

            with ui.column().classes('items-center justify-center w-full'):
                ui.label('Drag and drop a video here, or press the "+" button to select it manually')
                #TODO See if there's a better way to style the uploader, possibly make it hidden with custom drag and drop area
                uploader = ui.upload(max_files=1, on_upload=handle_upload, auto_upload=True).props('accept="video/*"')
                ui.label('Max file Size: 100MB, Max Duration: 2 hours')

        result = await upload_dialog
        return result

    async def change_preview(value):
        if value == 'video':
            preview_area.clear()
            with preview_area:
                ui.video('https://www.w3schools.com/html/mov_bbb.mp4', loop=True).classes('h-full w-max').style('object-fit: contain;')
        elif value == 'transcription':
            preview_area.clear()
            with preview_area:
                transcript = ui.log().classes('w-full h-full')
                transcript.push('This is an exmaple of a transcription. It will be generated automatically from the video.')
        elif value == 'notes':
            preview_area.clear()
            with preview_area:
                ui.html(f'<embed src="https://www.rd.usda.gov/sites/default/files/pdf-sample_0.pdf" type="application/pdf" width="100%" height="100%">').classes('w-full h-full')
    
    async def edit_name(action=None):
        global editing

        if action == True:
            editing = True
            proj_name.set_visibility(False)
            proj_name_input.set_value(proj_name.text)
            proj_name_input.set_visibility(True)
            proj_name_input.run_method('focus')
            proj_name_input.run_method('select')
            proj_name_edit_btn.set_visibility(False)
            return
        
        if action == False:
            if editing == False:
                return
            editing = False
            proj_name.set_text(proj_name_input.value)
            proj_name.set_visibility(True)
            proj_name_input.set_visibility(False)
            proj_name_edit_btn.set_visibility(True)
            ui.notify(f'Project name changed to {proj_name.text}', type='positive', position='top-right', close_button=True)
            return
    
    if id is None:
        ui.label('Not a project bruh')
        return

    bg_image = "https://images5.alphacoders.com/707/707888.jpg" # Set the background image
    ui.query('body').style(f'''
                           background-image: url("{bg_image}");
                           background-size: cover;
                           background-repeat: no-repeat;
                           ''')

    ui.query('.nicegui-content').classes('h-[calc(100vh-74px)]') # yuck https://github.com/zauberzeug/nicegui/discussions/2703#discussioncomment-8820280

    header = ui.header(elevated=True).classes('items-center justify-between')
    with header: # Create the header
        ui.link('📝', '/').style('font-size: 1.5rem;').tooltip('Home')
        proj_name = ui.label('Untitled project').style('font-size: 1.5rem;')
        proj_name_input = ui.input('Project Name').props('filled dense standout label-color="white"').on('keydown.enter', lambda: edit_name(False))
        proj_name_input.set_visibility(False)
        proj_name_edit_btn = ui.button(on_click=lambda: edit_name(True), icon='edit').props('flat round text-color="white"')
        ui.space()
        ui.button(on_click=logout, icon='logout').props('flat round text-color="white"')

    with ui.row().classes('w-full flex-nowrap h-full'):
        with ui.card().classes('w-1/4 h-full backdrop-blur-lg').style('background-color: #1d1d1dd9;'):
            ui.label('Picker').classes('text-h5')
            with ui.row().classes('items-center w-full'):
                add_media = ui.select({'notes': 'Notes', 'audiobook': 'Audiobook', 'flashcards': 'Flashcards'}, label='Add Media', value='notes').classes('grow').props('outlined')
                add_media_btn = ui.button(icon='add', on_click=lambda: ui.notify(f'Will generate media of type {add_media.value}')).props('flat round text-color="white"')
            ui.separator()
            preview_media = ui.select({'video': 'Original Lecture Video', 'transcription': 'Lecture Transcription', 'notes': 'AI-Summarized Notes'}, label='Preview Media', on_change=lambda: change_preview(preview_media.value)).classes('w-full').props('outlined')

        with ui.card().classes('w-3/4 h-full backdrop-blur-lg').style('background-color: #1d1d1dd9;'):
            ui.label('Preview').classes('text-h5')
            preview_area = ui.element('div').classes('w-full items-center justify-center h-full')
            with preview_area:
                with ui.column().classes('w-full items-center justify-center h-full'):
                    ui.icon('description', size='100px')
                    ui.label('Your media will appear here.').classes('text-h5')
                    ui.label('Select an option from the picker on the left to get started.')
            with ui.row():
                ui.button('Download', icon='download')
                ui.button('Delete', icon='delete')
    
    if new == True:
        await client.connected()
        success = await upload_file()
        print(success)
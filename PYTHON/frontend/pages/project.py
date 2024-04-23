from nicegui import ui, app, events
from common import logout
from config import DevelopmentConfig as config
import httpx, asyncio

editing = False

API_URL = config.API_URL
PROJECT_READ_URL = f'{API_URL}/project/read'

async def content(client, id: int, new: bool):
    async def upload_file():
        async def handle_upload(e: events.UploadEventArguments):
            filename = e.name
            data = e.content.read()
            mb = (len(data) / 1024) / 1024
            try: #TODO probably should be an if statement
                async with httpx.AsyncClient() as c:
                    res = await c.post(f'{API_URL}/project/{id}', headers={'Cookie': app.storage.user['cookie']}, data={'media_name': filename, 'media_type': 'video', 'file_type': 'mp4'}, files={'media_content': (filename, data, 'video/mp4')}, timeout=30.0)
                if res.status_code == 200:
                    upload_dialog.submit(True)
                else:
                    upload_dialog.submit(False)
            except Exception as e:
                upload_dialog.submit(False)

        with ui.dialog().props('persistent') as upload_dialog, ui.card().classes('w-1/2').style(replace=''): # Create a dialog for the file upload
            with ui.row().classes('w-full items-center'):
                ui.label('Upload Source Video').classes('text-h5')
                ui.space()

            with ui.column().classes('items-center justify-center w-full'):
                ui.label('Drag and drop a video here, or press the "+" button to select it manually')
                uploader = ui.upload(max_files=1, on_upload=handle_upload, auto_upload=True).props('accept="video/*"')
                ui.label('Max file Size: 4GB, Max Duration: 3 hours')

        result = await upload_dialog
        if result == True:
            ui.notify('Video uploaded successfully!', type='positive', position='top-right', close_button=True)
            async with httpx.AsyncClient() as c:
                res = await c.post('http://scribe_app:8200/add_action', json={
                    "action": "make_transcript",
                    "parameters": ["sample_video.mp4", "transcript.txt", "text", "transcribe", "en", False, True, id]
                })
            ui.notify('Transcription started, check back later.', type='positive', position='top-right', close_button=True)
        else:
            ui.notify('Failed to upload video, try again', type='negative', position='top-right', close_button=True)
        return result

    async def change_preview(value):
        preview_area.clear()
        with preview_area: #show a spinner while the preview is loading
            ui.spinner(size='lg')
        if value == 'video':
            delete_btn.set_enabled(False)
            async with httpx.AsyncClient() as c: #get the bytes of the video from the server
                res = await c.get(f'{API_URL}/project/{id}/video/mp4', headers={'Cookie': app.storage.user['cookie']})
                path = f'PYTHON/frontend/temp/{id}_video.mp4'
                with open(path, 'wb') as f:
                    f.write(res.content)
            url = app.add_media_file(url_path=f'/content/{id}_video.mp4', local_file=path) #make the video accessibile to the user
            preview_area.clear() #display it
            with preview_area:
                ui.video(url).classes('h-[calc(100vh-238px)] w-max').style('object-fit: contain;')
        elif value == 'transcript':
            delete_btn.set_enabled(False)
            async with httpx.AsyncClient() as c: #get the text from the server
                res = await c.get(f'{API_URL}/project/{id}/transcript/txt', headers={'Cookie': app.storage.user['cookie']})
                text = res.text
            preview_area.clear() #display it
            with preview_area:
                transcript = ui.log().classes('w-full h-[calc(100vh-238px)]')
                transcript.push(text)
        elif value == 'aisummary':
            delete_btn.set_enabled(True)
            async with httpx.AsyncClient() as c: #get the text from the server
                res = await c.get(f'{API_URL}/project/{id}/aisummary/txt', headers={'Cookie': app.storage.user['cookie']})
                text = res.text
            preview_area.clear() #display it
            with preview_area:
                transcript = ui.log().classes('w-full h-[calc(100vh-238px)]')
                transcript.push(text)
        elif value == 'aiaudio':
            delete_btn.set_enabled(True)
            async with httpx.AsyncClient() as c: #get the bytes of the audio from the server
                res = await c.get(f'{API_URL}/project/{id}/aiaudio/wav', headers={'Cookie': app.storage.user['cookie']})
                path = f'PYTHON/frontend/temp/{id}_audio.wav'
                with open(path, 'wb') as f:
                    f.write(res.content)
            await asyncio.sleep(1) 
            url = app.add_media_file(url_path=f'/content/{id}_audio.wav', local_file=path) #make the audio accessibile to the user
            preview_area.clear()
            with preview_area:
                ui.audio(url, controls=True).classes('w-full h-[calc(100vh-238px)]')
        elif value == 'aivideo':
            delete_btn.set_enabled(True)
            """ async with httpx.AsyncClient() as c: #get the bytes of the video from the server
                res = await c.get(f'{API_URL}/project/{id}/aivideo', headers={'Cookie': app.storage.user['cookie']})
                path = f'PYTHON/frontend/temp/{id}_aivideo.mp4'
                with open(path, 'wb') as f:
                    f.write(res.content) """
            url = app.add_media_file(f'content/{id}_aivideo.mp4', path, single_use=True) #make the video accessibile to the user
            preview_area.clear() #display it
            with preview_area:
                ui.video(url, loop=True).classes('h-full w-max').style('object-fit: contain;')
    
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
            async with httpx.AsyncClient() as c:
                res = await c.post(f'{API_URL}/project/{id}/edit', headers={'Cookie': app.storage.user['cookie']}, json={'project_name': proj_name_input.value})
            if res.status_code == 200:
                ui.notify(f'Project name changed to {proj_name.text}', type='positive', position='top-right', close_button=True)
                editing = False
                proj_name.set_text(proj_name_input.value)
                proj_name.set_visibility(True)
                proj_name_input.set_visibility(False)
                proj_name_edit_btn.set_visibility(True)
            else:
                ui.notify(f'Failed to change project name', type='negative', position='top-right', close_button=True)
                editing = False
                proj_name.set_visibility(True)
                proj_name_input.set_visibility(False)
                proj_name_edit_btn.set_visibility(True)
            return

    async def ai_generate_media(type):
        if type == 'aisummary':
            working = ui.notification('Working...', spinner=True, timeout=0)
            async with httpx.AsyncClient() as c:  #tell the queue to start the ai summary
                res = await c.post('http://scribe_app:8200/add_action', json={
                    "action": "summarize_transcript",
                    "parameters": ["output/transcript.txt", "output/summary.txt", id]
                })
            if res.status_code == 200:
                add_media_options.pop('aisummary')
                add_media.set_options(add_media_options)
                preview_media_options['aisummary'] = 'AI-Summarized Notes'
                preview_media.set_options(preview_media_options)
                ui.notify('Creating your notes! Check back later.', type='positive', position='top-right', close_button=True)
            else:
                ui.notify('Failed to create notes.', type='negative', position='top-right', close_button=True)
            working.dismiss()
        elif type == 'aiaudio':
            async with httpx.AsyncClient() as c:
                res = await c.post('http://scribe_app:8200/add_action', json={
                    "action": "get_audiobook",
                    "parameters": ["output/summary.txt", "output/audiobook.wav", "David - British Storyteller", id]
                })
            if res.status_code == 200:
                add_media_options.pop('aiaudio')
                add_media.set_options(add_media_options)
                preview_media_options['aiaudio'] = 'Audio Summary'
                preview_media.set_options(preview_media_options)
                ui.notify('Creating your audio! Check back later.', type='positive', position='top-right', close_button=True)
            else:
                ui.notify('Failed to create audio.', type='negative', position='top-right', close_button=True)
        elif type == 'aivideo':
            """ async with httpx.AsyncClient() as c:
                res = await c.post('http://scribe_app:8200/add_action', json={
                    "action": "make_video",
                    "parameters": ["output/audiobook.wav", "output/new_video.mp4", "David - British Storyteller", id]
                })
            if res.status_code == 200:
                add_media_options.pop('aivideo')
                add_media.set_options(add_media_options)
                preview_media_options['aivideo'] = 'Video Summary'
                preview_media.set_options(preview_media_options)
                ui.notify('Creating your video! Check back later.', type='positive', position='top-right', close_button=True)
            else: """
            ui.notify('Failed to create video.', type='negative', position='top-right', close_button=True)

    async def delete_media(type):
        if type == 'video' or type == 'transcript':
            ui.notify('nuh uh')
        elif type == 'aisummary' or type == 'aiaudio' or type == 'aivideo':
            for m in media:
                if m['type'] == type:
                    media_id = m['id']
                    break
            async with httpx.AsyncClient() as c:
                res = await c.post(f'{API_URL}/project/{id}/media/{media_id}/delete', headers={'Cookie': app.storage.user['cookie']})
        #add the option back to the select
        add_media_options[type] = {'aisummary': 'AI-Summarized Notes', 'aiaudio': 'Audio Summary', 'aivideo': 'Video Summary'}[type]
        add_media.set_options(add_media_options)
        #remove the option from the preview select
        preview_media_options.pop(type)
        preview_media.set_options(preview_media_options)

    async def download_media(type):
        if type == 'video' or type == 'aivideo':
            async with httpx.AsyncClient() as c:
                res = await c.get(f'{API_URL}/project/{id}/{type}/mp4', headers={'Cookie': app.storage.user['cookie']})
                bytes_out = res.content
            if res.status_code == 200:
                ui.download(bytes_out, f'{id}_{type}.mp4')
            else:
                ui.notify('Failed to download video', type='negative', position='top-right', close_button=True)
        elif type == 'transcript' or type == 'aisummary':
            async with httpx.AsyncClient() as c:
                res = await c.get(f'{API_URL}/project/{id}/{type}/txt', headers={'Cookie': app.storage.user['cookie']})
                text = res.content
            if res.status_code == 200:
                ui.download(text, f'{id}_{type}.txt')
            else:
                ui.notify('Failed to download text', type='negative', position='top-right', close_button=True)
        elif type == 'aiaudio':
            async with httpx.AsyncClient() as c:
                res = await c.get(f'{API_URL}/project/{id}/{type}/wav', headers={'Cookie': app.storage.user['cookie']})
                bytes_out = res.content
            if res.status_code == 200:
                ui.download(bytes_out, f'{id}_{type}.wav')
            else:
                ui.notify('Failed to download audio', type='negative', position='top-right', close_button=True)

    ui.query('.nicegui-content').classes('h-[calc(100vh-74px)]') # yuck https://github.com/zauberzeug/nicegui/discussions/2703#discussioncomment-8820280

    await client.connected()
    with ui.dialog().props('persistent') as spinner_dialog, ui.card().style(replace=''):
        ui.spinner(size='lg')
    spinner_dialog.open()
    async with httpx.AsyncClient() as c: #get the project data
        res = await c.post(PROJECT_READ_URL, json={'project_id': id}, headers={'Cookie': app.storage.user['cookie']})
        data = res.json()
        name = data['name']
        media = data['media']

    help_dialog = ui.dialog().props('full-width')
    with help_dialog, ui.card().style(replace='').classes('w-3/4'):
        with ui.row().classes('w-full items-center'):
            ui.label('Help').classes('text-h5')
            ui.space()
            ui.button(icon='close', on_click=help_dialog.close).props('flat round text-color="white"')
        with open('PYTHON/frontend/assets/help_project.md', 'r', encoding='utf-8') as f:
            ui.markdown(f.read())

    header = ui.header(elevated=True).classes('items-center justify-between')
    with header: # Create the header
        ui.link('📝', '/').style('font-size: 1.5rem;').tooltip('Home')
        proj_name = ui.label('Untitled project').style('font-size: 1.5rem; font-weight: 500;')
        proj_name.set_text(name)
        proj_name_input = ui.input('Project Name').props('filled dense standout label-color="white"').on('keydown.enter', lambda: edit_name(False))
        proj_name_input.set_value(name)
        proj_name_input.set_visibility(False)
        proj_name_edit_btn = ui.button(on_click=lambda: edit_name(True), icon='edit').props('flat round text-color="white"')
        ui.space()
        ui.button(on_click=help_dialog.open, icon='help').props('flat round text-color="white"').tooltip('Help')
        ui.button(on_click=logout, icon='logout').props('flat round text-color="white"').tooltip('Sign Out')

    #TODO this actually kinda works lmao
    media_exists = {}
    for m in media:
        #check for each type of media, and make a dict with the type as the key and whether or not it exists as the value
        if m['type'] == 'video':
            media_exists['video'] = True
        elif m['type'] == 'transcript':
            media_exists['transcript'] = True
        elif m['type'] == 'aisummary':
            media_exists['aisummary'] = True
        elif m['type'] == 'aiaudio':
            media_exists['aiaudio'] = True
        elif m['type'] == 'aivideo':
            media_exists['aivideo'] = True

    #use dict comprehension to create the options for the add_media select, include the options where the value is False
    add_media_options = {k: v for k, v in {'aisummary': 'AI-Summarized Notes', 'aiaudio': 'Audio Summary', 'aivideo': 'Video Summary'}.items() if k not in media_exists}
    #use dict comprehension to create the options for the preview_media select, include the options where the value is True
    preview_media_options = {k: v for k, v in {'video': 'Original Lecture Video', 'transcript': 'Lecture Transcription', 'aisummary': 'AI-Summarized Notes', 'aiaudio': 'Audio Summary', 'aivideo': 'Video Summary'}.items() if k in media_exists}
        
    with ui.row().classes('w-full flex-nowrap h-full'):
        with ui.card().classes('w-1/4 h-full backdrop-blur-lg'):
            ui.label('Picker').classes('text-h5')
            with ui.row().classes('items-center w-full'):
                add_media = ui.select(add_media_options, label='Add Media', value='notes').classes('grow')
                add_media_btn = ui.button(icon='add', on_click=lambda: ai_generate_media(add_media.value)).props('flat round text-color="white"')
            ui.separator()
            preview_media = ui.select(preview_media_options, label='Preview Media', on_change=lambda: change_preview(preview_media.value)).classes('w-full')

        with ui.card().classes('w-3/4 h-full backdrop-blur-lg'):
            ui.label('Preview').classes('text-h5')
            preview_area = ui.element('div').classes('w-full items-center justify-center h-full')
            with preview_area:
                with ui.column().classes('w-full items-center justify-center h-full'):
                    ui.icon('description', size='100px')
                    ui.label('Your media will appear here.').classes('text-h5')
                    ui.label('Select an option from the picker on the left to get started.')
            with ui.row():
                download_btn = ui.button('Download', icon='download', on_click=lambda: download_media(preview_media.value))
                delete_btn = ui.button('Delete', icon='delete', on_click=lambda: delete_media(preview_media.value))
    
    spinner_dialog.close()

    if new == True:
        await client.connected()
        success = await upload_file()
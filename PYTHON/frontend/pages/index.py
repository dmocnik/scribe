from nicegui import ui, app, Client
from nicegui.events import TableSelectionEventArguments
from config import DevelopmentConfig as config
from datetime import datetime
from common import logout
import httpx, asyncio

#TODO
# Make resizing the window not funky
# Potentially switch to single-column format with tabs on top instead of to side
# Parse the date
# Handle the table better when there are a lot of projects

API_URL = config.API_URL
PROJECT_CREATE_URL = f'{API_URL}/project/create'
PROJECT_READ_URL = f'{API_URL}/project/read'
PROJECT_LIST_URL = f'{API_URL}/project/list'

#PROJECT_EDIT_URL = f'{API_URL}/project'
#PROJECT_DELETE_URL = f'{API_URL}'

project_columns = [ # For now we have id, name, status, and last modified
    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': False}, # Hidden
    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
    {'name': 'status', 'label': 'Status', 'field': 'status', 'sortable': True},
    {'name': 'last_modified', 'label': 'Last Modified', 'field': 'last_modified', 'sortable': True},
]

async def content(client: Client): 
    async def handle_projects_selection(event: TableSelectionEventArguments): # Update the rename and delete buttons when the selection changes
        if len(projects_table.selected) == 0: # Disable the buttons if no projects are selected
            del_btn.props('disable')
            ren_btn.props('disable')
        elif len(projects_table.selected) == 1: # Enable both buttons if one project is selected
            del_btn.props(remove='disable')
            ren_btn.props(remove='disable')
        else: # Disable only the rename button if more than one project is selected
            del_btn.props(remove='disable')
            ren_btn.props('disable')

    async def handle_trashed_selection(event: TableSelectionEventArguments): # Update the restore and delete permanently buttons when the selection changes
        if len(trashed_table.selected) == 0: # Disable the buttons if no projects are selected
            restore_btn.props('disable')
            del_per_btn.props('disable')
        else: # Otherwise, enable both buttons
            restore_btn.props(remove='disable')
            del_per_btn.props(remove='disable')

    async def new_project():
        with ui.dialog() as new_project_dialog, ui.card().classes('w-1/2').style(replace=''): # Create a dialog for the new project name
            with ui.row().classes('w-full items-center'):
                ui.label('New Project').classes('text-h5')
                ui.space()
                ui.button(icon='close', on_click=lambda: new_project_dialog.close()).props('flat round text-color="white"')
            
            name_input = ui.input('Project Name', 
                validation={'Cannot be empty': lambda e: len(e) > 0},
                on_change=lambda e: create_btn.props('disable') if len(e.value) == 0 else create_btn.props(remove='disable')) \
                    .classes('w-full') \
                    .on('keydown.enter', lambda: new_project_dialog.submit(name_input.value) if name_input.validate() else None)

            with ui.row().classes('w-full'):
                ui.space()
                create_btn = ui.button('Create', on_click=lambda: new_project_dialog.submit(name_input.value)).props('disable')

        name = await new_project_dialog # Wait for the dialog to close and get the name
        if name: # If user gave a name, create the project
            working = ui.notification('Working...', spinner=True, timeout=0)
            async with httpx.AsyncClient() as c:
                res = await c.post(PROJECT_CREATE_URL, headers={'Cookie': app.storage.user['cookie']}, json={'project_name': name})
                id = res.json()
            if res.status_code == 200:
                working.dismiss()
                date_str = datetime.now().strftime('%B %e, %Y')
                projects_table.add_rows({'id': id, 'name': name, 'status': 'Waiting for Upload', 'last_modified': date_str})
                ui.notify(f'Project "{name}" created!', position='top-right', close_button=True, type='positive')
            else:
                working.dismiss()
                ui.notify('An error occurred. Please try again.', position='top-right', close_button=True, type='negative')

    async def rename_project():
        old_name = projects_table.selected[0]['name'] # Get the old name
        with ui.dialog() as rename_project_dialog, ui.card().classes('w-1/2').style(replace=''): # Create a dialog for the new project name
            with ui.row().classes('w-full items-center'):
                ui.label('Rename Project').classes('text-h5')
                ui.space()
                ui.button(icon='close', on_click=lambda: rename_project_dialog.close()).props('flat round text-color="white"')

            new_name_input = ui.input('Project Name', 
                validation={'Cannot be empty': lambda e: len(e) > 0},
                on_change=lambda e: confirm_rename_btn.props('disable') if len(e.value) == 0 else confirm_rename_btn.props(remove='disable')) \
                    .classes('w-full') \
                    .on('keydown.enter', lambda: rename_project_dialog.submit(new_name_input.value) if new_name_input.validate() else None)
            
            with ui.row().classes('w-full'):
                ui.space()
                confirm_rename_btn = ui.button('Rename', on_click=lambda: rename_project_dialog.submit(new_name_input.value)).props('disable')
                cancel_btn = ui.button('Cancel', on_click=lambda: rename_project_dialog.close())
            new_name_input.set_value(old_name) # Pre-fill the input with the old name

        new_name = await rename_project_dialog # Wait for the dialog to close and get the new name
        if new_name: # If the user gave a new name, rename the project
            if not (new_name == old_name): # If the new name is the not the same, update the name and notify the user
                idx = projects_table.rows.index(projects_table.selected[0])
                id = projects_table.rows[idx]['id']
                working = ui.notification('Working...', spinner=True, timeout=0)
                async with httpx.AsyncClient() as c:
                    res = await c.post(f'{API_URL}/project/{id}/edit', headers={'Cookie': app.storage.user['cookie']}, json={'project_name': new_name})
                if res.status_code == 200:
                    working.dismiss()
                    projects_table.rows[idx]['name'] = new_name
                    await deselect_all()
                    projects_table.update()
                    ui.notify(f'"{old_name}" renamed to "{new_name}"', position='top-right', type='positive')
                else:
                    working.dismiss()
                    ui.notify('An error occurred. Please try again.', position='top-right', close_button=True, type='negative')
            else: # Otherwise, don't do anything
                ui.notify('bruh')

    async def deselect_all(): # Deselect all rows in both tables.  This function is called to ensure the tables are updated rows are modified
        try:
            projects_table.selected = []
            trashed_table.selected = []
            projects_table.update()
            trashed_table.update()
        except NameError:
            pass

    async def trash_projects():
        rows_to_delete = projects_table.selected # Get the selected rows
        num_deleted = len(rows_to_delete) # Get the number of selected rows
        if num_deleted == 1: # If only one row is selected, get the name
            deleted_project_name = rows_to_delete[0]['name']
        working = ui.notification('Working...', spinner=True, timeout=0)
        results = []
        for row in rows_to_delete: # Move the selected rows to the trashed table, and update their status
            id = row['id']
            projects_table.rows.remove(row)
            row['status'] = 'Trashed'
            trashed_table.add_rows(row)
            async with httpx.AsyncClient() as c:
                res = await c.post(f'{API_URL}/project/{id}/delete', headers={'Cookie': app.storage.user['cookie']})
            results.append(res.status_code)
        if all([res == 200 for res in results]): # If all the requests were successful, dismiss the notification
            working.dismiss()
            await deselect_all() # Deselect all rows & update the tables
            if num_deleted == 1: # Notify the user of the action
                ui.notify(f'Trashed "{deleted_project_name}"', position='top-right', type='positive')
            else:
                ui.notify(f'Trashed {num_deleted} projects', position='top-right', type='positive')
        else: # Otherwise, display an error message
            working.dismiss()
            ui.notify('An error occurred. Please try again.', position='top-right', close_button=True, type='negative')

    async def restore_projects():
        rows_to_restore = trashed_table.selected # Get the selected rows
        num_restored = len(rows_to_restore) # Get the number of selected rows
        if num_restored == 1: # If only one row is selected, get the name
            restored_project_name = rows_to_restore[0]['name']
        for row in rows_to_restore: # Move the selected rows to the projects table, and update their status
            trashed_table.rows.remove(row)
            row['status'] = 'Huh?' 
            projects_table.add_rows(row)
        await deselect_all() # Deselect all rows & update the tables
        if num_restored == 1: # Notify the user of the action
            ui.notify(f'Restored "{restored_project_name}"', position='top-right', type='positive')
        else:
            ui.notify(f'Restored {num_restored} projects', position='top-right', type='positive')

    async def permanently_delete_projects():
        rows_to_delete = trashed_table.selected # Get the selected rows and the number of selected rows
        num_deleted = len(rows_to_delete)
        if num_deleted == 1: # If only one row is selected, get the name, and create the dialog text
            deleted_project_name = rows_to_delete[0]['name']
            text = f'Are you sure you want to delete "{deleted_project_name}"? This cannot be undone!'
        else:
            text = f'Are you sure you want to delete these {num_deleted} projects? This cannot be undone!'

        with ui.dialog() as permanently_delete_dialog, ui.card().classes('w-1/2').style(replace=''):  # Create a dialog for the delete confirmation
            with ui.row().classes('w-full items-center'):
                ui.label('Delete Permanently').classes('text-h5')
                ui.space()
                ui.button(icon='close', on_click=lambda: permanently_delete_dialog.close()).props('flat round text-color="white"')
        
            ui.label(text)

            with ui.row().classes('w-full'):
                ui.space()
                yes_btn = ui.button('Yes', on_click=lambda: permanently_delete_dialog.submit(True))
                no_btn = ui.button('No', on_click=lambda: permanently_delete_dialog.close())

        answer = await permanently_delete_dialog # Wait for the dialog to close and get the answer
        if answer == True: # If the user confirmed the deletion, delete the projects and notify the user
            for row in rows_to_delete:
                trashed_table.rows.remove(row)
            await deselect_all() # Deselect all rows & update the table
            if num_deleted == 1:
                ui.notify(f'Permanently deleted "{deleted_project_name}"', position='top-right', type='positive')
            else:
                ui.notify(f'Permanently deleted {num_deleted} projects', position='top-right', type='positive')

    async def open_project(name):
        ui.navigate.to(f'/project?id=testing&new=True&name={name}', new_tab=True)
        return

    # Main UI
    ui.query('.nicegui-content').classes('h-[calc(100vh-74px)]') # yuck https://github.com/zauberzeug/nicegui/discussions/2703#discussioncomment-8820280

    with ui.header(elevated=True).classes('items-center justify-between'): # Create the header
        ui.label('📝').style('font-size: 1.5rem;')
        ui.label('My Projects').style('font-size: 1.5rem; font-weight: 500;')
        ui.space()
        ui.button(on_click=lambda: ui.notify('no u'), icon='help').props('flat round text-color="white"').tooltip('Help') #TODO: Implement help
        ui.button(on_click=logout, icon='logout').props('flat round text-color="white"').tooltip('Sign Out')

    main_div = ui.row().classes('w-full gap-3 h-screen flex-nowrap') # Create the main div to contain the sidebar and the picker
    with main_div:
        sidebar = ui.card().classes('w-[250px] h-full backdrop-blur-lg')
        with sidebar:
            with ui.tabs(on_change=deselect_all).props('vertical inline-label').classes('w-full') as tabs: #Create the tabs for the sidebar
                projects_tab = ui.tab('Projects', icon='folder')
                trashed_tab = ui.tab('Trashed', icon='delete')
                projects_tab.disable()
                trashed_tab.disable()

        browser = ui.card().classes('w-full h-full backdrop-blur-lg') # Create a card to contain the tab panels
        with browser:
            with ui.column().classes('w-full items-center justify-center h-full'):
                spinner = ui.spinner(size='100px')

        await client.connected()
        async with httpx.AsyncClient() as c:
            res = await c.get(PROJECT_LIST_URL, headers={'Cookie': app.storage.user['cookie']}) #Get the projects
            if res.status_code == 200: # If the request was successful, clear the spinner and set the projects
                projects = res.json()
                for project in projects:
                    print(project['name'], project['id'], project['media'])
                projects_tab.enable()
                trashed_tab.enable()
                browser.clear()
            else: # otherwise, display an error message
                browser.clear() 
                with browser:
                    with ui.column().classes('w-full items-center justify-center h-full'):
                        ui.icon('error_outline', size='100px')
                        ui.label('There was an issue loading your projects.').classes('text-h5')
                        ui.label('Try reloading the page.')
                        return
        
        with browser:
            with ui.tab_panels(tabs, value=projects_tab) \
                .props('vertical') \
                .classes('w-full'): #Create the tab panel areas
            
                with ui.tab_panel(projects_tab).classes('p-0'):
                    #Create the projects table
                    projects_table = ui.table(columns=project_columns, rows=projects, row_key='id', selection='multiple', on_select=handle_projects_selection) \
                        .classes('w-full') \
                        .on('row-dblclick', lambda e: open_project(e.args[1]['name']))
                    
                    projects_table.columns[0]['classes'] = 'hidden' # Hide the ID column
                    projects_table.columns[0]['headerClasses'] = 'hidden'

                    with projects_table.add_slot('no-data'): # Add the message that shows if there are no projects
                        with ui.column().classes('full-width flex-center q-pa-md'):
                            ui.icon('warning', size='xl')
                            ui.label('No projects found. Click "New Project" to create one.')
                    
                    with projects_table.add_slot('top-right'): # Add the search bar
                        with ui.input(placeholder='Search').props('type=search clearable').bind_value(projects_table, 'filter').add_slot('append'):
                            ui.icon('search')

                    with projects_table.add_slot('top-left'): # Add the buttons
                        with ui.row().classes('gap-2'):
                            new_btn = ui.button('New Project', on_click=new_project, icon='add')
                            del_btn = ui.button('Delete', on_click=trash_projects, icon='delete').props('disable')
                            ren_btn = ui.button('Rename', on_click=rename_project, icon='edit').props('disable')

                with ui.tab_panel(trashed_tab).classes('p-0'): #TODO do something with the trashed projects
                    trashed_table = ui.table(columns=project_columns, rows=[], row_key='name', selection='multiple', on_select=handle_trashed_selection) \
                        .classes('w-full') # Create the table for the trashed projects
                    
                    trashed_table.add_slot('no-data', '''
                                            <div class="full-width column flex-center q-pa-md">
                                                <q-icon size="xl" name="warning" />
                                                <p>No projects found.</p>
                                            </div>''')
                    
                    with trashed_table.add_slot('top-right'): # Add the search bar
                        with ui.input(placeholder='Search').props('type=search clearable').bind_value(trashed_table, 'filter').add_slot('append'):
                            ui.icon('search')

                    with trashed_table.add_slot('top-left'): # Add the buttons
                        with ui.row().classes('gap-2'):
                            restore_btn = ui.button('Restore', icon='restore_from_trash', on_click=restore_projects).props('disable')
                            del_per_btn = ui.button('Delete Permanently', icon='delete_forever', on_click=permanently_delete_projects).props('disable')
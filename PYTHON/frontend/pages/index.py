from nicegui import ui, app
from nicegui.events import TableSelectionEventArguments
from config import DevelopmentConfig as config

#TODO
# Fix the height of the panels
# Fix the background acting fucky when a dialog opens
# Integrate with the backend
# Make it prettier
# Make resizing the window not fucky
# Potentially switch to single-column format with tabs on top instead of to side
# Disable buttons if no projects
# Parse the date maybe

API_URL = config.API_URL
PW_UPDATE_URL = f'{API_URL}/password/update'

project_columns = [ # For now we have name, status, and last modified
    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
    {'name': 'status', 'label': 'Status', 'field': 'status', 'sortable': True},
    {'name': 'last_modified', 'label': 'Last Modified', 'field': 'last_modified', 'sortable': True},
]

fake_projects = [  # Some sample data
    {'name': 'Project 1', 'status': 'Processing', 'last_modified': '2022-01-01'},
    {'name': 'Project 2', 'status': 'Ready', 'last_modified': '2022-01-02'},
    {'name': 'Project 3', 'status': 'Processing', 'last_modified': '2022-01-03'},
]

fake_trashed_projects = [
    {'name': 'Project 5', 'status': 'Trashed', 'last_modified': '2022-01-05'},
    {'name': 'Project 4', 'status': 'Trashed', 'last_modified': '2022-01-04'},
]

async def logout():
    app.storage.user.update({'authenticated': False})
    app.storage.user.update({'notifications': 'logout'})
    ui.open('/login')

async def content(): 
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
        with ui.dialog() as new_project_dialog, ui.card().classes('w-1/2'): # Create a dialog for the new project name
            with ui.row().classes('w-full items-center'):
                ui.label('New Project').classes('text-h5')
                ui.space()
                ui.button(icon='close', on_click=lambda: new_project_dialog.close()).props('flat round text-color="white"')
            
            name_input = ui.input('Project Name', 
                                  validation={'Cannot be empty': lambda value: len(value) > 0},
                                  on_change=lambda value: create_btn.props('disable') if len(value.value) == 0 else create_btn.props(remove='disable')) \
                                    .classes('w-full') \
                                    .props('outlined') \
                                    .on('keydown.enter', lambda: new_project_dialog.submit(name_input.value) if name_input.validate() else None)

            with ui.row().classes('w-full'):
                ui.space()
                create_btn = ui.button('Create', on_click=lambda: new_project_dialog.submit(name_input.value)).props('disable')

        name = await new_project_dialog # Wait for the dialog to close and get the name
        if name: # If user gave a name, create the project
            projects_table.add_rows({'name': name, 'status': 'Waiting for Upload', 'last_modified': '2022-01-01'})
            ui.notify(f'Project "{name}" created!', position='top-right', close_button=True, type='positive')

    async def rename_project():
        old_name = projects_table.selected[0]['name'] # Get the old name
        with ui.dialog() as rename_project_dialog, ui.card().classes('w-1/2'): # Create a dialog for the new project name
            with ui.row().classes('w-full items-center'):
                ui.label('Rename Project').classes('text-h5')
                ui.space()
                ui.button(icon='close', on_click=lambda: rename_project_dialog.close()).props('flat round text-color="white"')

            # TODO Fix this mess
            global confirm_rename_btn
            confirm_rename_btn = None

            new_name_input = ui.input('Project Name', 
                validation={'Cannot be empty': lambda e: len(e) > 0},
                on_change=lambda e: confirm_rename_btn.props('disable') if len(e.value) == 0 else confirm_rename_btn.props(remove='disable')) \
                    .classes('w-full') \
                    .props('outlined') \
                    .on('keydown.enter', lambda: rename_project_dialog.submit(new_name_input.value) if new_name_input.validate() else None)
            new_name_input.set_value(old_name) # Pre-fill the input with the old name
            
            with ui.row().classes('w-full'):
                ui.space()
                confirm_rename_btn = ui.button('Rename', on_click=lambda: rename_project_dialog.submit(new_name_input.value)).props('disable')
                cancel_btn = ui.button('Cancel', on_click=lambda: rename_project_dialog.close())

        new_name = await rename_project_dialog # Wait for the dialog to close and get the new name
        if new_name: # If the user gave a new name, rename the project
            if new_name == old_name: # If the name is the same, don't do anything
                ui.notify('bruh')
            else: # Otherwise, update the name and notify the user
                idx = projects_table.rows.index(projects_table.selected[0])
                projects_table.rows[idx]['name'] = new_name
                await deselect_all()
                projects_table.update()
                ui.notify(f'"{old_name}" renamed to "{new_name}"', position='top-right', type='positive')

    async def deselect_all(): # Deselect all rows in both tables.  This function is called to ensure the tables are updated rows are modified
        projects_table.selected = []
        trashed_table.selected = []
        projects_table.update()
        trashed_table.update()

    async def trash_projects():
        rows_to_delete = projects_table.selected # Get the selected rows
        num_deleted = len(rows_to_delete) # Get the number of selected rows
        if num_deleted == 1: # If only one row is selected, get the name
            deleted_project_name = rows_to_delete[0]['name']
        for row in rows_to_delete: # Move the selected rows to the trashed table, and update their status
            projects_table.rows.remove(row)
            row['status'] = 'Trashed'
            trashed_table.add_rows(row)
        await deselect_all() # Deselect all rows & update the tables
        if num_deleted == 1: # Notify the user of the action
            ui.notify(f'Trashed "{deleted_project_name}"', position='top-right', type='positive')
        else:
            ui.notify(f'Trashed {num_deleted} projects', position='top-right', type='positive')

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

        with ui.dialog() as permanently_delete_dialog, ui.card().classes('w-1/2'):  # Create a dialog for the delete confirmation
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
                ui.notify(f'Restored {num_deleted} projects', position='top-right', type='positive')

    # Main UI
    bg_image = "https://images5.alphacoders.com/707/707888.jpg" # Set the background image
    ui.query('body').style(f'''
                           background-image: url("{bg_image}");
                           background-size: cover;
                           background-repeat: no-repeat;
                           ''')
    
    with ui.header(elevated=True).classes('items-center justify-between'): # Create the header
        ui.label('📝 Scribe').style('font-size: 1.5rem;')
        ui.space()
        ui.button(on_click=logout, icon='logout')

    ui.label('My Projects').style('font-size: 3.75rem; font-weight: 500;') # Create the title

    main_div = ui.row().classes('w-full gap-3 h-dvh flex-nowrap') # Create the main div to contain the sidebar and the picker
    with main_div:
        sidebar = ui.card().classes('w-[250px] h-screen backdrop-blur-lg').style('background-color: #1d1d1dd9;')
        with sidebar:
            with ui.tabs(on_change=deselect_all).props('vertical inline-label').classes('w-full') as tabs: #Create the tabs for the sidebar
                projects = ui.tab('Projects', icon='folder')
                trashed = ui.tab('Trashed', icon='delete')

        picker = ui.card().classes('w-full h-screen backdrop-blur-lg').style('background-color: #1d1d1dd9;') # Create a card to contain the tab panels
        with picker:
            with ui.tab_panels(tabs, value=projects) \
                .props('vertical') \
                .classes('w-full backdrop-blur-lg') \
                .style('background-color: #1d1d1dd9;'): #Create the tab panel areas
            
                with ui.tab_panel(projects).classes('backdrop-blur-lg p-0').style('background-color: #1d1d1dd9;'):
                    projects_table = ui.table(columns=project_columns, rows=fake_projects, row_key='name', selection='multiple', on_select=handle_projects_selection) \
                        .classes('w-full backdrop-blur-lg') \
                        .style('background-color: #1d1d1dd9;') # Create the table for the projects
                    
                    with projects_table:
                        with projects_table.add_slot('top-right'): # Add the search bar
                            with ui.input(placeholder='Search').props('type=search clearable').bind_value(projects_table, 'filter').add_slot('append'):
                                ui.icon('search')

                        with projects_table.add_slot('top-left'): # Add the buttons
                            with ui.row().classes('gap-2'):
                                new_btn = ui.button('New Project', on_click=new_project, icon='add')
                                del_btn = ui.button('Delete', on_click=trash_projects, icon='delete').props('disable')
                                ren_btn = ui.button('Rename', on_click=rename_project, icon='edit').props('disable')


                with ui.tab_panel(trashed).classes('p-0'):
                    trashed_table = ui.table(columns=project_columns, rows=fake_trashed_projects, row_key='name', selection='multiple', on_select=handle_trashed_selection) \
                        .classes('w-full backdrop-blur-lg') \
                        .style('background-color: #1d1d1dd9;') # Create the table for the trashed projects
                    with trashed_table:
                        with trashed_table.add_slot('top-right'): # Add the search bar
                            with ui.input(placeholder='Search').props('type=search clearable').bind_value(trashed_table, 'filter').add_slot('append'):
                                ui.icon('search')

                    with trashed_table.add_slot('top-left'): # Add the buttons
                        with ui.row().classes('gap-2'):
                            restore_btn = ui.button('Restore', icon='restore_from_trash', on_click=restore_projects).props('disable')
                            del_per_btn = ui.button('Delete Permanently', icon='delete_forever', on_click=permanently_delete_projects).props('disable')
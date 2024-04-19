# Frontend

The frontend folder contains all the code related to the user interface and client-side functionality of the project.

## Structure

The frontend folder is organized as follows:
__pycache
assets
pages


Along with additional Python folders, including files relating to middleware and styles.

(The following was written with the assistance of GitHub Copilot to help generate some explanations)

### Pages
This section explains the contents of the foler "pages"

#### index.py
(Assisted by GitHub Copilot to help generate some explanations)

The function "content" contains several nested functions that handle various events and actions related to projects and project management. These functions include:
    - `handle_projects_selection`: Updates the rename and delete buttons when the selection changes in the projects table.
    - `handle_trashed_selection`: Updates the restore and delete permanently buttons when the selection changes in the trashed table.
    - `new_project`: Creates a new project by displaying a dialog for the user to enter the project name. If the user fills the dialog box with a name and clicks the Create button the project is created.
    - `rename_project`: Renames a selected project by displaying a dialog (similar to creating project) for the user to enter the new project name, replacing the old one.
    - `deselect_all`: Deselects all rows in both the projects and trashed tables.
    - `trash_projects`: Moves selected projects to the trashed table and updates their status.
    - `restore_projects`: This restores trashed projects. Will restore selected projects from the trashed table back to the main projects table.
    - `permanently_delete_projects`: Permanently deletes selected projects from the trashed table. Includes a confirmation dialog for the user.

    The `content` function is responsible for rendering the main content of the index page, including the UI elements and event handlers for project management. It interacts with the UI framework and makes HTTP requests to the server API for project creation, renaming, deletion, and restoration.


Here are more detailed explanations of two function implementations: `deselect_all()` and `open_project(name)`.

The `deselect_all()` function is essentially responsible for clearing the selection of rows in the tables, while the `open_project(name)` function handles the navigation to a specific project.

1. `deselect_all()` is an asynchronous function that deselects all rows in two tables (`projects_table` and `trashed_table`). This function is called to ensure that the tables are updated when rows are modified. It achieves this by setting the `selected` property of both tables to an empty list, and then calling the `update()` method on each table. The function also includes exception handling to catch a `NameError` in case the tables are not defined.

2. `open_project(name)` is an asynchronous function that opens a project. It takes a `name` parameter, which represents the name of the project to be opened. Inside the function, it uses the `ui.navigate.to()` method to navigate to a specific URL path that includes the project ID, a flag indicating that it's a new project, and the project name as query parameters. The `new_tab=True` argument ensures that the project is opened in a new tab. Finally, the function returns `None`.

The rest of the code in this file pertains to the implimentation of the user interface (UI).

#### login.py
This Python script pertains to the login page and the functionality associated with it. It imports necessary modules and defines several functions related to signing in, signing up, and resetting passwords. The code includes validation for sign-in inputs and sign-up inputs. It makes HTTP requests to the appropriate API endpoints for authentication purposes. 
The function content() represents the content of the login page.
It handles the login functionality, sign up functionality, and password reset functionality.
    The user can enter their email address and password to sign in, or they can sign up for a new account.
    The password must be at least 8 characters in length, must contain an uppercase letter, a lowercase letter, and a number. There is also a confirm password input taked by the user, in which the user types their password once again. If the intitial password and the confirm password don't match, the code will issue a warning.
    If the password is more than 50 characters, there will be validation warning saying "Too long".
    If the user forgets their password, they can request a password reset link to be sent to their email address. If the email the user inputs does not exist in the system, an error message will occur that says an account with the email doesn't exist. However, if the email does exist in the record, there will be the message: "Password reset requested. Check your email!".

#### project.py
This Python file pertains to the frontend, upload feature of Scribe.
The code firstly imports the necessary modules nicegui and common in order to accomplish this.
The code defines an async function named content that takes several parameters including client, id, new, and name.
The upload_file() function creates a dialog box for a user to uplaod a video file. This utilizes ui.dialog() and ui.card() from the NiceGUI library. It also has information
regard the maximum size of the file upload, which is 4 GB, and the length of the video file, which is 3 hours.
The change_preview() function is designed to have the preview be changed depending on the inputted file.
The edit_name() function is defined to handle the editing of the project name.
The content() function checks if the id parameter is None and displays a label indicating that the project ID is not given.
The code modifies the CSS class of a specific element to adjust the height of the content area.
The help_dialog() function is defined to display a help dialog when clicked.
The code creates a header section with various UI components including links, labels, buttons, and tooltips.
The code creates a row with two cards: a picker card and a preview card.
The picker card contains a select component for adding different types of media and a button for adding the selected media type.
If the `new` parameter is `True`, the code waits for the client to connect, then calls the `upload_file` function and prints the result.

#### reset_password.py
This Python file pertains to the password reset functionality. If the user chooses to reset the password, the password goes through a similar process as creating a password for the first time, such as validating that the password is at least 8 characters long, containing an uppercase letter, etc.

The code begins by importing necessary modules and dependencies:

nicegui: A module that provides a user interface for the application.
app: An instance of the application.
Client: A class representing the client.
httpx: A module for making HTTP requests.
re: A module for regular expressions.
config: A module containing configuration settings.
The code defines several constants:

API_URL: The URL of the API used for password reset.
ACCOUNT_LOGIN_CODE_URL: The URL for verifying the login code.
PW_RESET_URL: The URL for resetting the password.
DEBOUNCE_TIME: The debounce time for input fields.
The code defines an async function named content that takes a client object, an email string, and a code string as parameters. This function is responsible for rendering the content of the password reset page.

Within the content function, there is a block of code that displays a spinner while the page is loading. It uses the ui.dialog() and ui.card() functions from the nicegui module to create a spinner dialog.

The verify_code function is defined within the content function. It is responsible for verifying the password reset code entered by the user and changing the password if the code is valid.

Inside the verify_code function, there is a block of code that handles the password change process. It sends a POST request to the PW_RESET_URL endpoint with the new password and the user's authentication cookie. If the request is successful (status code 200), it submits the password change by calling the submit method of the pw_dialog dialog. Otherwise, it displays an error notification.

The code then defines the UI elements for the password reset page using the ui module functions. It creates input fields for the new password and confirm password, adds validation rules to ensure password strength and match, and sets up a button to trigger the password change process.

After the UI elements are defined, the code opens the spinner dialog to indicate that the page is loading.

The code sends a POST request to the ACCOUNT_LOGIN_CODE_URL endpoint to verify the email and code entered by the user. If the request is successful (status code 200), it updates the user's authentication information and waits for the password change dialog to be submitted.

If the password change dialog is submitted with a True result, it updates the user's notification and authentication status, navigates to the login page, and returns.

If the request returns a status code of 401, it displays an error notification indicating that the code is invalid.

If any other error occurs during the request, it displays a generic error notification.

Finally, the code updates the UI to display the password reset page content by calling the content function with the appropriate parameters.


#### verify_account.py
This file pertains to the account verification functionality. It includes the implementation of a function called verify_code() that is responsible for verifying a user's account activation code.

The verify_code() function is defined as an asynchronous function using the async keyword. This allows the function to use await to pause execution and wait for certain operations to complete.

Inside the verify_code() function, there is a with statement that creates a dialog and a card using the ui.dialog() and ui.card() functions from the nicegui library. The with statement ensures that the dialog and card are properly closed after their use.

Within the dialog and card, a spinner is displayed using the ui.spinner() function. This spinner indicates that the verification process is in progress.

The spinner_dialog.open() method is called to open the dialog and display the spinner.

An HTTP POST request is made to the ACCOUNT_ACTIVATE_URL endpoint using the httpx.AsyncClient().post() method. The request includes the user's email and activation code as JSON data.

The response from the server is stored in the res variable.

If the response status code is 200, it means that the activation code is valid. In this case, the user's account is updated with the verified email and authentication status. Additionally, a notification is displayed to the user indicating the success of the account creation. Finally, the user is navigated to the home page using the ui.navigate.to() function.

If the response status code is 401, it means that the activation code is invalid. In this case, an error notification is displayed to the user indicating that the code is invalid.

If the response status code is neither 200 nor 401, it means that an error occurred during the verification process. In this case, an error notification is displayed to the user indicating that an error occurred.

After the verification process is complete, the spinner_dialog.close() method is called to close the dialog and hide the spinner.

The verify_code() function is called when the email and code parameters are not None. This happens when the function is called with specific email and code values, indicating that the user wants to verify their account.

Overall, this code handles the verification of a user's account activation code by making an HTTP request to the server and updating the user's account status accordingly. It also provides visual feedback to the user during the verification process using a spinner and notifications.

### Others
#### common.py
This file handles the logout functionality of the application, as well as some notification functionality for different events, namely logging in, logging out, account verification, and password change.
The logout() function is responsible for logging out the user. It performs the following steps:

Clears the user data stored in the app.storage.user object using the clear() method.
Updates the app.storage.user object by setting the value of the notifications key to 'logout' using the update() method.
Opens the /login page using the open() function from the ui module.
check_notifications(): This function is used to handle notifications for different events. It performs the following steps:

Retrieves the value of the notifications key from the app.storage.user object using the pop() method. The pop() method removes the key from the dictionary if it exists.
Checks the value of notifications and performs different actions based on its value:
If the value of notifications is 'login', it displays a notification using the notify() function from the ui module. The notification includes a personalized greeting message "Hello, (username)!".
If the value of notifications is 'logout', it displays a notification indicating that the user has successfully logged out: "Successfully logged out!".
If the value of notifications is 'account_create_success', it displays a notification indicating that the account has been verified successfully and the user is now logged in: "Account verified successfully! You are now logged in."
If the value of notifications is 'pw_change_success', it displays a notification indicating that the password has been changed successfully and the user needs to log in again: "Password changed successfully! Please login again."

The notify() function is a utility function from the ui module that displays a notification on the screen. It accepts various parameters such as the message content, position, type, color, and more. It uses the context.get_client() function to get the client object and enqueue the notification message to be displayed.

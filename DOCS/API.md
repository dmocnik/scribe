### Account Management Module

## Functionality Overview
Login

    Endpoint: /login
    Method: POST
    Purpose: Authenticates user login credentials.
    Actions:
        Validates email and password against the database.
        Generates a session UUID for the authenticated user.
        Sets session data and attaches session cookie to the response.

Get Email

    Endpoint: /email
    Method: GET
    Purpose: Retrieves the email associated with the current session.
    Dependencies: Requires a valid session cookie.

Password Reset Request

    Endpoint: /password/reset/request
    Method: POST
    Purpose: Initiates a password reset process for a user.
    Actions:
        Generates a random code for password reset.
        Inserts reset code into the database with expiration time.
        Sends a password reset email containing the reset link and code.

Login with Code

    Endpoint: /account/login/code
    Method: POST
    Purpose: Allows login using a verification code sent via email.
    Actions:
        Verifies the provided code against stored codes in the database.
        Creates a session for the user if the code is valid.

Password Reset

    Endpoint: /password/reset
    Method: POST
    Purpose: Resets user password.
    Actions:
        Verifies the validity of the reset code.
        Updates the user's password in the database.
        Expires the reset code after use.

Password Update

    Endpoint: /password/update
    Method: POST
    Purpose: Allows the user to update their password.
    Actions:
        Verifies the old password.
        Updates the password with the new one in the database.

Delete Account

    Endpoint: /account/delete
    Method: POST
    Purpose: Deletes the user account and associated data.

Create Account

    Endpoint: /account/create
    Method: POST
    Purpose: Creates a new user account.
    Actions:
        Checks if the email already exists in the database.
        Generates a verification code and sends a verification email.

Deactivate Account

    Endpoint: /account/deactivate
    Method: POST
    Purpose: Deactivates the user account.

Activate Account

    Endpoint: /account/activate
    Method: POST
    Purpose: Activates a user account using a verification code.


### Media Management Module

The functionalities are managing media files within the Scribe application. 

## Functionality Overview
Create Project

    Endpoint: /project/create
    Method: POST
    Purpose: Creates a new project associated with the current user session.
    Actions:
        Connects to the database and retrieves the user ID from the session email.
        Creates a new project object with the provided name and user ID.
        Adds the project to the database and returns its ID.

Get Project Info

    Endpoint: /project/read
    Method: POST
    Purpose: Retrieves information about a specific project.
    Actions:
        Validates the user's access to the project.
        Retrieves media associated with the project from the database.
        Returns project information along with its media.

Update Project

    Endpoint: /project/{project_id}/edit
    Method: POST
    Purpose: Updates the name of a project.
    Actions:
        Validates the user's ownership of the project.
        Updates the project name in the database.

Delete Project

    Endpoint: /project/{project_id}/delete
    Method: POST
    Purpose: Deletes a project and associated media.
    Actions:
        Validates the user's ownership of the project.
        Deletes the project and its associated media from the database.

List Projects

    Endpoint: /project/list
    Method: GET
    Purpose: Retrieves a list of projects associated with the current user session.
    Actions:
        Retrieves project information and associated media from the database.
        Returns a list of projects along with their media.

Get Media

    Endpoint: /project/{project_id}/media/{media_id}
    Method: GET
    Purpose: Retrieves media content associated with a project.
    Actions:
        Validates the user's ownership of the project and access to the media.
        Retrieves media content from the database and returns it.

Create Media

    Endpoint: /project/{project_id}
    Method: POST
    Purpose: Uploads media content to a project.
    Actions:
        Validates the user's ownership of the project.
        Creates a new media object with the provided content and associates it with the project.
        Adds the media object to the database.

Read Video, Transcript, AI Summary, AI Audio, AI Video

    Endpoints: /project/{project_id}/video, /project/{project_id}/transcript, /project/{project_id}/aisummary, /project/{project_id}/aiaudio, /project/{project_id}/aivideo
    Methods: GET
    Purpose: Retrieves specific types of media content associated with a project.
    Actions:
        Validates the user's ownership of the project and access to the specific type of media.
        Retrieves the corresponding media content from the database and returns it.

Delete Media

    Endpoint: /project/{project_id}/media/{media_id}/delete
    Method: POST
    Purpose: Deletes a specific media item from a project.
    Actions:
        Validates the user's ownership of the project and access to the media.
        Deletes the media item from the database.


### FastAPI Application

This file represents a FastAPI application that serves as the backend for the Scribe application. It consists of two main routers: one for handling user authentication and account management (login) and another for managing media files (media).

## Functionality Overview
Router Initialization

    FastAPI instance is created to serve as the web application.

Router Inclusion

    Two routers (login.account and media.media) are included in the main application router.
    These routers handle requests related to user authentication/account management and media management, respectively.

Request Handling

    The login router handles requests related to user login, registration, password reset, and account management.
    The media router handles requests related to managing media files, such as uploading, retrieving, updating, and deleting media content associated with user projects.


### Settings Configuration

This defines a Settings class using Pydantic for managing application settings. It loads environment variables using dotenv and retrieves values for database connection, SMTP server configuration, frontend URL, and other necessary settings.

## Configuration Class

    Settings: Defines a class inheriting from BaseSettings for managing application settings.
        DATABASE_URI: String representing the URI for connecting to the database. Default value is provided as a fallback.
        Other settings like smtp_server, smtp_port, smtp_username, password, and FRONTEND_URL are retrieved from environment variables using os.environ.get.
        Database URI is constructed dynamically from environment variables for database connector, MySQL user, password, database name, and host.
        Error handling is implemented to handle exceptions when retrieving SMTP credentials from environment variables.
        Upon initialization, the class prints the loaded environment variables and the constructed database URI for debugging purposes.


### Database Model Definition

This script defines SQLAlchemy database models for user authentication, authorization, and project management.

## Model Classes

#   User:
        Table Name: 'user'
        Columns:
            id: Integer primary key representing the user's unique identifier.
            email: String representing the user's email address. It is non-nullable.
            password_hash: String representing the hashed password of the user. Non-nullable.
            disabled: Boolean flag indicating whether the user account is disabled. Default is True.
            name: String representing the user's name. Nullable.
        Relationships:
            codes: One-to-Many relationship with 'Codes' table, representing password reset codes associated with the user.
            project: One-to-Many relationship with 'Project' table, representing projects created by the user.

#   Codes:
        Table Name: 'codes'
        Columns:
            id: Integer primary key representing the unique identifier of the code.
            user_ID: Integer foreign key referencing the user's id in the 'user' table.
            code_hash: String representing the hashed code value.
            code_expiry: DateTime representing the expiration date and time of the code.
        Relationships:
            user: Many-to-One relationship with 'User' table, representing the user associated with the code.

#   Project:
        Table Name: 'project'
        Columns:
            id: Integer primary key representing the unique identifier of the project.
            name: String representing the name of the project. Non-nullable.
            user_id: Integer foreign key referencing the user's id in the 'user' table.
        Relationships:
            user: Many-to-One relationship with 'User' table, representing the user who owns the project.
            media: One-to-Many relationship with 'Media' table, representing media files associated with the project.

#   Media:
        Table Name: 'media'
        Columns:
            id: Integer primary key representing the unique identifier of the media.
            name: String representing the name of the media file. Non-nullable.
            type: Enum representing the type of the media file (video, transcript, etc.). Non-nullable.
            content: LONGBLOB representing the content of the media file.
            project_id: Integer foreign key referencing the project's id in the 'project' table.
        Relationships:
            project: Many-to-One relationship with 'Project' table, representing the project associated with the media file.


### Verifier

This script sets up session management using FastAPI's session extension and implements a basic session verifier for user authentication.

## Session Data Model

#   SessionData:
        Inherits from BaseModel.
        Attributes:
            email: String representing the user's email.
            code: Optional string representing additional session data (default is an empty string).

## Session Management Configuration

#   Cookie Parameters:
        Configures parameters for session cookies.

#   SessionCookie:
        Configures session cookies with UUID as the identifier.
        Attributes:
            cookie_name: Name of the session cookie.
            identifier: Identifier for the session.
            auto_error: Boolean indicating whether to raise an error automatically if session verification fails.
            secret_key: Secret key for encoding the session data.
            cookie_params: Cookie parameters configured earlier.

#   InMemoryBackend:
        Backend implementation for storing session data in memory.

## Session Verifier

#   BasicVerifier:
        Inherits from SessionVerifier.
        Constructor initializes verifier properties.
        Implements verify_session method to verify the session.

## Verifier Initialization

#   verifier:
        Instance of BasicVerifier initialized with appropriate parameters.
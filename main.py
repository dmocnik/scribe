# MIT License

# Copyright (c) 2024

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# [ Structure of code ]
# main.py: The main file that runs the program
# api directory: Contains the API for this software
# PYTHON directory: Other misc python files (maybe move API here?)

# Attempt to import all necessary libraries
try:
    import os, time, sys, subprocess, collections # General
    from rich import print as rich_print # Pretty print
    from rich.traceback import install # Pretty traceback
    install() # Install traceback
except ImportError as e:
    print("[INFO] You are missing one or more libraries. Please use PIP to install any missing ones.")
    print("Try running `python3 -m pip install -r requirements.txt` OR `pip install -r requirements.txt`.")
    print(f"Traceback: {e}")
    quit()

# Determine the main project directory, for compatibility (the absolute path to this file)
maindirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# [ OPTIONS ]
BACKEND_PATH = "PYTHON.api.app"
BACKEND_LAUNCH = ['uvicorn', f'{BACKEND_PATH}:app', '--reload', '--host', '0.0.0.0']

FRONTEND_PATH = os.path.join(maindirectory, "PYTHON", "frontend", "frontend_main.py")
FRONTEND_LAUNCH = ['python3', FRONTEND_PATH]

SYSTEM_QUEUE_PATH = os.path.join(maindirectory, "PYTHON", "queue", "runner_flask.py")
SYSTEM_QUEUE_LAUNCH = ['python3', SYSTEM_QUEUE_PATH]

# Custom low-level functions
def print(text="", log_filename="", end="\n", max_file_mb=10):
    global maindirectory
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    if log_filename == "":
        log_filename = f"{script_name}.log"
    log_file_path = os.path.join(maindirectory, "LOGS", log_filename)
    if not os.path.exists(log_file_path):
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        open(log_file_path, 'a').close()
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > max_file_mb * 1024 * 1024:
        try:
            with open(log_file_path, "w") as f:
                f.write("")
        except Exception as e:
            rich_print(f"[red][ERROR][/red]: {e}")
            rich_print(f"[red][ERROR][/red]: Could not clear log file at {log_file_path}.")
    try:
        with open(log_file_path, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    except Exception as e:
        rich_print(f"[red][ERROR][/red]: {e}")
        rich_print(f"[red][ERROR][/red]: Could not write to log file at {log_file_path}.")
    rich_print(text, end=end)

def tail(file, n):
    lines = collections.deque(maxlen=n)
    for line in file:
        lines.append(line)
    return lines

# [ MAIN ]
if __name__ == "__main__":
    # Print hello ASCII text
    print("""[white]
   _____           _ _          
  / ____|         (_) |         
 | (___   ___ _ __ _| |__   ___ 
  \\___ \\ / __| '__| | '_ \\ / _ \\
  ____) | (__| |  | | |_) |  __/
 |_____/ \\___|_|  |_|_.__/ \\___|
[/white]""", log_filename="startup.log")
    # Print welcome text in cycling colors
    welcome_text = "Welcome to Scribe. Starting necessary services..."
    color_cycling = ["red", "orange1", "yellow", "green", "blue", "blue_violet", "violet"]
    for i, letter in enumerate(welcome_text):
        rich_print(f"[{color_cycling[i % len(color_cycling)]}]{letter}[/{color_cycling[i % len(color_cycling)]}]", end="")
        time.sleep(0.01)
    print("\n")
    time.sleep(1)

    # Get arguments from kwargs
    try:
        sys_args = sys.argv[1:]
        arguments = {}
        for value in sys_args:
            if value.startswith("--"):
                value = value[2:]
            if "=" not in value:
                arguments[value] = True
            else:
                value = value.split("=")
                arguments[value[0]] = value[1]
    except IndexError:
        print(log_filename="errors.log", text="[red][ERROR][/red]: No arguments were provided. You must provide arguments in the format of `argument=value`")
        print(log_filename="errors.log", text=f"Example: `python3 {sys.argv[0]} webserver=False`")
        print(log_filename="errors.log", text=f"Please see the README for more info, or try `python3 {sys.argv[0]} help`")
        # TODO: Readme help
        quit()

    # Override everything and show help-docs if user includes help in arguments
    if "help" in arguments:
        print("Welcome to Scribe!")
        print(f"usage: python3 {sys.argv[0]} [OPTIONS]")
        print("This script hosts a full stack webapp using NiceGUI for frontend and Flask for backend, which allows users to upload video/audio/text lectures and use AI to convert them to note documents!")
        print("[OPTIONS]")
        print("help: Displays this help message.")
        quit()

    # Parse the arguments
    opts_dict = {}
    def parse_arg(opts_dict, arg_key, arg_val, default_val="", required=False):
        try:
            if str(arg_val).lower() == "true":
                arg_val = True
            elif str(arg_val).lower() == "false":
                arg_val = False
            opts_dict[arg_key] = arg_val
            return arg_val
        except KeyError:
            if required:
                print(f"[red][ERROR][/red]: No {arg_key} was provided. This is a required argument. Please see `python3 {sys.argv[0]} help` for more info.")
                quit()
            else:
                print(f"[gold1][INFO][/gold1]: No {arg_key} was provided. Assuming value of `{default_val}`.")
                opts_dict[arg_key] = default_val
                return default_val
    
    # Parse all arguments
    parse_arg(opts_dict, arg_key="webserver", arg_val=arguments.get("webserver", True), default_val=True, required=False)

    # Display all arguments in console
    print(f"Selected options: {opts_dict}\n")

    # [ Run the program ]
    # If show_webserver enabled, then run the webserver interface
    # Otherwise, run the program via command line interface
    if opts_dict.get("webserver", False):
        print("[gold1][INFO][/gold1]: webserver enabled, running webserver...")
        # Copy all environment variables to the subprocess
        env = os.environ.copy()
        # Run the backend by invoking Flask app in ./PYTHON/api/app.py using subprocess
        backend_process = subprocess.Popen(BACKEND_LAUNCH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        # Run the frontend by invoking NiceGUI in ./PYTHON/frontend/frontend_main.py using subprocess
        frontend_process = subprocess.Popen(FRONTEND_LAUNCH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        # Run the system queue by invoking runner.py in ./PYTHON/queue/runner.py using subprocess
        system_queue_process = subprocess.Popen(SYSTEM_QUEUE_LAUNCH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        # Periodically display the output of the subprocesses
        while True:
            try:
                # Check if the processes are still running
                if backend_process.poll() is not None:
                    print("[red][ERROR][/red]: Backend process has stopped running. Exiting...")
                    quit()
                if frontend_process.poll() is not None:
                    print("[red][ERROR][/red]: Frontend process has stopped running. Exiting...")
                    quit()
                if system_queue_process.poll() is not None:
                    print("[red][ERROR][/red]: System queue process has stopped running. Exiting...")
                    quit()
                print(f"[gold1][INFO][/gold1]: Heartbeat check-in. Sleeping for 60 seconds...")
                # Print the output of the processes
                print(f"[gold1][INFO][/gold1]: Backend process output: {backend_process.stdout.read().decode()}")
                print(f"[gold1][INFO][/gold1]: Frontend process output: {frontend_process.stdout.read().decode()}")
                print(f"[gold1][INFO][/gold1]: System queue process output: {system_queue_process.stdout.read().decode()}")
                # Flush the output buffer for all processes
                backend_process.stdout.flush()
                frontend_process.stdout.flush()
                system_queue_process.stdout.flush()
                time.sleep(60)
            except KeyboardInterrupt:
                print("[gold1][INFO][/gold1]: Keyboard interrupt detected, exiting webserver cleanly...")
                # Kill the processes if they exist
                if backend_process and backend_process.poll() is None:
                    backend_process.kill()
                if frontend_process and frontend_process.poll() is None:
                    frontend_process.kill()
                if system_queue_process and system_queue_process.poll() is None:
                    system_queue_process.kill()
                quit()
    else:
        print("[gold1][INFO][/gold1]: webserver disabled, running program in standalone mode for testing...")
        while True:
            try:
                # TODO: Main logic for setting up standalone class
                print("Not implemented yet. Press CTRL + C to quit.")
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("[gold1][INFO][/gold1]: Keyboard interrupt detected, exiting cleanly...")
                quit()
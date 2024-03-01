# Guide to Using our Remote Server
Hello! This is a guide on using our remote server for development, which has a live running version of our Docker deployment (database, backend, frontend, and SMTP setup)

As a reminder, the server is my personal gaming laptop, which I wiped and installed Ubuntu Server on, on campus. I have set up a ZeroTier network for us to connect to the server remotely. This guide will walk you through the process of joining the network and connecting to the server, as well as what remote dev features are available to you.

The primary use case for this will be interacting with the live version of Scribe, which is already running. It'll also give you access to any neccesary compute for messing with AI. Later on, we will purchase a domain and a VPS to proxy requests through the Zerotier VPN to the computer, but for now, this will keep us going.

##### Note: Please don't abuse my computer or my alt-account in gmail, which is also included on the system! 

##### 2nd Note: Just so I don't destroy the lifespan of my computer, I will only have it running when necessary. Please ask on Discord for whenever you want it on.

## How are we accomplishing this?
- [ZeroTier](https://www.zerotier.com/) for creating a virtual network, which we use to connect to our remote server (Gaming PC)
- [VS Code](https://code.visualstudio.com/) for remote development via SSH (Remote SSH lets you manage our database, docker containers, etc. from your own machine, but remotely 😎)

## Recommended VSCode Extensions
I recommend you have several extensions installed in VSCode to make your life easier. Here are a couple of the ones I use for this:

- Docker: for managing Docker containers directly in VSCode
- Remote - SSH: for connecting to our remote server (required)
- SQLTools and SQLTools MySQL/MariaDB: for managing our database directly in VSCode
- Task Runner: for running tasks directly in VSCode (like rebuilding the Docker container)

These can all be downloaded in the Extensions view of VSCode (`Ctrl+Shift+X`).

## Downloading and Installing ZeroTier

What is zerotier? Zerotier is a virtual mesh network that allows you to connect to a virtual network from anywhere in the world. It's a great tool for remote development as it allows you to connect to a server as if you were on the same local network.

### On Windows:

1. Visit the ZeroTier download page at https://www.zerotier.com/download/.
2. Click on the "Download" button for Windows.
3. Once the download is complete, open the installer and follow the instructions to install ZeroTier.

### On Linux:

1. Open a terminal.
2. Download and install ZeroTier with the following commands:

```bash
curl -s https://install.zerotier.com | sudo bash
```

## Joining the `sad_student_club_anonymous` Network 😎

1. After installing ZeroTier, you can join a network by right-clicking the ZeroTier icon in your system tray (Windows) or running a command in your terminal (Linux).
2. For Windows, right-click the ZeroTier icon in your system tray, select "Join Network", and enter the network ID "e4da7455b2f3cc81".
3. For Linux, run the following command in your terminal:

```bash
sudo zerotier-cli join e4da7455b2f3cc81
```

4. After you've joined the network, you will need to wait for your request to be approved by me and I've assigned you a private IP. Once your request has been approved, you will be connected to the network.

## Developing Remotely with VS Code

1. Install the "Remote - SSH" extension in VS Code. You can find this by searching for "Remote - SSH" in the Extensions view (`Ctrl+Shift+X`).
2. Open the Command Palette (`Ctrl+Shift+P`) and run the "Remote-SSH: Connect to Host..." command.
3. Enter `capstone@10.243.0.100` as the SSH host and click "Connect".
4. Enter the password (`squid6-flounder$-Emporium`) when prompted.

Remember, you need to be connected to the ZeroTier network before you can connect to the server via SSH.

## Accessing Scribe

I've already set up Docker and built the image for Scribe. Once in the VSCode remote session, just open the scribe folder. You can then develop directly on the server.

- I have also setup temp support for Task Runner. Whenenever you need to rebuild the Docker container, just click on the `Run on Docker` task inside the Task Runner menu in the bottom left of VSCode whilst remotely connected and the scribe project is open.

- In addition, if you have the Docker, SQLTools, and SQLTools MySQL/MariaDB extensions installed, you can manage both Docker containers and the SQL database directly in the remote VSCode window too!
- In order to actually play with scribe and its services, you need this VSCode remote window open. You can then click on the `Ports` button in the bottom window of VSCode and forward/tunnel these ports to your local machine:
  - `96` for the MariaDB Database
  - `97` for the Backend API
  - `98` for the Frontend
  - (These are all from the live running Docker containers)
- Please let me know if you have any questions!
<div class="row">
    <div class="column">
        <h1>Scribe</h1>
        <p>Upload and transcribe videos using AI, then convert to a note doc!</p>
        <a href="https://forthebadge.com"><img src="https://forthebadge.com/images/badges/docker-container.svg" alt="Badge 1"></a>
        <a href="https://forthebadge.com"><img src="https://forthebadge.com/images/badges/contains-tasty-spaghetti-code.svg" alt="Badge 2"></a>
        <a href="https://forthebadge.com"><img src="https://forthebadge.com/images/badges/license-mit.svg" alt="Badge 3"></a>
    </div>
</div>

### More documentation coming soon!

## Features
- Compiled Docker image for easy deployment
- Tested with Python 3.10

## Directory/File Structure
- `BUILD/` - Contains any additional assets for building and deploying the application
- `CONFIG/` - Contains configuration files and scripts (i.e. DB setup)
- `PYTHON` - Contains Python scripts and classes for the application
- `DOCS/` - Contains documentation, meeting notes, presentations, and other related files

- `.gitignore` - Specifies intentionally untracked files to ignore
- `.vscode/` - Contains VS Code settings and tasks
- `LICENSE` - The main license file for the application
- `README.md` - This file, a manual for your application

- `Dockerfile` - Dockerfile for creating a Docker image of the application
- `docker-compose.yaml` - Docker Compose file for defining and running multi-container Docker applications
- `.env` - Environment file for Docker Compose, contains environment variables
- `.dockerignore` - Specifies intentionally untracked files to ignore for Docker compilation

- `main.py` - Main Python script for running the application

## Installation
### Prerequisites/Requirements
- System compatible with Docker. We recommend using the latest version of Ubuntu or Ubuntu Server.
- Preferably 4GB of RAM or more, for running our Docker application.
- Docker and Docker-Compose itself should be installed on your system. For Ubuntu users, you can install Docker with the following commands from Docker's guide:
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker Engine:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
- If you will be running from source, make sure you have the following packages installed (adjust package manager according to your distro):
```bash
sudo apt-get install python3 python3-pip
```

## Development

### Setup MariaDB
Download MariaDB [here](https://mariadb.org/download/)

#### Linux (Tested on Debian)

Run ``sudo su`` to run as root.

Assuming the tarball is still in the Downloads directory
Run the following commands, changing \<USER\> to the user you used to download the tarball:
```sh
groupadd mysql
useradd -g mysql mysql
cd /usr/local
tar -zxvpf /home/<USER>/mariadb-11.4.0-preview-linux-systemd-x86_64.tar.gz
ln -s mariadb-11.4.0-preview-linux-systemd-x86_64/ mysql
cd mysql
./scripts/mariadb-install-db --user=mysql
chown -R root .
chown -R mysql data
```
Run 
```sh
sudo /usr/local/mysql/bin/mariadbd-safe
```
to start the daemon

Add this to the end of your (non-root) .bashrc file to invoke mariadb commands:

```sh
export PATH="/usr/local/mysql/bin:$PATH"
```

## About the Developers
Info will be added soon!

## Additional Note(s)
- Version schema: `YEAR.MONTH.DAY.REVISION`
- Healthcheck should be implemented on Flask side
- Search IDE for "TODO:" as there's placeholders there!

## License
This project is licensed under the MIT License. The full license can be found in the GitHub repository.
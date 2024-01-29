# scribe
Upload and transcribe videos using AI, then convert to a note doc!

# Development

## Setup MariaDB
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

## Setup Python Virtual Environment

See [here](https://docs.python.org/3/library/venv.html)
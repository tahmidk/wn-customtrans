# WN CustomTrans
A webapp extension to the wn-downtrans project built on the Flask framework and served using uWSGI and Nginx. WN CustomTrans is a webapp that allows the user to register, manage and read chapters from a list of supported webnovel host websites and is capable of applying customized user dictionary translations of novel jargon, and honorific translations.

## Install Docker and Docker Compose

### Windows Setup

#### 1 Enable Hyper-V in elevated cmd
```bash
> bcdedit /set hypervisorlaunchtype auto
```

#### 2 Install [WSL2 Linux Kernel Update](https://docs.microsoft.com/en-us/windows/wsl/install-manual#step-4---download-the-linux-kernel-update-package)

#### 3 Install [Docker Desktop](https://docs.docker.com/desktop/windows/install/)

#### 4 Expose the Windows Docker Daemon
1. Open Docker Desktop
2. Enable **Settings** > **General** > **Expose daemon on tcp://localhost:2375 without TLS** option
3. **Apply & Restart**

### Linux Setup

#### 1 Install the latest version of [Docker CE](https://support.netfoundry.io/hc/en-us/articles/360057865692-Installing-Docker-and-docker-compose-for-Ubuntu-20-04)

#### 2 Install the latest version of Docker Compose
```bash
# Fetch the latest version of Docker Compose
$ VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*\d')

# Set the installation destination
$ DESTINATION=/usr/local/bin/docker-compose

# Download the latest version Docker Compose package
$ sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION

# Grant the installation execute permissions
$ sudo chmod 755 $DESTINATION
```

Verify ``docker`` and ``docker-compose`` commands are recognized by system.
#### Add bashrc definition for Docker Host
Finally, in \~/.bashrc, add the following variable definition to the end of the file so we can access the the Windows Docker daemon exposed in the previous step inside Windows Subsystem Linux
```bash
# Append the following to the end of ~/.bashrc
export DOCKER_HOST=tcp://localhost:2375

# Save changes to ~/.bashrc and exit

# Apply changes
$ source ~/.bashrc
```

## Setting up a Production Server
Setting up a production server involves using Docker Compose to create the Nginx and Flask App dockers and running the docker containers on the host server.

### Windows Subsystem Linux
Ensure that the ``DOCKER_HOST`` environment variable is set and Docker Desktop is running on Windows

### Ubuntu/Unix
Start the docker daemon using the following command
```bash
$ sudo systemctl enable docker
```

After cloning the project onto the host machine, navigate to the root of the project ``/path/to/wn-customtrans`` and run the following command:
```bash
# Move to the root project directory
$ cd /path/to/wn-customtrans

# Build the docker containers using docker compose
$ docker-compose build

# Launch the docker compose containers
$ docker-compose
```

## Setting up a Development Server
This section goes through the steps needed to setup and run WNCustomTrans using a Flask dev server for development.

### First-time Step

#### Setup python3 virtual environment
```bash
# Move to the root directory of the project
$ cd /path/to/wn-customtrans

# Create the python virtual environment
$ python -m venv venv

# Activate the python virtual environment
$ source venv/bin/activate

# Install the project requirements
$ pip install -r requirements.txt
```

### Recurring Step

#### Run development server
```bash
# Enter the python virtual environment
$ ./venv/bin/activate

# Set Flask environment variables
$ set FLASK_APP=app
$ set FLASK_ENV=development

# Option 1: Launch the development server using the run.py script
$ python run.py

# Option 2: Launch the development server using Flask
$ flask run
```
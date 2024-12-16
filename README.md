<h1> SkinScan </h1>

<h3> Table of Contents </h3>

- [Running the Django Project:](#running-the-django-project)
  - [Create .env File in Repository Root Folder](#create-env-file-in-repository-root-folder)
  - [Run development server:](#run-development-server)
    - [macOS/Linux:](#macoslinux)
    - [Windows WSL:](#windows-wsl)
  - [Database Migrations](#database-migrations)
  - [Unit Tests](#unit-tests)
  - [Deactivating the Virtual Environment:](#deactivating-the-virtual-environment)
- [Installation](#installation)
  - [macOS/Linux:](#macoslinux-1)
    - [Set Up Python Virtual Environment \& Install Dependencies](#set-up-python-virtual-environment--install-dependencies)
  - [Windows WSL:](#windows-wsl-1)
    - [Installing Python 3.11 on Ubuntu WSL](#installing-python-311-on-ubuntu-wsl)
    - [Set Up Python Virtual Environment \& Install Dependencies](#set-up-python-virtual-environment--install-dependencies-1)
  - [Optional: Enable Nvidia CUDA GPU Support \[WSL\]](#optional-enable-nvidia-cuda-gpu-support-wsl)
    - [Step 1: Update Nvidia Drivers](#step-1-update-nvidia-drivers)
    - [Step 2: Install CUDA Toolkit](#step-2-install-cuda-toolkit)
    - [Step 3: Install cuDNN](#step-3-install-cudnn)
    - [Step 4: Run Test Script to Verify GPU Utilization:](#step-4-run-test-script-to-verify-gpu-utilization)


## Running the Django Project:

### Create .env File in Repository Root Folder
Make sure the .env file contains the following:
```sh
# Django secret key
SECRET_KEY = <KEY_VALUE>

# development / production
DJANGO_ENV = development

```
### Run development server:

#### macOS/Linux:
1. Navigate to the `Django` project root folder:
    ```bash
    cd server
    ```
2. Run the `Django` development server:
    ```bash
    python3 manage.py runserver
    ```
3. Open browser and navigate to:
    ```bash
    http://127.0.0.1:8000
    ```

#### Windows WSL:
1. Navigate to the `Django` project root folder:
    ```bash
    cd server
    ```
2. Run the `Django` development server:
    ```bash
    python manage.py runserver
    ```
3. Open browser and navigate to:
    ```bash
    http://127.0.0.1:8000
    ```


### Database Migrations

If any changes are made to the `Django` models (database schemas), the changes need to be migrated to the database(s). Execute the following commands from the `Django` project root folder: 

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py migrate --database=db_images
```


### Unit Tests

To run the `Django` unit tests, execute the following commands from the `Django` project root folder:
```bash
python3 manage.py test    
```


### Deactivating the Virtual Environment:

Once you are done, deactivate the Python virtual environment using:
```bash
deactivate
```


## Installation

### macOS/Linux:

#### Set Up Python Virtual Environment & Install Dependencies 
1. Navigate to the repository root folder in your terminal:
    ```bash
    cd /path/to/repository
    ```
2. Create a Python virtual environment:
    ```bash
    python3 -m venv venv
    ```
3. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```


### Windows WSL:
> **Note**: this guide is written for `WSL2` using `Ubuntu 22.04 LTS (Jammy)`. 


#### Installing Python 3.11 on Ubuntu WSL

<details>
<summary>Show/Hide</summary>

> Python 3.11 is not included in the default Ubuntu repository so we need to add a PPA in order to install. If you are using a different Ubuntu version you need to verify that Python 3.11 is provided [here](https://launchpad.net/%7Edeadsnakes/+archive/ubuntu/ppa) or use a different PPA.

1. Add `deadsnakes PPA` to the system:
    ```bash
    sudo add-apt-repository ppa:deadsnakes/ppa
    ```
2. Update package list to ensure the new repository is included:
    ```bash
    sudo apt update
    ```
3. Install Python 3.11 and tk dependencies:
    ```bash
    sudo apt install python3.11 python3-tk tk-dev
    ```
4. Verify installation & base Python installation intact:
    ```bash
    python3 --version
    python3.11 --version
    ```
5. Intall `venv` for Python 3.11:
    ```bash
    sudo apt install python3.11-venv
    ```

</details>


#### Set Up Python Virtual Environment & Install Dependencies 
1. Navigate to the repository root folder in your terminal:
    ```bash
    cd /path/to/repository
    ```
2. Create a Python virtual environment:
    ```bash
    python3.11 -m venv venv
    ```
3. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
4. Upgrade `pip` inside the virtual environment
    ```bash
    pip install --upgrade pip
    ```
5. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```


### Optional: Enable Nvidia CUDA GPU Support [WSL]
> In order to utilize the GPU for TensorFlow operations, additional setup is needed.

<details>
<summary>Show/Hide</summary>

> **Note**: verify that you have the hardware & system requirements needed: [TensorFlow website](https://www.tensorflow.org/install/pip#windows-wsl2)


#### Step 1: Update Nvidia Drivers

Ensure that you have the latest Nvidia GPU drivers installed. Most cards with updated drivers should support CUDA: [Nvidia website](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#step-1-install-nvidia-driver-for-gpu-support)


#### Step 2: Install CUDA Toolkit

Download the `CUDA Toolkit 12.3.2` installer for x86 from the [Nvidia website](https://developer.nvidia.com/cuda-12-3-2-download-archive?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_local)

Open `WSL` in terminal and navigate to the directory you saved the installer - run the following commands:
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin

sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600

wget https://developer.download.nvidia.com/compute/cuda/12.3.2/local_installers/cuda-repo-wsl-ubuntu-12-3-local_12.3.2-1_amd64.deb

sudo dpkg -i cuda-repo-wsl-ubuntu-12-3-local_12.3.2-1_amd64.deb

sudo cp /var/cuda-repo-wsl-ubuntu-12-3-local/cuda-*-keyring.gpg /usr/share/keyrings/

sudo apt-get update

sudo apt-get -y install cuda-toolkit-12-3
```

Verify installation using the following command:
```bash
nvcc --version
```

If the command doesn't work, you need to add the `CUDA Toolkit` to the environment variables:

1. Open the shell configuration in `nano`:
    ```bash
    nano ~/.bashrc
    ```
2. Add the following lines to the end of the file (to keep your custom configurations separate)
    ```bash
    export PATH=/usr/local/cuda/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    ```
3. Save the file and reload the shell configuration:
    ```bash
    source ~/.bashrc
    ```
4. Verify that the `nvcc` command now works:
    ```bash
    nvcc --version
    ```

#### Step 3: Install cuDNN

> **Note**: for this step you need to create an Nvidia developer account (for free) to download the library.

Download `cuDNN v8.9.7 (December 5th, 2023), for CUDA 12.x` for Ubuntu x86 from the [Nvidia website](https://developer.nvidia.com/rdp/cudnn-archive). 

Open `WSL` in terminal and navigate to the directory you saved the installer - run the following commands:

1. Install the local repository:
    ```bash
    sudo dpkg -i cudnn-local-repo-ubuntu2204-8.9.7.29_1.0-1_amd64.deb
    ```
    >**Note**: if you get the message about the `keyring`, copy the command from the output and run it in the terminal before proceeding with the next step.
2. Update package list:
    ```bash
    sudo apt update
    ```
3. Install the `cuDNN` library:
    ```bash
    sudo apt install -y libcudnn8
    ```
4. Verify installation success:
    ```bash
    dpkg -l | grep libcudnn
    ```
    You should see output similar to:
    ```bash
    ii  libcudnn8    8.9.7.29-1+cuda12.2   amd64    cuDNN runtime libraries
    ```

#### Step 4: Run Test Script to Verify GPU Utilization:
1. Navigate to the repository root folder in your terminal:
    ```bash
    cd /path/to/repository
    ```
2. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
3. Run the GPU test script
    ```bash
    python3.11 dev_utils/test_gpu.py
    ```
> **Note**: TensorFlow will silently default to using the CPU if it can't utilize the GPU. If you suspect that this is happening you can enable explicit device logging by editing the script and changing the parameter in the following line to `True`:
```Python
tf.debugging.set_log_device_placement(False)
```

</details>

<h1>🩺🔬 SkinScan </h1>

  <img src="https://github.com/user-attachments/assets/bba35aea-185e-40d7-97dc-414b16e213de" alt="SkinScan Overview" width="45%" align="right" style="margin-left: 15px;" />
<p>
<br><br>
  <strong>SkinScan</strong> is a skin cancer detector web application that allows users to upload images of their skin conditions. Our system uses a <strong>multi-class ML-model</strong> that analyses uploaded images, in conjunction with other features such as <strong>age</strong> and <strong>sex</strong>, to determine the probable type of condition and whether it is <strong>benign (noncancerous)</strong> or <strong>malignant (cancerous)</strong>.
</p>
<br><br>

<p>
  <img src="https://github.com/user-attachments/assets/bb5e108a-714e-43bf-b47e-e4cf3154b172" alt="AI Explainability Example" width="45%" align="left" style="margin-right: 15px;" />
  For legal and ethical concerns, the aim of this system is not to provide any medical diagnosis but rather a <strong>recommendation</strong> on whether the user should seek out professional medical assistance. The goal is to <strong>minimise false negatives</strong> (i.e., optimise recall) while retaining acceptable overall <strong>model accuracy</strong>.🎯 This ensures users can trust the model’s predictions for <strong>benign conditions</strong>. The model slightly <strong>overrepresents malignant conditions</strong> to avoid missing true positives, as the risks of missing malignant conditions far outweigh the inconvenience of recommending medical advice for benign conditions.
</p>

<p>
  <img src="https://github.com/user-attachments/assets/cd0f23d9-6e0a-4af3-b8df-b345a3827904" alt="Admin Panel Overview" width="45%" align="right" style="margin-left: 15px;" />
   To enhance <strong>transparency 🔍</strong> and build <strong>user trust 🤝</strong>, the results include <strong>AI explainability measures</strong>.🤖💡 These measures display a <strong>percentage score</strong> for each feature’s relative impact on the prediction, along with a <strong>heatmap overlay</strong> highlighting the areas of the input image that our ML model focused on during processing.
</p>
<br><br>
<br><br>

<p>
  <img src="https://github.com/user-attachments/assets/d66103b6-987c-4ff0-b980-a44b888c9be1" alt="Analytics Dashboard" width="45%" align="left" style="margin-right: 15px;" />
  The system’s web application includes an <strong>admin panel UI</strong> for <strong>administrator users</strong>. This panel provides access to <strong>system analytics</strong>📊 and other functionalities, such as managing the <strong>ML-pipeline</strong> to train new models or replace the current active model used for running inference on user data. Administrators can view <strong>previous model versions</strong>, review their <strong>hyperparameters</strong>, and compare <strong>performance metrics</strong> across different versions using visual <strong>graphs</strong>. The <strong>admin panel</strong> also provides detailed insights into the <strong>usage</strong> and <strong>accuracy</strong> of the system, helping developers and healthcare professionals make informed improvements. This ensures the tool remains <strong>accurate</strong>, <strong>effective</strong>, and <strong>trustworthy</strong>.
</p>




<h3>📑 Table of Contents </h3>

- [Svelte Web-app \[Frontend\]](#svelte-web-app-frontend)
- [Running Django \[Backend\]](#running-django-backend)
  - [Create .env File in Repository Root Folder](#create-env-file-in-repository-root-folder)
  - [Run development server](#run-development-server)
    - [macOS/Linux:](#macoslinux)
    - [Windows WSL:](#windows-wsl)
  - [Database Migrations](#database-migrations)
  - [Unit Tests](#unit-tests)
  - [Deactivating the Virtual Environment](#deactivating-the-virtual-environment)
- [Installation \[Backend\]](#installation-backend)
  - [macOS/Linux:](#macoslinux-1)
    - [Set Up Python Virtual Environment \& Install Dependencies](#set-up-python-virtual-environment--install-dependencies)
  - [Windows WSL:](#windows-wsl-1)
    - [Installing Python 3.11 on Ubuntu WSL](#installing-python-311-on-ubuntu-wsl)
    - [Set Up Python Virtual Environment \& Install Dependencies](#set-up-python-virtual-environment--install-dependencies-1)
  - [Optional: Enable Nvidia CUDA GPU Support \[Linux / WSL\]](#optional-enable-nvidia-cuda-gpu-support-linux--wsl)
    - [Step 1: Update Nvidia Drivers](#step-1-update-nvidia-drivers)
    - [Step 2: Install CUDA Toolkit](#step-2-install-cuda-toolkit)
    - [Step 3: Install cuDNN](#step-3-install-cudnn)
    - [Step 4: Run Test Script to Verify GPU Utilization](#step-4-run-test-script-to-verify-gpu-utilization)
- [Development team](#development-team)


## Svelte Web-app [Frontend]

To run locally, refer to the instructions inside the `Client` directory [README](https://git.chalmers.se/courses/dit826/2024/group6/-/tree/main/client?ref_type=heads#sv).


## Running Django [Backend]

### Create .env File in Repository Root Folder

Make sure the .env file contains the following:
```sh
# Django secret key
SECRET_KEY = <KEY_VALUE>

# Use "False" for production
DEBUG = "True"
```


### Run development server

#### macOS/Linux:

1. Navigate to the `Django` project root folder
    ```bash
    cd server
    ```
2. Run the `Django` development server
    ```bash
    python3 manage.py runserver
    ```
3. Open browser and navigate to:
    ```bash
    http://127.0.0.1:8000
    ```

#### Windows WSL:

1. Navigate to the `Django` project root folder
    ```bash
    cd server
    ```
2. Run the `Django` development server
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


### Deactivating the Virtual Environment

Once you are done, deactivate the Python virtual environment using:
```bash
deactivate
```


## Installation [Backend]

### macOS/Linux:

#### Set Up Python Virtual Environment & Install Dependencies 

1. Navigate to the repository root folder in your terminal
    ```bash
    cd /path/to/repository
    ```
2. Create a Python virtual environment
    ```bash
    python3 -m venv venv
    ```
3. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
4. Install the required dependencies
   
   on Linux:
    ```bash
    pip install -r requirements.txt
    ```

    on macOS:
    ```bash
    pip install -r requirements-mac.txt
    ```   


### Windows WSL:

> **Note**: this guide is written for `WSL2` using `Ubuntu 22.04 LTS (Jammy)`. 


#### Installing Python 3.11 on Ubuntu WSL

<details>
<summary>Show/Hide</summary>

> Python 3.11 is not included in the default Ubuntu repository so we need to add a PPA in order to install. If you are using a different Ubuntu version you need to verify that Python 3.11 is provided [here](https://launchpad.net/%7Edeadsnakes/+archive/ubuntu/ppa) or use a different PPA.

1. Add `deadsnakes PPA` to the system
    ```bash
    sudo add-apt-repository ppa:deadsnakes/ppa
    ```
2. Update package list to ensure the new repository is included
    ```bash
    sudo apt update
    ```
3. Install Python 3.11 and tk dependencies
    ```bash
    sudo apt install python3.11 python3-tk tk-dev
    ```
4. Verify installation & base Python installation intact
    ```bash
    python3 --version
    python3.11 --version
    ```
5. Intall `venv` for Python 3.11
    ```bash
    sudo apt install python3.11-venv
    ```

</details>


#### Set Up Python Virtual Environment & Install Dependencies 

1. Navigate to the repository root folder in your terminal
    ```bash
    cd /path/to/repository
    ```
2. Create a Python virtual environment
    ```bash
    python3.11 -m venv venv
    ```
3. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
4. Upgrade `pip` inside the virtual environment
    ```bash
    pip install --upgrade pip
    ```
5. Install the required dependencies
    ```bash
    pip install -r requirements.txt
    ```


### Optional: Enable Nvidia CUDA GPU Support [Linux / WSL]

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

If the last command doesn't work, you need to add the `CUDA Toolkit` to the environment variables:

1. Open the shell configuration in `nano` (or any other editor)
    ```bash
    nano ~/.bashrc
    ```
2. Add the following lines to the end of the file (to keep your custom configurations separate)
    ```bash
    export PATH=/usr/local/cuda/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    ```
3. Save the file and reload the shell configuration
    ```bash
    source ~/.bashrc
    ```
4. Verify that the `nvcc` command now works
    ```bash
    nvcc --version
    ```

#### Step 3: Install cuDNN

> **Note**: for this step you need to create an Nvidia developer account (for free) to download the library.

Download `cuDNN v8.9.7 (December 5th, 2023), for CUDA 12.x` for Ubuntu x86 from the [Nvidia website](https://developer.nvidia.com/rdp/cudnn-archive). 

Open `WSL` in terminal and navigate to the directory you saved the installer - run the following commands:

1. Install the local repository
    ```bash
    sudo dpkg -i cudnn-local-repo-ubuntu2204-8.9.7.29_1.0-1_amd64.deb
    ```
    >**Note**: if you get the message about the `keyring`, copy the command from the output and run it in the terminal before proceeding with the next step.
2. Update package list
    ```bash
    sudo apt update
    ```
3. Install the `cuDNN` library
    ```bash
    sudo apt install -y libcudnn8
    ```
4. Verify installation success
    ```bash
    dpkg -l | grep libcudnn
    ```
    **Note**: you should see output similar to:
    ```bash
    ii  libcudnn8    8.9.7.29-1+cuda12.2   amd64    cuDNN runtime libraries
    ```

#### Step 4: Run Test Script to Verify GPU Utilization

1. Navigate to the repository root folder in your terminal
    ```bash
    cd /path/to/repository
    ```
2. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
3. Run the GPU test script
    ```bash
    python3.11 dev_utils/test_gpu.py
    ```
> **Note**: TensorFlow will silently default to using the CPU. If you suspect that your GPU is not being utilized you can enable explicit device logging by editing the script and changing the parameter in the following line to `True`:
```Python
tf.debugging.set_log_device_placement(False)
```


</details>

## Development Team👩‍💻👨‍💻


The project has been developed over the course of **8 weeks** by the following:

- Kaisa Arumeel
- Amirpooya Asadollahnejad   
- Erik Lindstrand 
- Arvin Rahimi  
- Konstantinos Rokanas
- Alexander Säfström


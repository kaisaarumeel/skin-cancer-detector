# group6

## Installation & Running

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
3. Install Python 3.11:
    ```bash
    sudo apt install python3.11
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


#### Set Up Python Virtual Environment
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


### Optional: Enable Nvidia CUDA GPU Support (WSL)
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
    python3.11 test_gpu.py
    ```
> **Note**: TensorFlow will silently default to using the CPU if it can't utilize the GPU. If you suspect that this is happening you can enable explicit device logging by editing the script and changing the parameter in the following line to `True`:
```Python
tf.debugging.set_log_device_placement(False)
```

</details>


### Running the Django Project:

#### Create .env File in Repository Root Folder
Make sure the .env file contains the following:
```sh
# Django secret key
SECRET_KEY = <KEY_VALUE>

# development / production
DJANGO_ENV = development

```

#### macOS/Linux:
1. Navigate to the `SkinScan` project root folder:
    ```bash
    cd server/SkinScan
    ```
2. Run the Django development server:
    ```bash
    python3 manage.py runserver
    ```
3. Open browser and navigate to:
    ```bash
    http://127.0.0.1:8000
    ```

#### Windows WSL:
1. Navigate to the `SkinScan` project root folder:
    ```bash
    cd server/SkinScan
    ```
2. Run the Django development server:
    ```bash
    python3.11 manage.py runserver
    ```
3. Open browser and navigate to:
    ```bash
    http://127.0.0.1:8000
    ```


#### Deactivating the Virtual Environment:

Once you are done, deactivate the Python virtual environment using:
```bash
deactivate
```



<!--

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://git.chalmers.se/courses/dit826/2024/group6.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://git.chalmers.se/courses/dit826/2024/group6/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.

-->
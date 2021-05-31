# Coral USB Accelerator

You can greatly increase the inference speed by using a Google Coral USB Accelerator. 

Your best bet is to follow [the official getting started guide](https://coral.ai/docs/accelerator/get-started), but I will document the process here as well.

## Installation

### On a Mac

Follow [these instructions](https://coral.ai/docs/accelerator/get-started/#runtime-on-mac), or blindly trust the next steps.

**NOTE:** You must use python version 3.5-3.8 or `pycoral` will not install completely. Follow the instructions in the [README.md](README.md#python-version) to install the correct version of python.

1. Ensure you have either `homebrew` or `macports` installed.
2. Download and unpack the Edge TPU runtime:
    ```bash
    curl -LO https://github.com/google-coral/libedgetpu/releases/download/release-frogfish/edgetpu_runtime_20210119.zip

    unzip edgetpu_runtime_20210119.zip
    ```
3. Install the Edge TPU runtime. You will be required to enter your password. Select "No" when prompted to enable maximum operating frequency.
    ```bash
    cd edgetpu_runtime

    sudo bash install.sh
    ```
4. Install PyCoral into the virtual environment where Carl lives.
    - If you followed the `git` install:
        1. Activate your virtual environment (steps vary depending on how you manage your environment).
        2. Run the following to install pycoral:
            ```bash
            python -m pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral
            ```
    - If you followed the `pipx` install:
        1. Run the following to install pycoral into `carl`s virtual environment:
            ```bash
            pipx inject housecarl pycoral --pip-args "--extra-index-url https://google-coral.github.io/py-repo/"
            ```
5. Plug the USB Accelerator into your computer using a USB 3.0 cable.

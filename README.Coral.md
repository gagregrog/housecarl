# Coral USB Accelerator

You can greatly increase the inference speed by using a Google Coral USB Accelerator. 

Your best bet is to follow [the official getting started guide](https://coral.ai/docs/accelerator/get-started), but I will document the process here as well.

## Installation

### On a Mac (maybe Linux [not Raspberry Pi])

If you are brave, try running `carl --setup-coral` to have Carl assist you with this setup. If this does not work, try the manual steps below.

You can follow [these instructions](https://coral.ai/docs/accelerator/get-started/#runtime-on-mac), or try my steps below.

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

### Raspberry Pi

If you are brave, try running `carl --setup-coral` to have Carl assist you with this setup. If this does not work, try the manual steps below.

Follow the official instructions [here](https://coral.ai/docs/accelerator/get-started/#runtime-on-linux), or try my manual steps below.

If you are installing this on a Raspberry Pi, make sure that you are using python 3.7. Later versions require a version of lib6c that is not supported on the Pi.

1. Add Google's package repository to the system:
    ```bash
    echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

    sudo apt-get update
    ```
2. Install the Edge TPU Runtime:
    ```bash
    sudo apt-get install libedgetpu1-std
    ```
3. Install PyCoral into your virtual environment. This is where my steps differ from the official documentation. Again, make sure you are using python 3.7.
    1. With your virtualenv activated, install pycoral:
        ```bash
        pip install https://github.com/google-coral/pycoral/releases/download/v1.0.1/pycoral-1.0.1-cp37-cp37m-linux_armv7l.whl
        ```
    2. With your virtualenv activated, install tflite-runtime:
        ```bash
        pip install https://github.com/google-coral/pycoral/releases/download/v1.0.1/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl
        ```
4. Carl should now be able to use Pycoral to interface with the Coral.

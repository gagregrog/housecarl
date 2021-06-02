# Raspberry Pi Installation Notes

Before following the regular installation instructions, please follow these instructions in order to setup your Raspberry Pi for the OpenCV install.

## Installing Python and Pipx

Before continuing, you'll likely want to set up something to manage your virtual environments. This isn't required, but is always a good idea. Use your preferred method. I will go through the `pyenv` install steps.

1. Install `pyenv` via the [GitHub checkout method](https://github.com/pyenv/pyenv#basic-github-checkout)
2. Install `pyenv-virtualenv` [as a pyenv plugin](https://github.com/pyenv/pyenv-virtualenv#installing-as-a-pyenv-plugin).
3. The instructions for how to initialize `pyenv` seem pointlessly confusing in their README. All you need to do is add the following to the ***top*** of `~/.bashrc`. And while you're at it, go ahead and add the path for pipx (we'll install that shortly):
    ```bash
    # setup pyenv
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"

    # set path for pipx
    export PATH="$HOME/.local/bin:$PATH"
    ```
    - **Note:** Make sure this is at the top of your `.bashrc`, otherwise `pyenv` won't work in non-interactive shells.
4. Make sure you have installed all of the build requirements for Ubuntu as recommended in the [pyenv docs](https://github.com/pyenv/pyenv/wiki#suggested-build-environment). This is subject to change, but at the time of this writing this amounts to:
    ```bash
    sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

    ```

5. Now we're ready to install python with `pyenv`. Make sure to install with `--enabled-shared`. This will take longer to build, but will give you or more complete set of packages.
6. 
**NOTE:** If you will be using a Google Coral USB Accelerator, you must install python version 3.7.

To install python 3.7.10, for example:

    ```bash
    env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.7.10
    ```

If you'd like, you can set this as your global install with `pyenv global 3.7.10`.

7. Install pipx (if you want to install Carl with him): `python3 -m pip install --user pipx`
9. Set path: `python3 -m pipx ensurepath`
    - This will likely tell you that the path is already set (since we set it in our `~/.bashrc` earlier).

## Prerequisites for OpenCV

Before you can install Carl, we need to ensure that OpenCV will be able to install properly.

To do this, I recommend you follow Adrian Rosenbock's [tutorial for installing OpenCV 4 on a Raspberry Pi](https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/). Basically, you will be installing everything that has ever existed. Refer to the article for the most up to date information, but for your convenience, at the time of writing this amounts to the following:

```bash
sudo apt-get update && sudo apt-get upgrade -y; \
sudo apt-get install build-essential cmake pkg-config -y; \
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev -y; \
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y; \
sudo apt-get install libxvidcore-dev libx264-dev -y; \
sudo apt-get install libfontconfig1-dev libcairo2-dev -y; \
sudo apt-get install libgdk-pixbuf2.0-dev libpango1.0-dev; \
sudo apt-get install libgtk2.0-dev libgtk-3-dev -y; \
sudo apt-get install libatlas-base-dev gfortran -y; \
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103 -y; \
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5 -y; \
sudo apt-get install python3-dev -y; \
```

To be fair, I don't know that all of this is strictly required, but OpenCV did not work for me before the above, and it did after, so...

## Installing Carl

At this point, you should be able to return to the main set of installation instructions and install the app.

If you only plan on running the app, I would recommend to install the CLI using pipx.

If you want to modify anything, you'll be better off cloning the repo and running the app directly.

If you will be using a Google Coral USB Accelerator, you will need to follow additional setup instructions after installing Carl. Remember, you must use python3.7 with the Coral on a Raspberry pi with Buster OS. You can find more information on setting up the Coral in [README.Coral.md](/README.Coral.md).

Go there now, or return to the main [README.md](README.md#installation).

# housecarl

## Overview

What can [Carl](https://en.wikipedia.org/wiki/Housecarl) do for you?

  - Carl can process video from these sources: 
      - Built-in Webcam
      - USB Camera
      - Raspberry Pi Camera
      - Wyze RTSP Stream
      - Other streaming source
  - Carl will monitor your video feed and keep a lookout for you. He can perform object detection using the following models:
      - MobileNet_SSD
      - YoloV3
      - MobileNetV2 on Google Coral Edge TPU
  - Carl has a keen eye. If he notices anything out of the ordinary, he'll send you a push notifications via [Pushover](https://pushover.net/).
  - Carl has a good memory. If you want, he can record interesting events for you.

## How do I use it?

Make sure you have followed the [installation instructions](#installation).

Once all dependencies have been installed, you can run carl from a terminal prompt.

If you've installed by cloning the git repo, run: 

```bash
python main.py
```

If you've installed as a package via `pipx`, simply run:

```bash
carl
```

See the [configuration options](#configuration) for fine grain control.

See the available overrides passable as [CLI options](#cli-overrides).

### Configuration

By default, the app will search for `config.json` at the root of the project. If this file is not found, it will load the default configuration found at [housecarl/library/config.default.json](housecarl/library/config.default.json).

#### Configuration Options

The configuration options fall into five main categories:

  - `video` - If this category is omitted all defaults will be used
  - `detector` - If this category is omitted all defaults will be used
  - `monitor` - If this category is omitted all defaults will be used
  - `writer` - Omit this category to disable event recordings
  - `pushover` - Omit this category to disable event notifications

To view all default values, please reference the [default configuration file](housecarl/library/config.default.json). These defaults will be merged with any configuration options you provide.

The behavior of each option is explained below:

  ##### video

  - `src`: `str` or `int` - A webcam source, a stream url, or `usePiCamera`.
  - `width`: `int` - Width to resize frame before processing. Height adjusted automatically. This will impact the video display and recording size.
  - `display`: `bool` - Whether or not to display the video.
  - `name`: `str` - The name of the display window.

##### detector

  - `threaded`: `bool` - Perform detections in a thread. This results in faster video feed, but results in stale detections drawn to frame.
  - `model`: `str` - One of `mobilenet`, `yolo`, or `coral`. If not found, the model files will be downloaded.
  - `min_confidence`: `float: [0, 1]` - Weak detections will be filtered out.
  - `show_detections`: `bool` - Draw detections on the frame. Impacts video display, recorded events, and notification images.
  - `classes`: `List<str>` - The names of all classes you want to detect. Will be checked against the available classes for the chosen detector. Invalid values will be ignored.

##### monitor

  - `min_detection_ratio`: `float: [0, 1]` - Min value to accept for the ratio (frames_with_detections / frames_processed) to consider a detection series valid.
  - `min_detection_frames`: `int` - Min number of frames with detections before considering a detection series valid.
  - `detection_lapse_timeout`: `int` - Number of seconds without a detection to trigger detection series termination.
  - `max_detection_duration`: `int` - Maximum duration in seconds of a detection series.
  - `post_detection_debounce`: `int` - Number of seconds to wait after a successful detection series before initiating a new detection series.

##### writer

Omit this category to disable event recordings.

  - `fps`: `int` - Stream FPS may vary, so you may find this needs tweaking depending on the video source.
  - `timeout`: `int` or `float` - Amount of time the writer thread should pause before looking for new frames to write.
  - `out_dir`: `str` - Absolute path to a directory for saving videos. Defaults to [recordings](recordings). Video writer will create subdirectories by date.
  - `fourcc`: `str` - [FOURCC](https://www.fourcc.org/) codec to use for writing.
  - `buffer_size`: `int` - Size of the writer's queue. Larger values result in more "cushion" on either side of an event recording.
  - `min_disk_space`: `int` or `float` - If you have less than this quantity of free space, recordings will not be saved.

##### pushover

Omit this category to disable push notifications.

  - `mock`: `bool` - Don't send push notifications, but log mock to the console.
  - `user_key`: `str` - Your [Pushover user key](https://pushover.net/dashboard).
  - `api_token`: `str` - Your [Pushover app token](https://pushover.net/api#registration).

### CLI

Some configuration options can be overridden by passing CLI options.

#### CLI Options

  - `-c`, `--config`: Path to a configuration file to use instead of `config.json`.
  - `--mock-push`: Don't send push notifications, but show messages in terminal.
  - `--no-push`: Don't send push notifications or show messages in terminal.
  - `--no-write`: Don't record videos.
  - `--no-video`: Don't show the video.
  - `--show-video`: Do show the video.
  - `--no-detect`: Don't perform inference. This will disable everything except for `video`.
  - `--no-monitor`: Don't send push notifications or record events. Detections will still be drawn to video.
  - `--threaded`: Perform detections in a separate thread. This will speed up video but result in stale detections drawn to frames.
  - `--setup-coral`: Let Carl walk you through the setup of the Google Coral. (Additional install required)
  - `--src`: Video Source. Number or stream url or `usePiCamera`.
  - `--width`: Video width.
  - `--model`: Model to use. Either `yolo`, `mobilenet`, or `coral`.


## Setup

### RaspberryPi

If you plan to run Carl on a Raspberry Pi, I would recommend using a Raspberry Pi 4 with at least 4GB of RAM. Before continuing with the regular installation, please follow the instructions for installing the additional build dependencies required for OpenCV. 

The instructions are in [README.RPi.md](README.RPi.md).

### Installation

Depending on your intentions, you can either [install via pipx](#pipx-install) or  do a traditional [git install](#git-install).

If you plan on using a Google Coral USB Accelerator, you will need to install python 3.5-3.8. See the [Python version notes](#python-version) below.

#### pipx install

If you want to use the app and won't be developing any new features, consider installing via [pipx](https://pipxproject.github.io). This has many benefits. For example, it will handle creating a virtual environment for you, and it will also allow you to invoke carl via his alias, `carl`.

- ***NOTE:*** If you will be using a Google Coral USB Accelerator, you must follow the [these instructions instead](#pipx-install-with-coral).

1. Ensure you have [`pipx` installed](https://pipxproject.github.io/pipx/installation/).
    - If you are on a mac with homebrew, you can `brew install pipx`
2. Install `carl` with `pipx` as follows:
    - You can install the `main` branch with:
      ```bash
      pipx install git+https://github.com/RobertMcReed/housecarl.git
      ```
    - Or you can specify a branch to install with:
      ```bash
      pipx install git+https://github.com/RobertMcReed/housecarl.git@branch_name
      ```
    - Or install a specific release with:
      ```bash
      pipx install https://github.com/RobertMcReed/housecarl/archive/some_release.zip
      ```

#### pipx install with coral

If you want to use the Google Coral USB accelerator to speed up detections, you must install Carl into a virtual environment with python version 3.5-3.8. If you don't you won't be able to install `pycoral` completely, which is required for performing inference on the USB accelerator.

If you already have `pipx` installed, check the version:

```bash
~/.local/pipx/shared/bin/python3 --version
```

If you are within version 3.5-3.8, you are ok, and you can continue with the [regular install instructions](#pipx-install).

If you aren't you have a few options.

1. Reinstall `pipx` [using one of the supported versions of python](https://pipxproject.github.io/pipx/installation/).
    - One way to do this is to: 
        - Install the appropriate version of python using `pyenv`
        - Set that version as your global python version with `pyenv global 3.X.Y`
        - Install pyenv with `python -m pip install --user pipx`
2. Install a supported version of python using `pyenv` or `homebrew` (or some other means) and provide its executable to pipx:
    - You can do this in two ways.
        - If you want to set the version for *all* `pipx` installs, you can set the environment variable `PIPX_DEFAULT_PYTHON` in your `.bashrc` (or `.zshrc`, etc) as the path to the executable
            - If you do this, you can proceed by following the [regular install instructions](#pipx-install).
        - If you want to set the python version just for the Carl install, proceed as follows
3. Install `carl` using `pipx` by providing the path to a python executable:
```bash
pipx install --python {PATH_TO_PYTHON_EXEC} git+https://github.com/RobertMcReed/housecarl.git
```

For example, if you used `pyenv`, you might try something like:

```bash
pipx install --python ~/.pyenv/versions/3.8.9/bin/python3.8 git+https://github.com/RobertMcReed/housecarl.git
```

Or if you have a different version of python installed with `homebrew`, maybe try something like:

```bash
pipx install --python /usr/local/Cellar/python@3.8/3.8.10/bin/python3 git+https://github.com/RobertMcReed/housecarl.git
```

Once Carl is installed, make sure you follow the additional setup requirements for the Coral, detailed in [README.Coral.md](/README.Coral.md).

#### Git Install

If you plan on changing any features, you'll likely want to follow a traditional git install.

If you want to use the Google Coral USB accelerator to speed up detections, you must install Carl into a virtual environment with python version 3.5-3.8. If you don't, you won't be able to install `pycoral` completely, which is required for performing inference on the USB accelerator.

For help installing a specific version of python, see [python version](#python-version).

To install the Carl via git:

1. Clone the repository with `git clone https://github.com/RobertMcReed/housecarl.git`
2. Create and activate a virtual environment using your favorite method.
    - I prefer to use [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv).
3. Install project requirements with `pip install -r requirements.txt`
    - This will take a while if you are building on a Raspberry Pi
4. You're now ready to start processing video feeds. Get familiar with [the CLI](#cli) and [configuration options](#configuration), or keep reading to see additional setup.
5. If you will be using a Google Coral USB Accelerator, see the additional setup required in [README.Coral.md](/README.Coral.md).

#### Python Version

If you plan on using a Google Coral USB Accelerator, you will need to install python 3.5-3.8. My preferred way to do this is to use [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv). But you could also use [homebrew](https://brew.sh/) (if on OSX) or by other means.

To install via `pyenv`, see [their documentation](https://github.com/pyenv/pyenv#installation).

Make sure to install any [build dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment) first.

When you have pyenv installed, I recommend installing a framework version of python. It will take a little longer to install, but provides a more complete installation. You can read more about this [here](https://github.com/pyenv/pyenv/wiki#how-to-build-cpython-with-framework-support-on-os-x).

If you are on a Mac, you can install python as follows:

```bash
env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.8.9
```

Otherwise run:

```bash
env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.8.9
```

Once a suitable version of python has been installed, continue with the regular install instructions following either the [pipx install](#pipx-install) or [git install](#git-install).

#### Enable Google Coral Edge TPU Accelerator

In order to use a Google Coral USB Accelerator, there are additional setup requirements.

To begin, make sure you have installed Carl into an environment with python version 3.5-3.8. To do this, you can either follow the setup instructions for [pipx install with coral](#pipx-install-with-coral), or [Python Version](#python-version) followed by [Git Install](#git-install).

Once Carl has been installed, follow the additional instructions in [README.Coral.md](/README.Coral.md). If you are brave, try running `carl --setup-coral` to have Carl assist you in this.

#### Enable Wyze RTSP

The original intention behind Carl was to use him as a monitor for a Wyze cam. His horizons have broadened since then, but this is still a nice option. In order to capture your Wyze cam stream, you must flash the RTSP firmware to the device and enable it in the Wyze App.

1. [Flash the appropriate RTSP firmware](https://support.wyzecam.com/hc/en-us/articles/360031490871-How-to-flash-firmware-manually) to your camera
    - You can [download the firmware directly from Wyze](https://support.wyzecam.com/hc/en-us/articles/360024852172).
2. Once the firmware is flashed to your device, [enable the RTSP stream via the Wyze mobile app](https://support.wyzecam.com/hc/en-us/articles/360026245231-Wyze-Cam-RTSP?flash_digest=630b29ed5ddba4551c15029f9d8006765ae1ad0c#).
3. Once enabled in the app, you can generate a URL for the stream. Use this URL as the value of `config.video.src` or pass via the CLI as `--src=<RTSP_URL>`.
     - The stream url should look like `rtsp://{user}:{pw}@{stream_ip}/live`.
     - Note that `user` and `pw` are defined when enabling the stream, and are not your Wyze credentials.

### Uninstall

#### Uninstalling Google Coral

If you installed Google Coral support, you can uninstall dependencies by running `sudo bash edgetpu_runtime/uninstall.sh` from the root of the project.

#### Uninstalling Carl

Uninstalling Carl is pretty easy. 

If you installed Carl with `pipx`, simply run `pipx uninstall housecarl`.

If you installed Carl via `git`, simply remove the folder you downloaded, and delete the virtual environment that you installed it into.

### Enable Background Processing

 - TODO

### Local event playback in browser

 - TODO



## Resources

### Wyze

 - [Wyze Firmwares](https://support.wyzecam.com/hc/en-us/articles/360024852172)

 - [Flashing Wyze Firmware](https://support.wyzecam.com/hc/en-us/articles/360031490871-How-to-flash-firmware-manually)

 - [Wyze Cam RTSP](https://support.wyzecam.com/hc/en-us/articles/360026245231-Wyze-Cam-RTSP?flash_digest=630b29ed5ddba4551c15029f9d8006765ae1ad0c#)

 - [Wyze RTSP Forum](https://forums.wyzecam.com/t/real-time-streaming-protocol-rtsp/6694/986)

### PyImageSearch

 - [PyImageSearch Live Video Streaming](https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/)

 - [PyImageSearch Key Events Recorder](https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/)

### Models

 - [Darknet/Yolo](https://github.com/pjreddie/darknet)

 - [Pre-trained Yolo Models](https://github.com/AlexeyAB/darknet#pre-trained-models)

### Others

- [Pushover](https://pushover.net/)

- [pyenv](https://github.com/pyenv/pyenv)

- [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

- [homebrew](https://brew.sh/)

- [pipx](https://pypa.github.io/pipx/)

- [pycoral](https://www.coral.ai/software/#pycoral-api)

- [coral usb accelerator](https://coral.ai/docs/accelerator/get-started/)

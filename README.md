
# Live Video Transcription and Translation Tool

This tool allows you to perform real-time live video transcription and translation using Python. It consists of three main steps: downloading the live stream, transcribing and translating the video, and playing the video with updated captions.

## Workflow Overview:

1. **Downloading the Live Stream:** 
   - Utilizes `streamlink` to download the live stream and append it into a continuously growing video file (`video.mp4`).
   
2. **Transcribing and Translating the Video:**
   - Loads the video and transcribes each new 30-second segment, then translates it.
   - Saves the transcription and translation into a `captions.srt` file.

3. **Playing the Video with Updated Captions:**
   - Utilizes `mpc-be` (Media Player Classic - Black Edition) to play the video.
   - A Python script detects the player window and presses `Ctrl + Shift + Alt + R` to reload the captions for up-to-date translation.

## Setup Instructions

### Part 1: Downloading the Live Stream

To download the live stream, we use `streamlink`, a command-line utility for fetching streams from various websites. Follow these steps to set it up:

1. **Install Streamlink:**
   - You can quickly install `streamlink` using pip. Open a command prompt (cmd) or terminal and run the following command:
     ```
     pip install streamlink
     ```
   - Alternatively, you can download and install `streamlink` from the official website: [Streamlink GitHub](https://github.com/streamlink/streamlink). Follow the installation instructions provided for your operating system.

2. **Using Streamlink:**
   - After installation, open a command prompt (cmd) or terminal.
   - Run `streamlink <URL>` to download the live stream from a supported website.
   - Replace `<URL>` with the URL of the live stream you want to download.
   - For example, to download the stream at the best quality and save it as `video.mp4`, you can use the following command:
     ```bash
     streamlink <URL> best -o video.mp4
     ```
   - This command fetches the best available quality stream and continuously adds new parts of the stream to a single video file (`video.mp4`). So, as the live stream progresses, the video file keeps growing with the newly downloaded content..

   - **Note:** Ensure that the `<URL>` is replaced with the actual URL of the live stream you want to download, such as `https://www.twitch.tv/example_stream`.


### Part 2: Running the Tool

You have two options for running the tool: using a Python environment or using provided windows executables.

#### Using Python Environment:

1. **Set Up Python Environment:**
   - Run the following commands in your terminal to set up a Python virtual environment:
     ```
     python -m venv local
     .\local\Scripts\pip.exe install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu118
     .\local\Scripts\pip.exe install deep-translator==1.11.4 faster-whisper==0.10.0 ffmpeg-python==0.2.0 pysrt==1.1.2 pywinauto==0.6.8
     ```

2. **Run the Tool:**
   - Use Python from the local environment to run this script to start transcription and translation:
     ```
     .\local\Scripts\python.exe transcriber.py
     ```

   - and this script to start the video player:
     ```
     .\local\Scripts\python.exe player.py
     ```
   - **Note:** Make sure to config `transcriber.ini` and  `player.ini` before running.

#### Using Provided Executables:

1. **Download Executables:**
   - Download the appropriate executable for your system (CPU-only or GPU-supported) from the repository.

2. **Run the Executable:**
   - Simply execute the downloaded executable to run the tool.
   - The executables include the necessary dependencies and scripts for running the transcription and translation process.

### Part 3: Setting up MPC-BE Player

To play the video with updated captions, we use MPC-BE (Media Player Classic - Black Edition). Follow these steps to set it up:

1. **Install MPC-BE:**
   - Download and install MPC-BE from the official website: [MPC-BE](https://sourceforge.net/projects/mpcbe/).

2. **Set the Reload Captions Shortcut:**
   - Open MPC-BE.
   - Go to Options > Player > Keys.
   - Search for "reload" and assign a shortcut key combination (e.g., `Ctrl + Shift + Alt + R`) for "Reload Subtitles".

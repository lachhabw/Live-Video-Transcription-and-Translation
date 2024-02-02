import subprocess, os
import time
from pywinauto import Application
from configparser import ConfigParser

def run_video(player_executable_name, video_path, subtitles_path):
    # Run the command to start the application
    command = [player_executable_name, video_path, "/sub", subtitles_path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("--- Starting the video process ---")
    return process

def main():
    # Get the time of the captions
    last_modified_time = os.path.getmtime(CAPTION_FILE)
    # Run the video player
    process = run_video(PLAYER_EXECUTABLE_NAME, INPUT_VIDEO, CAPTION_FILE)
    # Connect to the app and get the window
    app = Application().connect(path=PLAYER_EXECUTABLE_NAME)
    window = app.top_window()

    while True:
        # Check if the video player process has terminated
        if process.poll() is not None:
            print("--- Video player process has terminated ---")
            break

        # Check if subtitles file has been changed
        current_modified_time = os.path.getmtime(CAPTION_FILE)
        if current_modified_time != last_modified_time:
            print("--- Reloading ---")
            last_modified_time = current_modified_time
            window.send_keystrokes('^%+R')
        # Sleep a while
        time.sleep(1)


if __name__ == "__main__":
    # Load config from file
    config = ConfigParser()
    config.read('player.ini')
    # Settings
    PLAYER_EXECUTABLE_NAME = config.get('Player', 'PLAYER_EXECUTABLE_NAME')
    INPUT_VIDEO = config.get('Video', 'INPUT_VIDEO')
    CAPTION_FILE = config.get('Video', 'CAPTION_FILE')
    # Play the video
    main()
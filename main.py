import os
import sys
import giphy_client
from giphy_client.rest import ApiException
from moviepy.editor import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.video.fx.all import resize
import requests
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog

# Load environment variables from .env file
load_dotenv()

# Your Giphy API key
GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')

# Function to search and download a GIF
def get_gif(api_instance, search_query):
    try:
        # Configure API key authorization: api_key
        configuration = giphy_client.Configuration()
        configuration.api_key['api_key'] = GIPHY_API_KEY

        # Search for GIF
        response = api_instance.gifs_search_get(GIPHY_API_KEY, search_query, limit=1, rating='g')

        # Extract GIF URL
        gif_url = response.data[0].images.downsized_large.url

        # Ensure 'video' directory exists
        if not os.path.exists("video"):
            os.makedirs("video")

        # Determine the filename for the GIF
        gif_filename = os.path.join("video", search_query + ".gif")

        # Download GIF using requests
        with open(gif_filename, 'wb') as f:
            f.write(requests.get(gif_url).content)

        return gif_filename

    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

# Function to create video with looping GIF and provided MP3
def create_video(gif_file, mp3_file):
    gif_clip = VideoFileClip(gif_file)
    audio_clip = AudioFileClip(mp3_file)
    audio_duration = audio_clip.duration

    num_loops = int(audio_duration / gif_clip.duration) + 1
    gif_clips = [gif_clip] * num_loops
    concatenated_gif = concatenate_videoclips(gif_clips)
    concatenated_gif = concatenated_gif.set_duration(audio_duration)

    final_clip = concatenated_gif.set_audio(audio_clip)
    final_clip = final_clip.fx(resize, width=1920, height=1080)

    # Get the directory of the MP3 file
    mp3_dir = os.path.dirname(mp3_file)

    # Construct the output path in the same directory as the MP3 file
    output_filename = os.path.splitext(os.path.basename(mp3_file))[0] + ".mp4"
    output_path = os.path.join(mp3_dir, output_filename)

    final_clip.write_videofile(output_path, fps=24, codec="libx264", preset="medium", bitrate="5000k", threads=8)

    final_clip.close()
    gif_clip.close()
    os.remove(gif_file)

def create_gui():
    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        mp3_entry.delete(0, tk.END)
        mp3_entry.insert(0, file_path)

    def create_video_callback():
        search_query = query_entry.get()
        mp3_file = mp3_entry.get()

        if not search_query or not mp3_file:
            error_label.config(text="Please enter a search query and select an MP3 file.")
            return

        api_instance = giphy_client.DefaultApi()
        gif_file = get_gif(api_instance, search_query)
        create_video(gif_file, mp3_file)
        success_label.config(text="Video created successfully!")

    root = tk.Tk()
    root.title("Create Video from GIF and MP3")

    query_label = tk.Label(root, text="GIF Search Query:")
    query_label.pack()
    query_entry = tk.Entry(root)
    query_entry.pack()

    mp3_label = tk.Label(root, text="MP3 File:")
    mp3_label.pack()
    mp3_entry = tk.Entry(root)
    mp3_entry.pack()
    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.pack()

    create_button = tk.Button(root, text="Create Video", command=create_video_callback)
    create_button.pack()

    error_label = tk.Label(root, text="", fg="red")
    error_label.pack()

    success_label = tk.Label(root, text="", fg="green")
    success_label.pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
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
from PIL import Image, ImageTk
import io

load_dotenv()

GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')

def get_gif(api_instance, search_query):
    try:
        configuration = giphy_client.Configuration()
        configuration.api_key['api_key'] = GIPHY_API_KEY

        response = api_instance.gifs_search_get(GIPHY_API_KEY, search_query, limit=8, rating='g')

        return response.data

    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

def create_video(gif_url, mp3_file):
    if not os.path.exists("video"):
        os.makedirs("video")

    gif_filename = os.path.join("video", "selected_gif.gif")

    with open(gif_filename, 'wb') as f:
        f.write(requests.get(gif_url).content)

    gif_clip = VideoFileClip(gif_filename)
    audio_clip = AudioFileClip(mp3_file)
    audio_duration = audio_clip.duration

    num_loops = int(audio_duration / gif_clip.duration) + 1
    gif_clips = [gif_clip] * num_loops
    concatenated_gif = concatenate_videoclips(gif_clips)
    concatenated_gif = concatenated_gif.set_duration(audio_duration)

    final_clip = concatenated_gif.set_audio(audio_clip)
    final_clip = final_clip.fx(resize, width=1920, height=1080)

    mp3_dir = os.path.dirname(mp3_file)

    output_filename = os.path.splitext(os.path.basename(mp3_file))[0] + ".mp4"
    output_path = os.path.join(mp3_dir, output_filename)

    final_clip.write_videofile(output_path, fps=24, codec="libx264", preset="medium", bitrate="5000k", threads=8)

    final_clip.close()
    gif_clip.close()
    os.remove(gif_filename)

def create_gif_selection_window(gifs):
    gif_window = tk.Toplevel()
    gif_window.title("Select a GIF")

    selected_gif = [None]

    def on_gif_click(index):
        selected_gif[0] = gifs[index].images.downsized_large.url
        gif_window.destroy()

    for i, gif in enumerate(gifs):
        gif_url = gif.images.downsized_medium.url
        response = requests.get(gif_url)
        img_data = response.content
        img = Image.open(io.BytesIO(img_data))
        photo = ImageTk.PhotoImage(img)

        gif_label = tk.Label(gif_window, image=photo)
        gif_label.image = photo
        gif_label.grid(row=i // 4, column=i % 4, padx=5, pady=5)
        gif_label.bind("<Button-1>", lambda event, index=i: on_gif_click(index))

    gif_window.wait_window()
    return selected_gif[0]

def create_gui():
    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        mp3_entry.delete(0, tk.END)
        mp3_entry.insert(0, file_path)

    def search_gifs():
        search_query = query_entry.get()

        if not search_query:
            error_label.config(text="Please enter a search query.")
            return

        api_instance = giphy_client.DefaultApi()
        gifs = get_gif(api_instance, search_query)

        if not gifs:
            error_label.config(text="No GIFs found for the search query.")
            return

        selected_gif_url = create_gif_selection_window(gifs)

        if selected_gif_url:
            mp3_file = mp3_entry.get()
            if mp3_file:
                create_video(selected_gif_url, mp3_file)
                success_label.config(text="Video created successfully!")
            else:
                error_label.config(text="Please select an MP3 file.")
        else:
            error_label.config(text="No GIF selected.")

    root = tk.Tk()
    root.title("Create Video from GIF and MP3")

    query_label = tk.Label(root, text="GIF Search Query:")
    query_label.pack()
    query_entry = tk.Entry(root)
    query_entry.pack()

    search_button = tk.Button(root, text="Search GIFs", command=search_gifs)
    search_button.pack()

    mp3_label = tk.Label(root, text="MP3 File:")
    mp3_label.pack()
    mp3_entry = tk.Entry(root)
    mp3_entry.pack()
    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.pack()

    error_label = tk.Label(root, text="", fg="red")
    error_label.pack()

    success_label = tk.Label(root, text="", fg="green")
    success_label.pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
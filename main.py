import os
import sys
import giphy_client
from giphy_client.rest import ApiException
from moviepy.editor import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import concatenate_videoclips
import requests

# Your Giphy API key
GIPHY_API_KEY = 'R3GfEVtxXSo3iyAYxQpAClDS1lusUxOQ'

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

        # Download GIF using requests
        with open("video/temp.gif", 'wb') as f:
            f.write(requests.get(gif_url).content)

        return "video/temp.gif"

    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

# Function to create video with looping GIF and provided MP3
def create_video(gif_file, mp3_file):
    gif_clip = VideoFileClip(gif_file)
    audio_clip = AudioFileClip(mp3_file)
    audio_duration = audio_clip.duration
    
    # Calculate the number of times to loop the GIF to match the audio duration
    num_loops = int(audio_duration / gif_clip.duration) + 1
    gif_clips = [gif_clip] * num_loops
    
    # Concatenate the GIF clips
    concatenated_gif = concatenate_videoclips(gif_clips)
    
    # Trim the concatenated GIF to match the audio duration
    concatenated_gif = concatenated_gif.set_duration(audio_duration)
    
    # Combine GIF and audio
    final_clip = concatenated_gif.set_audio(audio_clip)

    # Write to file
    output_path = "video/output.mp4"
    final_clip.write_videofile(output_path, fps=24)

    # Clean up temporary files
    os.remove(gif_file)

# Main function
def main():
    if len(sys.argv) != 2:
        print("Usage: python autogif.py <mp3_file>")
        return

    mp3_file = sys.argv[1]
    search_query = os.path.splitext(os.path.basename(mp3_file))[0]

    # Initialize Giphy client
    api_instance = giphy_client.DefaultApi()

    gif_file = get_gif(api_instance, search_query)
    create_video(gif_file, mp3_file)

if __name__ == "__main__":
    main()
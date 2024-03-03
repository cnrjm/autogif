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
    
    # Calculate the number of times to loop the GIF to match the audio duration
    num_loops = int(audio_duration / gif_clip.duration) + 1
    gif_clips = [gif_clip] * num_loops
    
    # Concatenate the GIF clips
    concatenated_gif = concatenate_videoclips(gif_clips)
    
    # Trim the concatenated GIF to match the audio duration
    concatenated_gif = concatenated_gif.set_duration(audio_duration)
    
    # Combine GIF and audio
    final_clip = concatenated_gif.set_audio(audio_clip)
    
    # Resize the final clip to 1080p resolution
    final_clip = final_clip.fx(resize, width=1920, height=1080)

    # Write to file with specified resolution
    output_path = os.path.join("video", "output.mp4")
    final_clip.write_videofile(output_path, fps=24, codec="libx264", preset="medium", bitrate="5000k", threads=8)

    # Clean up temporary files
    os.remove(gif_file)

# Main function
def main():
    if len(sys.argv) != 3:
        print("Usage: python autogif.py <search_query> <mp3_file>")
        return

    search_query = sys.argv[1]
    mp3_file = sys.argv[2]

    # Initialize Giphy client
    api_instance = giphy_client.DefaultApi()

    gif_file = get_gif(api_instance, search_query)
    create_video(gif_file, mp3_file)

if __name__ == "__main__":
    main()

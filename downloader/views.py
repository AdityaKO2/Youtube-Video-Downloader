from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
import yt_dlp
import os
import tempfile
import threading

# Function to handle the video download and streaming
def download_video(request, video_id):
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        youtube_cookies =  os.environ.get('YOUTUBE_COOKIES')

        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'quiet': True,
            'cookies': youtube_cookies,
            'outtmpl': '-',  # Direct output to standard output (memory)
        }

        # Use yt-dlp to download and stream video in memory
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info and download it
            info_dict = ydl.extract_info(video_url, download=True)

            # Create a temporary file in memory to hold the video content
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                temp_file.write(ydl.download([video_url]))

            # Define a file iterator for streaming the video
            def file_iterator(file_name, chunk_size=8192):
                with open(file_name, 'rb') as f:
                    while chunk := f.read(chunk_size):
                        yield chunk

            response = StreamingHttpResponse(
                file_iterator(temp_file.name),
                content_type='video/mp4'
            )
            response['Content-Disposition'] = f'attachment; filename="{info_dict["title"]}.mp4"'
            response['Content-Length'] = str(os.path.getsize(temp_file.name))

            # Function to clean up the temporary file after streaming
            def cleanup():
                os.remove(temp_file.name)

            # Run cleanup in a background thread
            threading.Thread(target=cleanup).start()

            return response

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=400)

def home(request):
    return render(request, 'download_X/index.html')

# from django.shortcuts import render
# from pytube import YouTube
# from django.http import HttpResponse, FileResponse, StreamingHttpResponse
# import os
# from tempfile import NamedTemporaryFile

# def home(request):
#     return render(request, 'download_X/index.html')

# import yt_dlp
# import os
# import time
# from tempfile import NamedTemporaryFile


# import os

# youtube_cookies = os.environ.get('YOUTUBE_COOKIES')



# def download_video(request, video_id):
#     try:

#         video_url = f"https://www.youtube.com/watch?v={video_id}"

#         ydl_opts = {
#             'format': 'best',  # Download the best available quality
#             'outtmpl': 'media/%(id)s.%(ext)s',  # Save to the 'downloads' folder with video ID as filename
#             'noplaylist': True,  # Don't download playlists, only a single video
#             'quiet': True,  # Disable unnecessary logs
#             'cookies': youtube_cookies,  # Use the value here

#         }

#         # Use yt-dlp to download the video
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             # Download the video
#             info_dict = ydl.extract_info(video_url, download=True)
#             filename = ydl.prepare_filename(info_dict)

#             # Check if the downloaded file exists
#             if not os.path.exists(filename):
#                 return HttpResponse("Error: Video could not be downloaded.", status=400)

#             # Stream the video file back to the user (avoid file being locked)
#             def file_iterator(file_name, chunk_size=8192):
#                 with open(file_name, 'rb') as f:
#                     while chunk := f.read(chunk_size):
#                         yield chunk

#             response = StreamingHttpResponse(file_iterator(filename), content_type='video/mp4')
#             response['Content-Disposition'] = f'attachment; filename="{info_dict["title"]}.mp4"'
#             response['Content-Length'] = str(os.path.getsize(filename))

#             # Clean up the file after the response is done
#             def cleanup():
#                 time.sleep(1)  # Give a little time before removing the file
#                 if os.path.exists(filename):
#                     os.remove(filename)

#             # Run cleanup in the background after sending the response
#             import threading
#             threading.Thread(target=cleanup).start()

#             return response

#     except Exception as e:
#         # Handle any error (e.g., invalid video ID, yt-dlp error)
#         return HttpResponse(f"An error occurred: {str(e)}", status=400)

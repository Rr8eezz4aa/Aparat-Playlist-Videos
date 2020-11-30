from bs4 import BeautifulSoup
from hurry.filesize import size
import datetime
import json
import re
import requests
import sys
import urllib

def get_video_download_links(video_code):
    page = requests.get(VIDEO_BASE_URL.format(video_code)).content
    soup = BeautifulSoup(page, 'lxml')

    download_links = []

    for i in soup.select(".download-dropdown .dropdown-content .menu-list li a"):
        video_download_url = i['href']
        video_quality = re.match(VIDEO_QUALITY_PATTERN, video_download_url)[1]
        video = urllib.request.urlopen(video_download_url)
        video_size_in_bytes = int(video.info()['Content-Length'])
        video_size = size(video_size_in_bytes)
        
        print('->', video_quality)

        download_links.append({
            'url': video_download_url,
            'quality': video_quality,
            'size_in_bytes': video_size_in_bytes,
            'size': video_size
        })
    
    return download_links

try:
    PLAYLIST = sys.argv[1]
except:
    PLAYLIST = input(">>> PLAYLIST: ")

BASE_URL = "https://www.aparat.com/playlist/{}"
VIDEO_BASE_URL = "https://www.aparat.com/v/{}"
VIDEO_QUALITY_PATTERN = r".*[-](.*p)\.mp4.*"

page = requests.get(BASE_URL.format(PLAYLIST)).content

soup = BeautifulSoup(page, 'lxml')

videos = []

for item in soup.select(".playlist-item"):
    video_code = item.select("div.thumbnail-video")[0]['data-uid']
    video_title = item.select(".playlist-item h2 .text")[0].string
    duration = str(datetime.timedelta(seconds=int(item.select("div.thumbnail-video")[0]['data-duration'])))

    print(video_code)

    download_links = get_video_download_links(video_code)

    videos.append({
        'code': video_code,
        'title': video_title,
        'duration': duration,
        'download': download_links
    })

with open(f'{PLAYLIST}_videos.json', 'w', encoding='utf-8') as f:
    json.dump(videos, f, ensure_ascii=False, indent=4)
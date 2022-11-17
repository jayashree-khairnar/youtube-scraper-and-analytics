from urllib.request import urlopen as urReq
from bs4 import BeautifulSoup as bs
import logging as console

console.basicConfig(filename="youtube_logs.log", level=console.INFO,\
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")


def get_video_ids(youtube, searchString):
    try:
        url = "https://www.youtube.com/c/" + searchString + "/videos"
        response_website = urReq(url)
        data_yt = response_website.read()
        beautified_html = bs(data_yt, 'html.parser')
        str(beautified_html.find_all('meta')[-5])
        text = str(beautified_html.find_all('meta')[-5])

        console.info('Fetching Channel ID')
        channel_id = text.split('"')[1]

    except Exception as e:
        console.error(f'Error occurred while fetching channel ID: {e}')


    try:
        console.info('Fetching Video IDs')
        req = youtube.channels().list(part='contentDetails', id=channel_id)
        res = req.execute()
        playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        request = youtube.playlistItems().list(part="snippet",
                                               playlistId=playlist_id,
                                               maxResults="50"
                                               )
        response = request.execute()
        """
        # To fetch all video ids uncomment this code

        nextPageToken = response.get('nextPageToken')

        while ('nextPageToken' in response):
            nextPage_request = youtube.playlistItems().list(part="snippet",
                                                            playlistId=playlistId,
                                                            maxResults="50",
                                                            pageToken=nextPageToken
                                                            )

            nextPage_response = nextPage_request.execute()
            response['items'] = response['items'] + nextPage_response['items']

            if 'nextPageToken' not in nextPage_response:
                response.pop('nextPageToken', None)
            else:
            nextPageToken = nextPage_response['nextPageToken']"""

        # To fetch first 50 video id's
        video_ids = []
        for i in range(len(response['items'])):
            video_ids.append(response['items'][i]['snippet']['resourceId']['videoId'])

        return channel_id, video_ids

    except Exception as e:
        console.error(f'Error while fetching video IDs: {e}')

import logging as console

console.basicConfig(filename="youtube_logs.log", level=console.INFO, \
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

def get_video_details(youtube, video_id, channel_id):
    try:
        console.info('Fetching video details')
        vid_details = []

        req = youtube.channels().list(part='snippet', id=channel_id)
        res = req.execute()
        channel_profile = res['items'][0]['snippet']['thumbnails']['default']['url']
        channel_name = res['items'][0]['snippet']['title']

        # for vid in video_ids:
        request = youtube.videos().list(part='snippet,statistics',
                                        id=','.join(video_id))
                                        # id=vid)
                                        # maxResults=50)
        response = request.execute()

        for i in range(len(response['items'])):
            data = dict(
                ChannelName=response['items'][i]['snippet']['channelTitle'],
                Title=response['items'][i]['snippet']['title'],
                Views=int(response['items'][i]['statistics']['viewCount']),
                Likes=int(response['items'][i]['statistics']['likeCount']),
                CommentsCount=int(response['items'][i]['statistics']['commentCount']),
                PublishedDate=response['items'][i]['snippet']['publishedAt'].split('T')[0],
                VideoLink='https://www.youtube.com/watch?v=' + response['items'][i]['id'],
                ThumbnailLink=response['items'][i]['snippet']['thumbnails']['high']['url'],
                VideoId=response['items'][i]['id']
            )
            vid_details.append(data)

        return channel_profile, channel_name, vid_details

    except Exception as e:
        console.error(f'Error while getting Video Details: {e}')
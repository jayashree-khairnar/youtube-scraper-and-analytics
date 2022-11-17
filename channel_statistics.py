import logging as console

console.basicConfig(filename="youtube_logs.log", level=console.INFO, \
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

def get_channel_stats(youtube, channel_id):
    try:
        console.info('Fetching channel statistics')
        channel_stats = []

        request = youtube.channels().list(part='snippet,contentDetails,statistics',
                                          id=channel_id)
                                          # maxResults=50)
        response = request.execute()

        for i in range(len(response['items'])):
            data = dict(Channel_Name=response['items'][i]['snippet']['title'],
                        Subscribers=int(response['items'][i]['statistics']['subscriberCount']),
                        View_Count=int(response['items'][i]['statistics']['viewCount']),
                        Total_Videos=int(response['items'][i]['statistics']['videoCount'])
                        )
            channel_stats.append(data)
        return channel_stats

    except Exception as e:
        console.error(f'Error while fetching Channel Statistics: {e}')
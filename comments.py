import logging as console

console.basicConfig(filename="youtube_logs.log", level=console.INFO, \
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

def get_top_level_comments(youtube, video_ids):
    try:
        console.info('Fetching Top Level Comments')
        list_of_all_videos_comments = []

        for vid in video_ids:
            comments_list = []
            request = youtube.commentThreads().list(
                part='id,replies,snippet',
                order='relevance',
                videoId=vid
            )
            response = request.execute()

            for i in range(len(response['items'])):
                data = dict(CommentId=response['items'][i]['snippet']['topLevelComment']['id'],
                            VideoLink='https://www.youtube.com/watch?v=' + response['items'][i]['id'],
                            CommentatorsName=response['items'][i]['snippet']['topLevelComment']['snippet'][
                                'authorDisplayName'],
                            CommentText=response['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal']
                            )

                comments_list.append(data)

            while response.get('nextPageToken', None):  # default is none
                request = youtube.commentThreads().list(
                    part='id,replies,snippet',
                    order='relevance',
                    videoId=vid,
                    pageToken=response['nextPageToken']
                )
                response = request.execute()
                # pprint(response)
                for i in range(len(response['items'])):
                    data = dict(CommentId=response['items'][i]['snippet']['topLevelComment']['id'],
                                VideoLink='https://www.youtube.com/watch?v=' + response['items'][i]['id'],
                                CommentatorsName=response['items'][i]['snippet']['topLevelComment']['snippet'][
                                    'authorDisplayName'],
                                CommentText=response['items'][i]['snippet']['topLevelComment']['snippet'][
                                    'textOriginal']
                                )

                    comments_list.append(data)

            list_of_all_videos_comments.extend(comments_list)
        return list_of_all_videos_comments

    except Exception as e:
        console.error(f'Error while loading Top Level Comments: {e}')


def get_nested_comments(youtube, video_id):
    try:
        console.info('Fetching Nested Comments')
        nested_comments = []

        for vid in video_id:
            comments_reply_list = []
            request = youtube.commentThreads().list(
                part='id,replies,snippet',
                order='relevance',
                videoId=vid
            )
            response = request.execute()

            for i in range(len(response['items'])):
                if 'replies' in response['items'][i].keys():
                    data = dict(
                        CommentParentId=int(response['items'][i]['replies']['comments'][0]['snippet']['parentId']),
                        CommentatorsName=response['items'][i]['replies']['comments'][0]['snippet'][
                            'authorDisplayName'],
                        CommentText=response['items'][i]['replies']['comments'][0]['snippet']['textOriginal']
                        )

                    comments_reply_list.append(data)

            while response.get('nextPageToken', None):  # default is none
                request = youtube.commentThreads().list(
                    part='id,replies,snippet',
                    order='relevance',
                    videoId=vid,
                    pageToken=response['nextPageToken']
                )
                response = request.execute()
                # pprint(response)
                for i in range(len(response['items'])):
                    if 'replies' in response['items'][i].keys():
                        data = dict(
                            CommentParentId=int(response['items'][i]['replies']['comments'][0]['snippet']['parentId']),
                            CommentatorsName=response['items'][i]['replies']['comments'][0]['snippet'][
                                'authorDisplayName'],
                            CommentText=response['items'][i]['replies']['comments'][0]['snippet']['textOriginal']
                        )

                        comments_reply_list.append(data)

            nested_comments.extend(comments_reply_list)
            # print(f'Finished fetching comments for {vid}, {len(comments_reply_list)} comments found.')

        return nested_comments

    except Exception as e:
        console.error(f'Error while loading Nested Comments: {e}')
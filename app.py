from comments import get_top_level_comments, get_nested_comments
from channel_statistics import get_channel_stats
from video_details import get_video_details
from video_id import get_video_ids

from flask import Flask, send_file, render_template, request
from flask_cors import cross_origin
from googleapiclient.discovery import build
from dotenv import load_dotenv
import logging as console
from pytube import YouTube
from io import BytesIO
import pandas as pd
import pymongo
import os


console.basicConfig(filename="youtube_logs.log", level=console.INFO, \
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")
load_dotenv()

app = Flask(__name__)

try:
    DEVELOPER_KEY = os.getenv('API_KEY')
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    VERSION = 'v3'
    youtube = build(YOUTUBE_API_SERVICE_NAME, VERSION, developerKey=DEVELOPER_KEY)
    console.info("API built successfully")
except Exception as e:
    console.error(f'Error occurred: {e}')

try:
    client = pymongo.MongoClient("mongodb+srv://jk:mongo123@jk-cluster.dqfdb.mongodb.net/?retryWrites=true&w=majority")
    client.server_info()
    db = client.youtube_scraper
    chan_stats = db['Channel_Statistics']
    vid_details = db['Video_Details']
    top_comments = db['Top_Level_Comments']
    nested_comments = db['Nested_Comments']

except pymongo.errors.ServerSelectionTimeoutError as e:
    console.error(f'Error while connecting to MongoDB: {e}')


@app.route('/', methods=['GET'])
@cross_origin()
def home_page():
    try:
        return render_template("index.html")
    except Exception as e:
        console.error(f'Error while rendering index: {e}')
        return render_template('not_found.html')


@app.route('/video_details', methods=['POST'])
@cross_origin()
def video_details():
    try:
        if request.method == 'POST':
            searchString = request.form['channel_name'].replace(' ', '')
            channel_id, video_ids = get_video_ids(youtube, searchString)

            channel_stats = get_channel_stats(youtube=youtube, channel_id=channel_id)

            channel_profile, channel_name, video_details.vid_detail = get_video_details(youtube=youtube, \
                                                                          video_id=video_ids, channel_id=channel_id)

            for i in video_details.vid_detail:
                vid_details.insert_one(i)
            return render_template('vdetails.html', vid_detail=video_details.vid_detail, profile=channel_profile,\
                                   ch_name=channel_name, subscribers=channel_stats[0]['Subscribers'])

    except Exception as e:
        console.error(f'Error while rendering Video Details: {e}')
        return render_template('not_found.html')


@app.route('/download/', defaults={'path':''})
@app.route('/download/<path:path>')
def download(path):
    try:
        buffer = BytesIO()
        video = YouTube('https://www.youtube.com/watch?v='+path)
        title = video.title
        highest_res = video.streams.get_highest_resolution()
        highest_res.stream_to_buffer(buffer)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=title+'.mp4')
    except Exception as e:
        console.error(f'Error while downloading file: {e}')
        return render_template("server_error.html")


@app.route('/comments/', defaults={'path':''})
@app.route('/comments/<path:path>')
def comments(path):
    try:
        top_level_comments = get_top_level_comments(youtube=youtube, video_ids=[path])
        for comment in top_level_comments:
            top_comments.insert_one(comment)

        return render_template('comments.html', comment=top_level_comments, \
                               vid_details=video_details.vid_detail, v_id=path)

    except Exception as e:
        console.error(f'Error while rendering to comments page: {e}')


@app.route('/dashboard')
def dashboard():
    try:
        videos = pd.DataFrame(video_details.vid_detail)
        return render_template('dashboard.html', labels=list(videos['Title']), value1=list(videos['Views']),\
                               value2=list(videos['Likes']), value3=list(videos['CommentsCount']), \
                               date=list(videos['PublishedDate']))
    except Exception as e:
        console.error(f'Exception while rendering to Dashboard: {e}')


if __name__ == '__main__':
    app.run(debug=True)

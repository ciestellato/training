import requests
import os
from dotenv import load_dotenv


# 事前に取得したアクセストークンをここに設定
load_dotenv()
token = os.getenv("SPOTIFY_TOKEN")

def fetch_web_api(endpoint, method='GET', body=None):
    url = f'https://api.spotify.com/{endpoint}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=body)
    else:
        raise ValueError("Unsupported HTTP method")

    return response.json()

def get_top_tracks():
    endpoint = 'v1/me/top/tracks?time_range=long_term&limit=5'
    data = fetch_web_api(endpoint)
    return data.get('items', [])

# 実行して表示
top_tracks = get_top_tracks()
for track in top_tracks:
    name = track['name']
    artists = ', '.join(artist['name'] for artist in track['artists'])
    print(f"{name} by {artists}")
import os
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Securely retrieve API key from environment variables (RECOMMENDED)
# RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
# if not RAPIDAPI_KEY:
#     raise ValueError("RAPIDAPI_KEY environment variable not set")

# DANGER: Exposing API key directly in code - VERY INSECURE (ONLY FOR TESTING/LOCAL)
RAPIDAPI_KEY = "9c744b1e04msh43b2dea878f2e0ep196409jsn715043e55446"  # Replace with your key - INSECURE - TESTING ONLY

RAPIDAPI_HOST = "all-media-downloader1.p.rapidapi.com"
RAPIDAPI_URL = "https://all-media-downloader1.p.rapidapi.com/all"

@app.route('/api/download', methods=['POST'])
def download_media():
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        payload = {"url": url}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(RAPIDAPI_URL, data=payload, headers=headers)
        response.raise_for_status()

        download_data = response.json()

        selected_download = None

        if quality and download_data and download_data.get("links"):
            for link in download_data["links"]:
                if link.get("quality") and quality.lower() in link["quality"].lower():
                    selected_download = link
                    break

        if not selected_download and download_data and download_data.get("links"):
            selected_download = download_data["links"][0]

        if selected_download:
            return jsonify({
                'download_link': selected_download.get("url"),
                'title': download_data.get("title") or "downloaded_file"
            }), 200
        else:
            return jsonify({'error': 'No download link found for the specified quality or any quality'}), 404

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
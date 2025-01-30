const express = require('express');
const fetch = require('node-fetch');
const app = express();
const port = process.env.PORT || 3000;

// *** SECURELY get the API key from environment variables ***
const rapidApiKey = process.env.RAPIDAPI_KEY; // Get from environment variables

if (!rapidApiKey) {
    console.error("RAPIDAPI_KEY environment variable is NOT set!");
    process.exit(1); // Exit the process if the key is missing
}

app.get('/download', async (req, res) => {
    const videoUrl = req.query.url;

    if (!videoUrl) {
        return res.status(400).send('Missing video URL parameter.');
    }

    try {
        const apiUrl = 'https://facebook-reel-and-video-downloader.p.rapidapi.com/app/main.php';
        const url = new URL(apiUrl);
        url.searchParams.set('url', videoUrl);

        const apiResponse = await fetch(url, {
            method: 'GET',
            headers: {
                'x-rapidapi-key': rapidApiKey, // Use the API key from env variables
                'x-rapidapi-host': 'facebook-reel-and-video-downloader.p.rapidapi.com'
            }
        });

        if (!apiResponse.ok) {
            const errorData = await apiResponse.text();
            console.error("API Error:", apiResponse.status, errorData);
            return res.status(apiResponse.status).send(`API request failed: ${errorData}`);
        }

        const data = await apiResponse.json();
        const downloadUrl = data.hd_video_url || data.sd_video_url || data.url;

        if (!downloadUrl) {
            console.error("No download URL found in API response:", data);
            return res.status(500).send('No download link found in the API response.');
        }

        const videoResponse = await fetch(downloadUrl, { redirect: 'follow' });

        if (!videoResponse.ok) {
            const errorData = await videoResponse.text();
            console.error("Video Fetch Error:", videoResponse.status, errorData);
            return res.status(videoResponse.status).send(`Failed to fetch video: ${errorData}`);
        }

        const contentType = videoResponse.headers.get('Content-Type');
        const contentLength = videoResponse.headers.get('Content-Length');
        const contentDisposition = videoResponse.headers.get('Content-Disposition');
        let filename = 'video.mp4';

        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1];
            }
        }

        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Type', contentType);
        if (contentLength) {
            res.setHeader('Content-Length', contentLength);
        }

        videoResponse.body.pipe(res);

    } catch (error) {
        console.error("Server Error:", error);
        res.status(500).send('An error occurred on the server.');
    }
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});

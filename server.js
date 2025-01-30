// server.js (Node.js/Express)
import express from 'express';
import fetch from 'node-fetch';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import path from 'path'; // Import the path module

const app = express();
const port = process.env.PORT || 3000;

// CORS Configuration (Important!)
const allowedOrigins = ['http://localhost:7700']; // Replace with your website's origin(s) for production

app.use(cors({
    origin: function (origin, callback) {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true)
        } else {
            callback(new Error('Not allowed by CORS'))
        }
    }
}));

const apiLimiter = rateLimit({
    windowMs: 1000, // 1 second window
    max: 1, // Limit each IP to 1 requests per second (adjust as needed)
    message: "Too many requests, please try again later."
});

app.use('/download', apiLimiter);

const rapidApiKey = process.env.RAPIDAPI_KEY;

if (!rapidApiKey) {
    console.error("RAPIDAPI_KEY environment variable is NOT set!");
    process.exit(1);
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
                'x-rapidapi-key': rapidApiKey,
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
        let filename = 'video.mp4'; // Default filename

        const contentDisposition = videoResponse.headers.get('Content-Disposition');
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1];
          }
        }

        console.log("Content-Type:", contentType);
        console.log("Content-Length:", contentLength);
        console.log("Filename:", filename);

        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Type', contentType);
        if (contentLength) {
            res.setHeader('Content-Length', contentLength);
        }

        videoResponse.body.pipe(res).on('error', (err) => {
            console.error("Streaming error:", err);
            res.status(500).send("Error streaming video.");
        });

    } catch (error) {
        console.error("Error in /download route:", error);
        res.status(500).send('An error occurred on the server.');
    }
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});

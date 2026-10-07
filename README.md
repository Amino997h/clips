# TikTok Automator (Clip + Telegram) 🚀

This project is an automated AI pipeline that transforms long-form YouTube videos into highly engaging, viral-ready short-form clips, and instantly uploads them to a Telegram channel with AI-generated titles, descriptions, and hashtags.

## Features ✨

*   **Fully Automated Pipeline:** Provide a YouTube URL (or local video path) and the number of clips you want. The tool handles the rest automatically.
*   **Smart Highlighting:** Uses AI to read the video's transcript and extract the most engaging, "viral-worthy" moments based on professional short-form editing criteria.
*   **Fast Video Cropping:** Employs an ultra-fast, single-pass FFmpeg strategy to perfectly cut and statically center-crop the video to vertical formats (like 4:5 or 9:16).
*   **Local AI Engine Support:** Integrates seamlessly with local OpenAI-compatible APIs (like the Playwright-based ChatGPT Engine) to bypass paid API costs.
*   **Telegram Auto-Upload:** Automatically uploads the finished clips sequentially to a designated Telegram channel as soon as they are processed.
*   **Dynamic Metadata Generation:** The AI doesn't just cut clips—it creates punchy titles, short descriptions, and relevant hashtags for each clip before pushing it to Telegram.

## Setup & Usage 🛠️

1.  **Dependencies:** Make sure you have `ffmpeg` installed on your system.
2.  **Environment:** Install Python requirements using `pip install -r requirements-local.txt`.
3.  **Local API Setup:** If using a local API, ensure your `.env` file contains your Local API Key and Base URL.
4.  **Run:** Execute `run_integrated.py` to start the pipeline!

```bash
python run_integrated.py "YOUR_YOUTUBE_URL_HERE" --num-clips 5 --aspect-ratio 4:5
```

Alternatively, use the provided `mix.bat` for a quick command-line interactive experience.

---
*Built for absolute automation and maximum speed.*

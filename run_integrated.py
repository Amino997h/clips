import os
import argparse
import threading
import queue
import requests

from shorts_generator.local.downloader import download_youtube_local
from shorts_generator.local.transcriber import transcribe_local
from shorts_generator.local.llm import call_local_llm
from shorts_generator.highlights import get_highlights
from shorts_generator.local.clipper import crop_clip_local

# --- TELEGRAM CONFIG ---
# Extracted from telegram-byos-storage
TELEGRAM_BOT_TOKEN = "8951711275:AAFpZH-GfdFxEMO-oCb4iJQz1eBASYGBdCQ"
TELEGRAM_CHANNEL_ID = "-1004247712091"

# --- UPLOAD WORKER ---
def upload_worker(upload_queue):
    print("[Uploader] Worker started.", flush=True)
    while True:
        item = upload_queue.get()
        if item is None:
            break  # Stop signal
            
        video_path = item['video_path']
        title = item.get('telegram_title', 'New Clip')
        desc = item.get('telegram_description', '')
        tags = item.get('telegram_hashtags', '')
        
        caption = f"{title}\n\n{desc}\n\n{tags}"
        print(f"[Uploader] Uploading {video_path} to Telegram...", flush=True)
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
            with open(video_path, 'rb') as f:
                files = {'video': f}
                data = {'chat_id': TELEGRAM_CHANNEL_ID, 'caption': caption}
                response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                print(f"[Uploader] Successfully uploaded {os.path.basename(video_path)}!", flush=True)
            else:
                print(f"[Uploader] Failed to upload {video_path}: {response.text}", flush=True)
        except Exception as e:
            print(f"[Uploader] Exception during upload: {e}", flush=True)
            
        upload_queue.task_done()

# --- MAIN PIPELINE ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="YouTube URL or local file path")
    parser.add_argument("--num-clips", type=int, default=3)
    parser.add_argument("--aspect-ratio", default="9:16")
    args = parser.parse_args()

    # 1. Download & Transcribe
    print("[Pipeline] Downloading video...")
    source_path = download_youtube_local(args.url, fmt="720")
    
    print("[Pipeline] Transcribing video...")
    transcript = transcribe_local(source_path)
    
    # 2. Get Highlights (with Telegram metadata)
    print("[Pipeline] Finding highlights...")
    highlights_result = get_highlights(transcript, num_clips=args.num_clips, llm_fn=call_local_llm)
    highlights = highlights_result.get("highlights", [])
    
    top = sorted(highlights, key=lambda h: int(h.get("score", 0)), reverse=True)[:args.num_clips]
    
    # 3. Setup Upload Queue & Worker Thread
    upload_queue = queue.Queue()
    uploader_thread = threading.Thread(target=upload_worker, args=(upload_queue,))
    uploader_thread.start()
    
    # 4. Crop sequentially, queue uploads immediately
    out_dir = "shorts_output"
    os.makedirs(out_dir, exist_ok=True)
    
    for i, h in enumerate(top, 1):
        out_path = os.path.join(out_dir, f"short_{i:02d}.mp4")
        print(f"[Pipeline] Cropping clip {i}/{len(top)}...")
        
        try:
            crop_clip_local(
                source_path,
                float(h["start_time"]),
                float(h["end_time"]),
                args.aspect_ratio,
                out_path,
            )
            
            # Queue for upload as soon as cropping is done
            upload_item = {
                'video_path': out_path,
                'telegram_title': h.get('telegram_title') or h.get('title'),
                'telegram_description': h.get('telegram_description') or h.get('virality_reason'),
                'telegram_hashtags': h.get('telegram_hashtags') or '#shorts #viral'
            }
            upload_queue.put(upload_item)
            
        except Exception as e:
            print(f"[Pipeline] Cropping failed for clip {i}: {e}")

    # Wait for all uploads to finish
    print("[Pipeline] All clips generated. Waiting for background uploads to finish...")
    upload_queue.put(None) # Send stop signal
    uploader_thread.join()
    print("[Pipeline] Done!")

if __name__ == "__main__":
    main()

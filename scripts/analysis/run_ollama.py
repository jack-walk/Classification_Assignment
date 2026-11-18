#!/usr/bin/env python
"""
Analyze YouTube video transcripts for dog/baby dog references.
Uses yt-dlp to fetch transcripts.
"""
import pandas as pd
from pathlib import Path
import subprocess

base_dir = Path(__file__).parent.parent.parent
csv_path = base_dir / 'data' / 'import' / 'clean' / 'all-briefings.csv'

print("📋 Loading baseline data...")
df = pd.read_csv(csv_path)
print(f"✅ Loaded {len(df)} videos from {csv_path}")

def get_transcript(video_id):
    """Fetch transcript for a YouTube video using yt-dlp"""
    try:
        cmd = [
            'yt-dlp',
            '--write-auto-subs',
            '--skip-download',
            '--sub-langs', 'en',
            '--output', '/tmp/%(id)s',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        subprocess.run(cmd, capture_output=True, timeout=60, check=False)
        
        # Look for subtitle file
        for ext in ['en.vtt', 'en.srt', 'en.json3.vtt']:
            sub_file = Path(f'/tmp/{video_id}.{ext}')
            if sub_file.exists():
                return sub_file.read_text()
        return None
    except Exception as e:
        return None

def search_transcript(transcript):
    """Check if transcript mentions dog or babydog"""
    if not transcript:
        return False
    
    text = transcript.lower()
    dog_keywords = ['dog', 'puppy', 'babydog', 'baby dog', 'pup']
    return any(kw in text for kw in dog_keywords)

print("🤖 Processing videos...\n")

results = []
for idx, row in df.iterrows():
    title = row.get('Title', '')
    url = row.get('URL', '')
    video_id = url[url.find('v=')+2:].split('&')[0] if 'v=' in url else ''
    
    print(f"[{idx+1:2d}/{len(df)}] {title[:50]:<50} ", end='', flush=True)
    
    transcript = get_transcript(video_id)
    contains_babydog = search_transcript(transcript)
    
    result_str = "🐕 Yes" if contains_babydog else "✗ No"
    print(result_str)
    
    results.append({
        'video_id': video_id,
        'title': title,
        'date': row.get('Date', ''),
        'youtube_link': url,
        'contains_babydog': 'True' if contains_babydog else 'False',
        'interesting': '',
        'reviewer': 'Ollama',
        'note': ''
    })

print(f"\n✅ Analysis complete!")

# Save to CSV
results_df = pd.DataFrame(results)
output_csv = base_dir / 'data' / 'export' / 'ai' / 'ollama.csv'
output_csv.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(output_csv, index=False)

print(f"💾 Saved {len(results_df)} results to {output_csv}")
print(f"\n📊 Summary:")
print(f"   Baby dog detected: {(results_df['contains_babydog'] == 'True').sum()}")
print(f"   No baby dog: {(results_df['contains_babydog'] == 'False').sum()}")

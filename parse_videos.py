#!/usr/bin/env python3
import json
import csv

def parse_channel_videos(json_file, output_csv, channel_name):
    videos = []
    with open(json_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                videos.append({
                    'id': data.get('id', ''),
                    'title': data.get('title', ''),
                    'view_count': data.get('view_count', 0),
                    'duration': data.get('duration', 0),
                    'duration_string': data.get('duration_string', ''),
                    'url': f"https://www.youtube.com/watch?v={data.get('id', '')}"
                })
            except json.JSONDecodeError:
                continue
    
    # 再生回数でソート（降順）
    videos.sort(key=lambda x: x['view_count'] if x['view_count'] else 0, reverse=True)
    
    # CSVに保存
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'view_count', 'duration', 'duration_string', 'url'])
        writer.writeheader()
        writer.writerows(videos)
    
    print(f"\n{channel_name}:")
    print(f"  総動画数: {len(videos)}")
    print(f"  1万再生以上: {len([v for v in videos if v['view_count'] and v['view_count'] >= 10000])}")
    print(f"  5000再生以上: {len([v for v in videos if v['view_count'] and v['view_count'] >= 5000])}")
    print(f"  3000再生以上: {len([v for v in videos if v['view_count'] and v['view_count'] >= 3000])}")
    
    print(f"\n  上位10本の動画:")
    for i, v in enumerate(videos[:10], 1):
        print(f"    {i}. {v['title'][:50]}... ({v['view_count']}回)")
    
    return videos

# チャンネル1
videos1 = parse_channel_videos(
    '/home/ubuntu/youtube_analysis/channel1_all_videos.json',
    '/home/ubuntu/youtube_analysis/channel1_videos.csv',
    'プレアデスの光〜アセンション・ガイド〜'
)

# チャンネル2
videos2 = parse_channel_videos(
    '/home/ubuntu/youtube_analysis/channel2_all_videos.json',
    '/home/ubuntu/youtube_analysis/channel2_videos.csv',
    'プレアデスの真理~アセンションゲート~'
)

# 分析対象の動画IDをまとめる
print("\n\n=== 分析対象の動画（上位10本ずつ） ===")
print("\nチャンネル1の上位10本:")
for v in videos1[:10]:
    print(f"  {v['id']}")

print("\nチャンネル2の上位10本:")
for v in videos2[:10]:
    print(f"  {v['id']}")

# 全動画IDをファイルに保存
with open('/home/ubuntu/youtube_analysis/target_video_ids.txt', 'w') as f:
    f.write("# チャンネル1: プレアデスの光〜アセンション・ガイド〜\n")
    for v in videos1[:10]:
        f.write(f"{v['id']}\n")
    f.write("\n# チャンネル2: プレアデスの真理~アセンションゲート~\n")
    for v in videos2[:10]:
        f.write(f"{v['id']}\n")

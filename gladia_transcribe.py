#!/usr/bin/env python3
import requests
import json
import time
import os

GLADIA_API_KEY = "667eb577-ace5-46fe-a59f-2acc433bee4f"
GLADIA_URL = "https://api.gladia.io/v2/pre-recorded"

# 分析対象の動画ID
channel1_videos = [
    "YUD11BYfl1A",
    "UVyau093Uuc",
    "b3ZO70sFXZo",
    "86C82J2a-wU",
    "Ou3pyeYFJgo",
    "RiXuo863nW8",
    "x56KMYVffqg",
    "W_t0QsVzdqE",
    "Fs4BMhOvT60",
    "ttBB9gpMx4c"
]

channel2_videos = [
    "KQqrAMhQu0c",
    "nGw9QTQn2Wc",
    "heX1hRYV_xg",
    "oCA9LspxgXo",
    "Dw3H_9mMmtg",
    "oEvUfhyGD9c",
    "XLo-7r-zV-c",
    "_1Cv77IhlwI",
    "e_Zcbo-cBiQ",
    "X7TmrrbTyHQ"
]

def submit_transcription_request(video_id):
    """Gladia APIに文字起こしリクエストを送信"""
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    headers = {
        "Content-Type": "application/json",
        "x-gladia-key": GLADIA_API_KEY
    }
    
    payload = {
        "audio_url": youtube_url,
        "custom_vocabulary": False,
        "translation": False,
        "custom_spelling": False,
        "language_config": {
            "languages": ["ja"],
            "code_switching": False
        },
        "diarization": False,
        "name_consistency": False,
        "punctuation_enhanced": False,
        "sentiment_analysis": True,
        "callback": False
    }
    
    try:
        response = requests.post(GLADIA_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return {
            "video_id": video_id,
            "status": "submitted",
            "result_url": result.get("result_url"),
            "id": result.get("id"),
            "response": result
        }
    except requests.exceptions.RequestException as e:
        return {
            "video_id": video_id,
            "status": "error",
            "error": str(e)
        }

def main():
    results = []
    
    # チャンネル1の動画を処理
    print("=== チャンネル1: プレアデスの光〜アセンション・ガイド〜 ===")
    for i, video_id in enumerate(channel1_videos, 1):
        print(f"  [{i}/10] 送信中: {video_id}")
        result = submit_transcription_request(video_id)
        result["channel"] = "channel1"
        results.append(result)
        print(f"    ステータス: {result['status']}")
        if result['status'] == 'submitted':
            print(f"    結果URL: {result.get('result_url', 'N/A')}")
        else:
            print(f"    エラー: {result.get('error', 'N/A')}")
        time.sleep(1)  # レート制限対策
    
    # チャンネル2の動画を処理
    print("\n=== チャンネル2: プレアデスの真理~アセンションゲート~ ===")
    for i, video_id in enumerate(channel2_videos, 1):
        print(f"  [{i}/10] 送信中: {video_id}")
        result = submit_transcription_request(video_id)
        result["channel"] = "channel2"
        results.append(result)
        print(f"    ステータス: {result['status']}")
        if result['status'] == 'submitted':
            print(f"    結果URL: {result.get('result_url', 'N/A')}")
        else:
            print(f"    エラー: {result.get('error', 'N/A')}")
        time.sleep(1)  # レート制限対策
    
    # 結果を保存
    with open('/home/ubuntu/youtube_analysis/transcription_requests.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完了 ===")
    print(f"成功: {len([r for r in results if r['status'] == 'submitted'])}")
    print(f"失敗: {len([r for r in results if r['status'] == 'error'])}")
    print(f"結果は transcription_requests.json に保存されました")

if __name__ == "__main__":
    main()

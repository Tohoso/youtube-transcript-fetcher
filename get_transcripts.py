#!/usr/bin/env python3
from youtube_transcript_api import YouTubeTranscriptApi
import json
import os

# 分析対象の動画ID
channel1_videos = [
    ("YUD11BYfl1A", "【選ばれた魂のみ表示】あなたが特別であることが証明されました。17秒以内に審査結果をお受け取りください。"),
    ("UVyau093Uuc", "【※強制通知】プレアデス最高評議会が強い失望を示しています。この動画公開をもってあなたへの加護を停止します"),
    ("b3ZO70sFXZo", "【※緊急通信】再生した瞬間、顔つきが変わります。プレアデスが強制起動させる若返りコードの波動"),
    ("86C82J2a-wU", "【選ばれた人へ】プレアデスの使者から遂に告げられます。若返りDNAがあなたに起動するまで残り1秒"),
    ("Ou3pyeYFJgo", "【※閲覧注意】今日を逃すと二度と届きません。あと24時間で閉じる魂の移行ゲート"),
    ("RiXuo863nW8", "5秒以内に見た人だけ、若返ります"),
    ("x56KMYVffqg", "選ばれし者よ、プレアデスの使者からの思いがけない贈り物がやって来る。永遠の若さ受け取ってください"),
    ("W_t0QsVzdqE", "※これ実話です。13秒以内に再生して下さい。あなたに直接約束されます"),
    ("Fs4BMhOvT60", "【※1回のみ表示】泣くほど嬉しい…宇宙が定めたツインレイ。今日だけ開かれる特別な扉"),
    ("ttBB9gpMx4c", "【※警告】この動画を明日までに見ないと貧困が確定します。")
]

channel2_videos = [
    ("KQqrAMhQu0c", "【※１度のみ表示】働かずに暮らせる時代がもうそこまで来ています。真相を受信してください。"),
    ("nGw9QTQn2Wc", "【※3万人に1人】あなたは合格です時間が無いので必ず今受信して下さい"),
    ("heX1hRYV_xg", "【※一度のみ表示】合格者の3％しか受信できません。7秒以内に受信して下さい"),
    ("oCA9LspxgXo", "【※一度のみ表示】地球人には再生できません。選ばれしあなたが受信してください。"),
    ("Dw3H_9mMmtg", "【※最後の魂へ】最終通知が届きました。このメッセージは必ず今受信してください。"),
    ("oEvUfhyGD9c", "※動画が削除されました。緊急につき後一回だけ投稿させて頂きます。"),
    ("XLo-7r-zV-c", "【※一度のみ表示】地球人には表示されません。必ず今受信してください。"),
    ("_1Cv77IhlwI", "【※本日限定】残念ながら再生できない人は残留です。まもなく日本が新次元に突入します。"),
    ("e_Zcbo-cBiQ", "【※一度のみ表示】３次元から去る魂へ最後のメッセージです。覚悟して受信してください。"),
    ("X7TmrrbTyHQ", "【※秘密事項】表示された方だけに誰よりも先にお伝えします。17秒以内に受信して下さい")
]

def get_transcript(video_id, title):
    """YouTube Transcript APIを使用して字幕を取得"""
    try:
        # 新しいAPI: YouTubeTranscriptApi().list(video_id)
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # 日本語字幕を探す
        transcript = None
        for t in transcript_list:
            if t.language_code == 'ja':
                transcript = api.fetch(t)
                break
        
        # 日本語がなければ自動生成字幕を取得
        if transcript is None:
            try:
                generated = transcript_list.find_generated_transcript(['ja'])
                transcript = api.fetch(generated)
            except:
                # それでもなければ最初の字幕を取得
                for t in transcript_list:
                    transcript = api.fetch(t)
                    break
        
        if transcript:
            # テキストを結合
            full_text = " ".join([entry.text for entry in transcript])
            return {
                "video_id": video_id,
                "title": title,
                "status": "success",
                "transcript": [{"text": entry.text, "start": entry.start, "duration": entry.duration} for entry in transcript],
                "full_text": full_text
            }
        else:
            return {
                "video_id": video_id,
                "title": title,
                "status": "no_transcript",
                "error": "字幕が見つかりませんでした"
            }
            
    except Exception as e:
        return {
            "video_id": video_id,
            "title": title,
            "status": "error",
            "error": str(e)
        }

def main():
    os.makedirs('/home/ubuntu/youtube_analysis/transcripts', exist_ok=True)
    
    all_results = []
    
    # チャンネル1の動画を処理
    print("=== チャンネル1: プレアデスの光〜アセンション・ガイド〜 ===")
    channel1_results = []
    for i, (video_id, title) in enumerate(channel1_videos, 1):
        print(f"  [{i}/10] 取得中: {video_id}")
        result = get_transcript(video_id, title)
        result["channel"] = "channel1"
        channel1_results.append(result)
        print(f"    ステータス: {result['status']}")
        if result['status'] == 'success':
            print(f"    文字数: {len(result['full_text'])}")
            # 個別ファイルに保存
            with open(f'/home/ubuntu/youtube_analysis/transcripts/ch1_{video_id}.txt', 'w', encoding='utf-8') as f:
                f.write(f"タイトル: {title}\n")
                f.write(f"動画ID: {video_id}\n")
                f.write(f"URL: https://www.youtube.com/watch?v={video_id}\n")
                f.write("="*50 + "\n\n")
                f.write(result['full_text'])
        else:
            print(f"    エラー: {result.get('error', 'N/A')}")
    
    all_results.extend(channel1_results)
    
    # チャンネル2の動画を処理
    print("\n=== チャンネル2: プレアデスの真理~アセンションゲート~ ===")
    channel2_results = []
    for i, (video_id, title) in enumerate(channel2_videos, 1):
        print(f"  [{i}/10] 取得中: {video_id}")
        result = get_transcript(video_id, title)
        result["channel"] = "channel2"
        channel2_results.append(result)
        print(f"    ステータス: {result['status']}")
        if result['status'] == 'success':
            print(f"    文字数: {len(result['full_text'])}")
            # 個別ファイルに保存
            with open(f'/home/ubuntu/youtube_analysis/transcripts/ch2_{video_id}.txt', 'w', encoding='utf-8') as f:
                f.write(f"タイトル: {title}\n")
                f.write(f"動画ID: {video_id}\n")
                f.write(f"URL: https://www.youtube.com/watch?v={video_id}\n")
                f.write("="*50 + "\n\n")
                f.write(result['full_text'])
        else:
            print(f"    エラー: {result.get('error', 'N/A')}")
    
    all_results.extend(channel2_results)
    
    # 結果をJSONに保存
    with open('/home/ubuntu/youtube_analysis/transcripts/all_transcripts.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # サマリー
    success_count = len([r for r in all_results if r['status'] == 'success'])
    print(f"\n=== 完了 ===")
    print(f"成功: {success_count}/20")
    print(f"失敗: {20 - success_count}/20")

if __name__ == "__main__":
    main()

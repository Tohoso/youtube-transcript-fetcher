#!/usr/bin/env python3
"""
YouTube Transcript Fetcher - 使用例

このスクリプトは、YouTube Transcript Fetcherの基本的な使用方法を示します。
"""

from youtube_transcript_fetcher import YouTubeTranscriptFetcher, VideoInfo


def example_fetch_from_channels():
    """
    例1: 複数チャンネルから文字起こしを取得
    """
    print("=" * 60)
    print("例1: 複数チャンネルから文字起こしを取得")
    print("=" * 60)
    
    # フェッチャーを初期化
    fetcher = YouTubeTranscriptFetcher(output_dir="./output/channels")
    
    # 対象チャンネルを設定
    channels = [
        # (チャンネルURL, 表示名)
        ("https://www.youtube.com/@YouTube", "YouTube公式"),
        # 他のチャンネルを追加...
    ]
    
    # 各チャンネルから上位5本の動画の文字起こしを取得
    results = fetcher.fetch_from_channels(
        channels=channels,
        videos_per_channel=5,
        languages=['ja', 'en'],  # 日本語優先、なければ英語
        delay=2.0  # 2秒間隔
    )
    
    # 結果を保存
    fetcher.save_all_results("channels_transcripts")
    
    # サマリーを表示
    fetcher.print_summary()


def example_fetch_specific_videos():
    """
    例2: 特定の動画IDから文字起こしを取得
    """
    print("=" * 60)
    print("例2: 特定の動画IDから文字起こしを取得")
    print("=" * 60)
    
    fetcher = YouTubeTranscriptFetcher(output_dir="./output/specific")
    
    # 取得したい動画を指定
    videos = [
        VideoInfo(
            video_id="dQw4w9WgXcQ",  # 例: Rick Astley - Never Gonna Give You Up
            title="Never Gonna Give You Up",
            channel_name="Rick Astley"
        ),
        # 他の動画を追加...
    ]
    
    # 文字起こしを取得
    results = fetcher.fetch_multiple_videos(
        videos=videos,
        languages=['en'],
        delay=1.5
    )
    
    # 結果を保存
    fetcher.save_all_results("specific_videos")
    
    # サマリーを表示
    fetcher.print_summary()


def example_single_video():
    """
    例3: 単一動画の文字起こしを取得
    """
    print("=" * 60)
    print("例3: 単一動画の文字起こしを取得")
    print("=" * 60)
    
    fetcher = YouTubeTranscriptFetcher(output_dir="./output/single")
    
    video = VideoInfo(
        video_id="YOUR_VIDEO_ID",
        title="動画タイトル",
        channel_name="チャンネル名"
    )
    
    result = fetcher.fetch_transcript(video, languages=['ja'])
    
    if result.status == "success":
        print(f"取得成功！")
        print(f"文字数: {len(result.full_text)}")
        print(f"最初の200文字: {result.full_text[:200]}...")
    else:
        print(f"取得失敗: {result.error_message}")


if __name__ == "__main__":
    # 実行したい例のコメントを外してください
    
    # example_fetch_from_channels()
    # example_fetch_specific_videos()
    # example_single_video()
    
    print("使用例を実行するには、上記の関数呼び出しのコメントを外してください。")
    print("詳細はREADME.mdを参照してください。")

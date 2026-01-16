#!/usr/bin/env python3
"""
YouTube Transcript Fetcher
複数のYouTubeチャンネルから動画の文字起こしを取得するスクリプト

使用方法:
    python youtube_transcript_fetcher.py

依存関係:
    pip install youtube-transcript-api yt-dlp

注意:
    - クラウド環境（AWS, GCP, Azureなど）ではYouTubeにIPがブロックされる可能性があります
    - その場合はプロキシを使用するか、ローカル環境で実行してください
"""

import json
import os
import time
import csv
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess

# YouTube Transcript API
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False
    print("Warning: youtube-transcript-api not installed. Run: pip install youtube-transcript-api")


@dataclass
class VideoInfo:
    """動画情報を格納するデータクラス"""
    video_id: str
    title: str
    channel_name: str
    view_count: int = 0
    duration: int = 0
    url: str = ""
    
    def __post_init__(self):
        if not self.url:
            self.url = f"https://www.youtube.com/watch?v={self.video_id}"


@dataclass
class TranscriptResult:
    """文字起こし結果を格納するデータクラス"""
    video_id: str
    title: str
    channel_name: str
    status: str  # success, error, no_transcript, disabled
    full_text: str = ""
    transcript_segments: List[Dict] = None
    error_message: str = ""
    fetched_at: str = ""
    
    def __post_init__(self):
        if self.transcript_segments is None:
            self.transcript_segments = []
        if not self.fetched_at:
            self.fetched_at = datetime.now().isoformat()


class YouTubeTranscriptFetcher:
    """YouTube動画の文字起こしを取得するクラス"""
    
    def __init__(self, output_dir: str = "./transcripts", proxy: str = None):
        """
        初期化
        
        Args:
            output_dir: 出力ディレクトリ
            proxy: プロキシURL（例: "http://proxy:8080"）
        """
        self.output_dir = output_dir
        self.proxy = proxy
        self.results: List[TranscriptResult] = []
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "individual"), exist_ok=True)
    
    def get_channel_videos(self, channel_url: str, max_videos: int = None) -> List[VideoInfo]:
        """
        チャンネルの動画一覧を取得
        
        Args:
            channel_url: チャンネルURL
            max_videos: 取得する最大動画数（Noneで全件）
        
        Returns:
            動画情報のリスト
        """
        videos = []
        
        try:
            # yt-dlpを使用してチャンネルの動画一覧を取得
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "-j",
                f"{channel_url}/videos"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    video = VideoInfo(
                        video_id=data.get('id', ''),
                        title=data.get('title', ''),
                        channel_name=data.get('channel', '') or data.get('playlist_uploader', ''),
                        view_count=data.get('view_count', 0) or 0,
                        duration=int(data.get('duration', 0) or 0)
                    )
                    videos.append(video)
                except json.JSONDecodeError:
                    continue
            
            # 再生回数でソート（降順）
            videos.sort(key=lambda x: x.view_count, reverse=True)
            
            # 最大数を制限
            if max_videos:
                videos = videos[:max_videos]
                
        except subprocess.TimeoutExpired:
            print(f"Error: Timeout while fetching channel videos from {channel_url}")
        except Exception as e:
            print(f"Error fetching channel videos: {e}")
        
        return videos
    
    def fetch_transcript(self, video: VideoInfo, languages: List[str] = ['ja']) -> TranscriptResult:
        """
        単一動画の文字起こしを取得
        
        Args:
            video: 動画情報
            languages: 取得する言語のリスト（優先順）
        
        Returns:
            文字起こし結果
        """
        if not TRANSCRIPT_API_AVAILABLE:
            return TranscriptResult(
                video_id=video.video_id,
                title=video.title,
                channel_name=video.channel_name,
                status="error",
                error_message="youtube-transcript-api not installed"
            )
        
        try:
            api = YouTubeTranscriptApi()
            
            # 字幕リストを取得
            transcript_list = api.list(video.video_id)
            
            # 指定言語の字幕を探す
            transcript = None
            for lang in languages:
                for t in transcript_list:
                    if t.language_code == lang:
                        transcript = api.fetch(t)
                        break
                if transcript:
                    break
            
            # 見つからなければ自動生成字幕を取得
            if transcript is None:
                try:
                    generated = transcript_list.find_generated_transcript(languages)
                    transcript = api.fetch(generated)
                except:
                    # 最初の字幕を取得
                    for t in transcript_list:
                        transcript = api.fetch(t)
                        break
            
            if transcript:
                # テキストを結合
                full_text = " ".join([entry.text for entry in transcript])
                segments = [
                    {"text": entry.text, "start": entry.start, "duration": entry.duration}
                    for entry in transcript
                ]
                
                return TranscriptResult(
                    video_id=video.video_id,
                    title=video.title,
                    channel_name=video.channel_name,
                    status="success",
                    full_text=full_text,
                    transcript_segments=segments
                )
            else:
                return TranscriptResult(
                    video_id=video.video_id,
                    title=video.title,
                    channel_name=video.channel_name,
                    status="no_transcript",
                    error_message="No transcript found"
                )
                
        except Exception as e:
            error_msg = str(e)
            status = "error"
            
            if "disabled" in error_msg.lower():
                status = "disabled"
            elif "not found" in error_msg.lower():
                status = "no_transcript"
            
            return TranscriptResult(
                video_id=video.video_id,
                title=video.title,
                channel_name=video.channel_name,
                status=status,
                error_message=error_msg[:500]  # エラーメッセージを短縮
            )
    
    def fetch_multiple_videos(
        self,
        videos: List[VideoInfo],
        languages: List[str] = ['ja'],
        delay: float = 1.0,
        save_individual: bool = True
    ) -> List[TranscriptResult]:
        """
        複数動画の文字起こしを取得
        
        Args:
            videos: 動画情報のリスト
            languages: 取得する言語のリスト
            delay: リクエスト間の遅延（秒）
            save_individual: 個別ファイルに保存するか
        
        Returns:
            文字起こし結果のリスト
        """
        results = []
        total = len(videos)
        
        for i, video in enumerate(videos, 1):
            print(f"  [{i}/{total}] Fetching: {video.video_id} - {video.title[:50]}...")
            
            result = self.fetch_transcript(video, languages)
            results.append(result)
            
            if result.status == "success":
                print(f"    ✓ Success ({len(result.full_text)} chars)")
                
                if save_individual:
                    self._save_individual_transcript(result)
            else:
                print(f"    ✗ {result.status}: {result.error_message[:100]}")
            
            # レート制限対策
            if i < total:
                time.sleep(delay)
        
        self.results.extend(results)
        return results
    
    def fetch_from_channels(
        self,
        channels: List[Tuple[str, str]],
        videos_per_channel: int = 10,
        languages: List[str] = ['ja'],
        delay: float = 1.0
    ) -> Dict[str, List[TranscriptResult]]:
        """
        複数チャンネルから文字起こしを取得
        
        Args:
            channels: (チャンネルURL, チャンネル名)のリスト
            videos_per_channel: チャンネルあたりの動画数
            languages: 取得する言語のリスト
            delay: リクエスト間の遅延（秒）
        
        Returns:
            チャンネル名をキーとした結果の辞書
        """
        all_results = {}
        
        for channel_url, channel_name in channels:
            print(f"\n{'='*60}")
            print(f"Channel: {channel_name}")
            print(f"URL: {channel_url}")
            print(f"{'='*60}")
            
            # 動画一覧を取得
            print("Fetching video list...")
            videos = self.get_channel_videos(channel_url, videos_per_channel)
            print(f"Found {len(videos)} videos")
            
            if not videos:
                print("No videos found, skipping...")
                all_results[channel_name] = []
                continue
            
            # 文字起こしを取得
            print("\nFetching transcripts...")
            results = self.fetch_multiple_videos(videos, languages, delay)
            all_results[channel_name] = results
            
            # チャンネルごとのサマリー
            success_count = len([r for r in results if r.status == "success"])
            print(f"\nChannel Summary: {success_count}/{len(results)} successful")
        
        return all_results
    
    def _save_individual_transcript(self, result: TranscriptResult):
        """個別の文字起こしファイルを保存"""
        filename = f"{result.channel_name}_{result.video_id}.txt"
        # ファイル名に使えない文字を置換
        filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
        filepath = os.path.join(self.output_dir, "individual", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"タイトル: {result.title}\n")
            f.write(f"動画ID: {result.video_id}\n")
            f.write(f"チャンネル: {result.channel_name}\n")
            f.write(f"URL: https://www.youtube.com/watch?v={result.video_id}\n")
            f.write(f"取得日時: {result.fetched_at}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result.full_text)
    
    def save_all_results(self, filename_prefix: str = "transcripts"):
        """全結果を保存"""
        # JSON形式で保存
        json_path = os.path.join(self.output_dir, f"{filename_prefix}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(r) for r in self.results],
                f,
                ensure_ascii=False,
                indent=2
            )
        print(f"Saved JSON: {json_path}")
        
        # CSV形式で保存（サマリー）
        csv_path = os.path.join(self.output_dir, f"{filename_prefix}_summary.csv")
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'video_id', 'title', 'channel_name', 'status',
                'text_length', 'error_message', 'fetched_at'
            ])
            for r in self.results:
                writer.writerow([
                    r.video_id, r.title, r.channel_name, r.status,
                    len(r.full_text), r.error_message[:100], r.fetched_at
                ])
        print(f"Saved CSV: {csv_path}")
        
        # 成功した文字起こしを1つのファイルにまとめる
        combined_path = os.path.join(self.output_dir, f"{filename_prefix}_combined.txt")
        with open(combined_path, 'w', encoding='utf-8') as f:
            for r in self.results:
                if r.status == "success":
                    f.write(f"\n{'#'*60}\n")
                    f.write(f"# タイトル: {r.title}\n")
                    f.write(f"# 動画ID: {r.video_id}\n")
                    f.write(f"# チャンネル: {r.channel_name}\n")
                    f.write(f"# URL: https://www.youtube.com/watch?v={r.video_id}\n")
                    f.write(f"{'#'*60}\n\n")
                    f.write(r.full_text)
                    f.write("\n\n")
        print(f"Saved Combined: {combined_path}")
    
    def print_summary(self):
        """結果のサマリーを表示"""
        total = len(self.results)
        success = len([r for r in self.results if r.status == "success"])
        errors = len([r for r in self.results if r.status == "error"])
        no_transcript = len([r for r in self.results if r.status == "no_transcript"])
        disabled = len([r for r in self.results if r.status == "disabled"])
        
        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"Total videos processed: {total}")
        print(f"  ✓ Success: {success}")
        print(f"  ✗ Error: {errors}")
        print(f"  - No transcript: {no_transcript}")
        print(f"  - Disabled: {disabled}")
        print(f"Success rate: {success/total*100:.1f}%" if total > 0 else "N/A")


def main():
    """メイン関数 - 使用例"""
    
    # 対象チャンネルの設定
    channels = [
        (
            "https://www.youtube.com/@プレアデスの光アセンションガイド",
            "プレアデスの光〜アセンション・ガイド〜"
        ),
        (
            "https://www.youtube.com/@プレアデスの真理アセンションゲート",
            "プレアデスの真理~アセンションゲート~"
        )
    ]
    
    # フェッチャーを初期化
    fetcher = YouTubeTranscriptFetcher(
        output_dir="/home/ubuntu/youtube_analysis/transcripts"
    )
    
    # 各チャンネルから上位10本の動画の文字起こしを取得
    results = fetcher.fetch_from_channels(
        channels=channels,
        videos_per_channel=10,
        languages=['ja'],
        delay=1.5  # レート制限対策
    )
    
    # 結果を保存
    fetcher.save_all_results("pleiades_transcripts")
    
    # サマリーを表示
    fetcher.print_summary()


if __name__ == "__main__":
    main()

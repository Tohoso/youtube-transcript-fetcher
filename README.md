# YouTube Transcript Fetcher

複数のYouTubeチャンネルから動画の文字起こしを一括取得するPythonスクリプトです。

## 機能

- 複数のYouTubeチャンネルから動画一覧を自動取得
- 再生回数順でソートし、上位N本の動画を選択
- YouTube Transcript APIを使用して字幕/文字起こしを取得
- 日本語字幕を優先的に取得（自動生成字幕にも対応）
- 結果をJSON、CSV、テキストファイルで出力
- レート制限対策の遅延機能付き

## 必要な依存関係

```bash
pip install youtube-transcript-api yt-dlp
```

## インストール

```bash
git clone https://github.com/YOUR_USERNAME/youtube-transcript-fetcher.git
cd youtube-transcript-fetcher
pip install -r requirements.txt
```

## 使用方法

### コマンドラインから実行

```bash
python youtube_transcript_fetcher.py
```

### Pythonスクリプトとして使用

```python
from youtube_transcript_fetcher import YouTubeTranscriptFetcher

# フェッチャーを初期化
fetcher = YouTubeTranscriptFetcher(output_dir="./transcripts")

# チャンネルを設定
channels = [
    ("https://www.youtube.com/@チャンネル名1", "チャンネル表示名1"),
    ("https://www.youtube.com/@チャンネル名2", "チャンネル表示名2"),
]

# 文字起こしを取得
results = fetcher.fetch_from_channels(
    channels=channels,
    videos_per_channel=10,  # 各チャンネルから取得する動画数
    languages=['ja'],       # 取得する言語
    delay=1.5               # リクエスト間の遅延（秒）
)

# 結果を保存
fetcher.save_all_results("output_prefix")

# サマリーを表示
fetcher.print_summary()
```

### 特定の動画IDから取得

```python
from youtube_transcript_fetcher import YouTubeTranscriptFetcher, VideoInfo

fetcher = YouTubeTranscriptFetcher(output_dir="./transcripts")

# 動画情報を手動で設定
videos = [
    VideoInfo(video_id="VIDEO_ID_1", title="動画タイトル1", channel_name="チャンネル名"),
    VideoInfo(video_id="VIDEO_ID_2", title="動画タイトル2", channel_name="チャンネル名"),
]

# 文字起こしを取得
results = fetcher.fetch_multiple_videos(videos, languages=['ja'])

# 結果を保存
fetcher.save_all_results("custom_videos")
```

## 出力ファイル

スクリプトは以下のファイルを生成します：

| ファイル | 説明 |
|---------|------|
| `{prefix}.json` | 全結果をJSON形式で保存（タイムスタンプ付き字幕セグメント含む） |
| `{prefix}_summary.csv` | サマリーをCSV形式で保存 |
| `{prefix}_combined.txt` | 成功した全文字起こしを1ファイルにまとめたもの |
| `individual/` | 各動画の文字起こしを個別ファイルで保存 |

## 設定オプション

### YouTubeTranscriptFetcher

| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|----------|------|
| `output_dir` | str | "./transcripts" | 出力ディレクトリ |
| `proxy` | str | None | プロキシURL（例: "http://proxy:8080"） |

### fetch_from_channels

| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|----------|------|
| `channels` | List[Tuple] | - | (チャンネルURL, チャンネル名)のリスト |
| `videos_per_channel` | int | 10 | チャンネルあたりの動画数 |
| `languages` | List[str] | ['ja'] | 取得する言語のリスト |
| `delay` | float | 1.0 | リクエスト間の遅延（秒） |

## 注意事項

### IPブロックについて

クラウド環境（AWS, GCP, Azure等）ではYouTubeにIPがブロックされる可能性があります。
その場合は以下の対策を検討してください：

1. **ローカル環境で実行する** - 最も確実な方法
2. **プロキシを使用する** - 住宅用プロキシが効果的
3. **遅延を増やす** - `delay`パラメータを大きくする（3-5秒推奨）

### レート制限

YouTubeには暗黙のレート制限があります。短時間に大量のリクエストを送ると
一時的にブロックされる可能性があります。`delay`パラメータで適切な遅延を設定してください。

### 字幕の可用性

すべてのYouTube動画に字幕があるわけではありません。以下の場合、字幕を取得できません：

- 動画に字幕が設定されていない
- 字幕が無効化されている
- 自動生成字幕が利用できない言語

## トラブルシューティング

### "YouTube is blocking requests from your IP"

クラウド環境のIPがブロックされています。ローカル環境で実行するか、プロキシを使用してください。

### "No transcript found"

動画に字幕が設定されていません。別の動画を試してください。

### "Transcripts disabled"

動画の所有者が字幕を無効化しています。

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更を加える場合は、まずissueを開いて議論してください。

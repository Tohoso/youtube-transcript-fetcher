#!/usr/bin/env python3
"""
台本品質検証スクリプト
生成された台本が元の台本のスタイルを再現できているか検証する
"""

import re
import json

# 検証項目
REQUIRED_PHRASES = [
    "偶然ではありません",
    "3万人に1人",
    "上位3%",
    "恐れることはありません",
    "一人ではありません",
    "プレアデス",
    "銀河連邦",
    "5次元",
    "3次元",
    "覚醒",
    "チャンネル登録",
    "コメント",
    "高評価",
]

SYMPTOM_KEYWORDS = [
    "ゾロ目",
    "夜中",
    "目覚め",
    "不安",
    "孤独",
    "違和感",
]

STRUCTURE_MARKERS = [
    "オープニング",
    "問題提起",
    "宇宙的背景",
    "歴史的根拠",
    "変化の説明",
    "行動指針",
    "エンディング",
]

ENDING_PHRASES = [
    "ノア",
    "愛と祝福",
    "また明日",
    "光",
]

def load_script(filepath):
    """台本を読み込む"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def check_phrases(script, phrases, category_name):
    """フレーズの存在を確認する"""
    results = []
    found_count = 0
    for phrase in phrases:
        found = phrase in script
        if found:
            found_count += 1
        results.append({
            "phrase": phrase,
            "found": found
        })
    
    score = (found_count / len(phrases)) * 100 if phrases else 0
    return {
        "category": category_name,
        "score": score,
        "found": found_count,
        "total": len(phrases),
        "details": results
    }

def check_structure(script):
    """台本構造を確認する"""
    results = []
    found_count = 0
    for marker in STRUCTURE_MARKERS:
        found = marker in script
        if found:
            found_count += 1
        results.append({
            "marker": marker,
            "found": found
        })
    
    score = (found_count / len(STRUCTURE_MARKERS)) * 100
    return {
        "category": "台本構造",
        "score": score,
        "found": found_count,
        "total": len(STRUCTURE_MARKERS),
        "details": results
    }

def check_character_count(script):
    """文字数を確認する"""
    char_count = len(script)
    target_min = 6000
    target_max = 8000
    
    if target_min <= char_count <= target_max:
        score = 100
        status = "適切"
    elif char_count < target_min:
        score = (char_count / target_min) * 100
        status = "不足"
    else:
        score = (target_max / char_count) * 100
        status = "超過"
    
    return {
        "category": "文字数",
        "score": score,
        "char_count": char_count,
        "target_range": f"{target_min}〜{target_max}",
        "status": status
    }

def check_tone(script):
    """トーンを確認する（語尾パターン）"""
    # 「〜のです」「〜なのです」の出現回数
    pattern1 = len(re.findall(r'のです[。、]', script))
    pattern2 = len(re.findall(r'なのです[。、]', script))
    pattern3 = len(re.findall(r'ください[。、]', script))
    
    total_sentences = len(re.findall(r'[。]', script))
    target_patterns = pattern1 + pattern2 + pattern3
    
    # 目標: 文末の30%以上がこれらのパターン
    ratio = (target_patterns / total_sentences) * 100 if total_sentences > 0 else 0
    score = min(100, ratio * 3)  # 30%で100点
    
    return {
        "category": "トーン（語尾）",
        "score": score,
        "のです_count": pattern1,
        "なのです_count": pattern2,
        "ください_count": pattern3,
        "total_sentences": total_sentences,
        "ratio": f"{ratio:.1f}%"
    }

def run_quality_check(filepath):
    """品質検証を実行する"""
    script = load_script(filepath)
    
    results = {
        "file": filepath,
        "checks": []
    }
    
    # 各検証を実行
    results["checks"].append(check_phrases(script, REQUIRED_PHRASES, "必須フレーズ"))
    results["checks"].append(check_phrases(script, SYMPTOM_KEYWORDS, "症状キーワード"))
    results["checks"].append(check_phrases(script, ENDING_PHRASES, "エンディングフレーズ"))
    results["checks"].append(check_structure(script))
    results["checks"].append(check_character_count(script))
    results["checks"].append(check_tone(script))
    
    # 総合スコア計算
    total_score = sum(check["score"] for check in results["checks"]) / len(results["checks"])
    results["total_score"] = total_score
    
    return results

def print_results(results):
    """結果を表示する"""
    print("=" * 60)
    print("台本品質検証レポート")
    print("=" * 60)
    print(f"ファイル: {results['file']}")
    print(f"総合スコア: {results['total_score']:.1f}/100")
    print("-" * 60)
    
    for check in results["checks"]:
        print(f"\n【{check['category']}】 スコア: {check['score']:.1f}/100")
        
        if "details" in check:
            found_items = [d for d in check["details"] if d.get("found")]
            missing_items = [d for d in check["details"] if not d.get("found")]
            
            if found_items:
                print(f"  ✓ 検出: {len(found_items)}件")
            if missing_items:
                print(f"  ✗ 未検出: {[d.get('phrase') or d.get('marker') for d in missing_items]}")
        
        if "char_count" in check:
            print(f"  文字数: {check['char_count']}字 (目標: {check['target_range']})")
            print(f"  状態: {check['status']}")
        
        if "ratio" in check:
            print(f"  語尾パターン使用率: {check['ratio']}")
    
    print("\n" + "=" * 60)
    
    # 改善提案
    print("\n【改善提案】")
    for check in results["checks"]:
        if check["score"] < 80:
            print(f"- {check['category']}: スコア{check['score']:.1f}% - 改善が必要")
    
    if results["total_score"] >= 80:
        print("✓ 全体的に良好な品質です")
    elif results["total_score"] >= 60:
        print("△ いくつかの改善点があります")
    else:
        print("✗ 大幅な改善が必要です")

def main():
    filepath = "/home/ubuntu/youtube_analysis/test_script.txt"
    results = run_quality_check(filepath)
    print_results(results)
    
    # JSON形式でも保存
    with open("/home/ubuntu/youtube_analysis/quality_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n詳細レポートを保存しました: /home/ubuntu/youtube_analysis/quality_report.json")

if __name__ == "__main__":
    main()

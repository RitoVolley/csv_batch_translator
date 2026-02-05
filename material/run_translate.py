from tkinter import messagebox
import requests
import logging
import csv
from io import StringIO
from pathlib import Path
from material.api_register import load_api_config
from charset_normalizer import from_path

# ログ設定
logging.basicConfig(level=logging.ERROR, filename="error.log", format="%(asctime)s - %(levelname)s - %(message)s")

# 定数
DEEPL_API_FREE_URL = "https://api-free.deepl.com/v2/translate"
DEEPL_API_PRO_URL = "https://api.deepl.com/v2/translate"
DEFAULT_SOURCE_LANG = "EN"
DEFAULT_TARGET_LANG = "JA"
MAX_CHARS_PER_REQUEST = 5000  # DeepL APIの1リクエストあたりの推奨文字数制限


def read_csv_file(file_path):
    """CSVファイルを読み込む"""
    try:
        result = from_path(file_path)
        best_match = result.best()
        
        if best_match is None:
            raise ValueError("ファイルのエンコーディングを検出できませんでした")
        
        # str() で文字列として取得（.output() はバイト列を返すため）
        content = str(best_match)
        
        # CSVとして構造的に処理
        reader = csv.reader(StringIO(content))
        rows = list(reader)
        return rows
    except Exception as e:
        logging.error(f"ファイルの読み込みに失敗しました: {e}", exc_info=True)
        raise ValueError(f"ファイルの読み込みに失敗しました: {e}")


def translate_text(api_key, texts, source_lang=DEFAULT_SOURCE_LANG, target_lang=DEFAULT_TARGET_LANG):
    """DeepL APIを使用してテキストを翻訳する（バッチ処理対応）"""
    if not texts:
        return []
    
    translated_texts = []
    batch = []
    current_chars = 0
    
    for text in texts:
        text_len = len(text)
        
        # 文字数制限を超える場合、現在のバッチを送信
        if current_chars + text_len > MAX_CHARS_PER_REQUEST and batch:
            translated_texts.extend(_call_deepl_api(api_key, batch, source_lang, target_lang))
            batch = []
            current_chars = 0
        
        batch.append(text)
        current_chars += text_len
    
    # 残りのバッチを送信
    if batch:
        translated_texts.extend(_call_deepl_api(api_key, batch, source_lang, target_lang))
    
    return translated_texts


def _call_deepl_api(api_key, texts, source_lang, target_lang):
    """DeepL APIを呼び出す内部関数"""
    api_key = api_key.strip()
    api_url = DEEPL_API_FREE_URL if api_key.endswith(":fx") else DEEPL_API_PRO_URL

    headers = {
        'Authorization': f'DeepL-Auth-Key {api_key}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    params = {
        'text': texts,
        'source_lang': source_lang,
        'target_lang': target_lang
    }
    try:
        response = requests.post(api_url, data=params, headers=headers, timeout=30)
        response.raise_for_status()
        return [item['text'] for item in response.json()['translations']]
    except requests.exceptions.Timeout:
        logging.error("翻訳APIがタイムアウトしました", exc_info=True)
        raise ValueError("翻訳APIがタイムアウトしました。再度お試しください。")
    except requests.exceptions.RequestException as e:
        logging.error(f"翻訳APIの呼び出し中にエラーが発生しました: {e}", exc_info=True)
        raise ValueError(f"翻訳APIの呼び出し中にエラーが発生しました: {e}")


def save_translated_file(output_path, translated_rows):
    """翻訳結果をCSVファイルに保存する"""
    try:
        with open(output_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(translated_rows)
    except Exception as e:
        logging.error(f"翻訳結果の書き込み中にエラーが発生しました: {e}", exc_info=True)
        raise ValueError(f"翻訳結果の書き込み中にエラーが発生しました: {e}")


def _translate_csv_rows(api_key, rows):
    """CSVの各行を翻訳する"""
    # 全セルをフラット化
    flat_texts = []
    cell_positions = []  # (row_index, col_index) のリスト
    
    for row_idx, row in enumerate(rows):
        for col_idx, cell in enumerate(row):
            flat_texts.append(cell)
            cell_positions.append((row_idx, col_idx))
    
    # 一括翻訳
    translated_texts = translate_text(api_key, flat_texts)
    
    # 元の構造に戻す
    translated_rows = [row[:] for row in rows]  # 深いコピー
    for idx, (row_idx, col_idx) in enumerate(cell_positions):
        translated_rows[row_idx][col_idx] = translated_texts[idx]
    
    return translated_rows


def run_translation(file_path, on_success=None, on_error=None):
    """指定されたファイルパスに対してバッチ翻訳を実行します。

    Args:
        file_path: CSV ファイルのパス
        on_success: 成功時のコールバック関数 (message: str) -> None
        on_error: エラー時のコールバック関数 (message: str) -> None
    """
    # デフォルトのコールバック（UIとの結合を維持しつつ、テスト時は差し替え可能）
    if on_success is None:
        on_success = lambda msg: messagebox.showinfo("情報", msg)
    if on_error is None:
        on_error = lambda msg: messagebox.showerror("エラー", msg)

    try:
        rows = read_csv_file(file_path)
    except Exception as e:
        on_error(str(e))
        return

    # APIキーの取得
    config = load_api_config()
    api_key = config.get("api_key", "")
    if not api_key:
        on_error("APIキーが設定されていません。API登録画面でキーを登録してください。")
        return

    try:
        translated_rows = _translate_csv_rows(api_key, rows)
        path = Path(file_path)
        output_path = path.with_stem(path.stem + '_translated')
        save_translated_file(str(output_path), translated_rows)
        on_success(f"翻訳が完了しました。出力ファイル: {output_path}")
    except Exception as e:
        on_error(str(e))
from tkinter import messagebox
import requests
from material.api_register import load_api_config

def run_translation(file_path):
    """指定されたファイルパスに対してバッチ翻訳を実行します。

    `file_path` は CSV ファイルまたはディレクトリを想定しています。
    ここに翻訳ワークフロー（CSV の読み込み、API 呼び出し、翻訳結果の書き出し）を実装してください。
    """
    # CSVファイルの読み込み
    # 複数のエンコーディングに対応
    encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'latin-1']
    lines = None
    try:
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    lines = f.readlines()
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if lines is None:
            raise ValueError(f"{file_path} をサポートされているエンコーディング {encodings} で読み込めませんでした")
        
        messagebox.showinfo("情報", f"ファイルを正常に読み込みました: {file_path} (エンコーディング: {encoding})")

    except Exception as e:
        messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました: {e}")
        return
    
    # APIキーの取得
    config = load_api_config()
    API_KEY = config.get("api_key", "")
    if not API_KEY:
        messagebox.showerror("エラー", "APIキーが設定されていません。API登録画面でキーを登録してください。")
        return

    # 翻訳APIの呼び出し
    params = {
        'auth_key':API_KEY,
        'text': lines,
        'source_lang':'EN',
        'target_lang':'JA'
        }

    # 翻訳結果の書き出し

    try:
        response = requests.post("https://api-free.deepl.com/v2/translate", data=params)
        response.raise_for_status()
        result = response.json()

        translated_lines = [item['text'] for item in result['translations']]
        output_path = file_path.rsplit('.', 1)[0] + '_translated.csv'
        with open(output_path, "w", encoding="utf-8") as f:
            for line in translated_lines:
                f.write(line + "\n")
        
        messagebox.showinfo("情報", f"翻訳が完了しました。出力ファイル: {output_path}")

    except Exception as e:
        messagebox.showerror("エラー", f"翻訳中にエラーが発生しました: {e}")


    
import tkinter as tk
from tkinter import messagebox
import json
import os

# .env をプロジェクトルートに置いて API キーを管理します
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))


def _read_env_lines() -> list[str]:
    """`.env` ファイルを行ごとに読み込み、行リストを返します。

    ファイルが存在しない場合は空のリストを返します。
    """
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []


def _write_env_lines(lines: list[str]) -> None:
    """指定された行を `.env` ファイルに書き込みます。必要に応じてディレクトリを作成します。"""
    os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


def load_api_config() -> dict:
    """`.env` ファイルを解析して保存されている API キーを返します。

    `API_KEY` または `TRANSLATION_API_KEY` を探し、見つかれば {"api_key": 値} を返します。見つからない場合は空の dict を返します。
    """
    lines = _read_env_lines()
    for line in lines:
        if not line or line.strip().startswith("#"):
            continue
        if line.strip().startswith("API_KEY=") or line.strip().startswith("TRANSLATION_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('\"\'')
            return {"api_key": key}
    return {}


def save_api_config(config: dict) -> None:
    """`.env` ファイルに API キーを保存します。

    既存の `API_KEY`/`TRANSLATION_API_KEY` 行を更新するか、無ければ `API_KEY="<value>"` 行を追記します。
    """
    key = config.get("api_key", "").strip()
    lines = _read_env_lines()
    found = False
    out_lines: list[str] = []
    for line in lines:
        if line.strip().startswith("API_KEY=") or line.strip().startswith("TRANSLATION_API_KEY="):
            out_lines.append(f'API_KEY="{key}"\n')
            found = True
        else:
            out_lines.append(line)
    if not found:
        out_lines.append(f'API_KEY="{key}"\n')
    _write_env_lines(out_lines)


def open_api_register_window(parent: tk.Tk | None = None) -> None:
    """API キーを入力・保存できるモーダルウィンドウを開きます。

    既存のキーがあれば読み込み、ユーザーが編集して保存ボタンを押すと `.env` に書き込みます。
    """
    win = tk.Toplevel(parent) if parent else tk.Tk()
    win.title("API登録")
    win.geometry("400x150")
    win.resizable(False, False)

    config = load_api_config()
    api_key = config.get("api_key", "")

    frame = tk.Frame(win)
    frame.pack(padx=10, pady=10, fill=tk.X)

    label = tk.Label(frame, text="APIキー：")
    label.pack(side=tk.LEFT)

    entry = tk.Entry(frame, width=40)
    entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    entry.insert(0, api_key)

    def on_save():
        key = entry.get().strip()
        if not key:
            messagebox.showwarning("入力エラー", "APIキーを入力してください。", parent=win)
            return
        save_api_config({"api_key": key})
        messagebox.showinfo("保存完了", "APIキーを保存しました。", parent=win)
        win.destroy()

    def on_cancel():
        win.destroy()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    save_btn = tk.Button(btn_frame, text="保存", command=on_save)
    save_btn.pack(side=tk.LEFT, padx=5)

    cancel_btn = tk.Button(btn_frame, text="キャンセル", command=on_cancel)
    cancel_btn.pack(side=tk.LEFT, padx=5)

    if parent:
        win.transient(parent)
    win.grab_set()
    win.focus()

import tkinter as tk
from tkinter import filedialog
import os
import material.run_translate as run_translate
import material.demo_runner as demo_runner
import material.api_register as api_register


def use_screen_operation():
    """CSV一括翻訳ツールのメインウィンドウを作成して表示します。

    上部のボタン（デモ／API登録）、ファイルパス入力欄、実行ボタンなどの UI を構築し、
    Tk のメインループを開始します。ウィンドウが閉じられるまで処理はブロックされます。
    """
    root = tk.Tk()
    root.title("CSV一括翻訳ツール")
    root.geometry("400x150")
    root.resizable(False, False) # ウィンドウサイズ固定

    # 上部のボタン（横並び）
    top_button_frame = tk.Frame(root)
    top_button_frame.pack(pady=(5, 0), fill=tk.X)

    demo_button = tk.Button(top_button_frame, text="デモ実行", command=run_demo_callback)
    demo_button.pack(side=tk.LEFT, padx=5)

    api_register_button = tk.Button(top_button_frame, text="API登録画面へ遷移", command=lambda: api_register.open_api_register_window(root))
    api_register_button.pack(side=tk.LEFT, padx=5)

    # ファイルパス入力行
    execute_frame = tk.Frame(root)
    execute_frame.pack(pady=10, fill=tk.X)
    
    label = tk.Label(execute_frame, text="ファイルパス：")
    label.pack(side=tk.LEFT)
    
    entry = tk.Entry(execute_frame, width=40)
    entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    file_select_button = tk.Button(execute_frame, text="ファイル選択", command=lambda: select_file(entry))
    file_select_button.pack(side=tk.LEFT, padx=5)

    # 実行ボタン（下の行、右端）
    action_frame = tk.Frame(root)
    action_frame.pack(fill=tk.X, pady=(5, 0))
    run_button = tk.Button(action_frame, text="実行", command=lambda: run_translation_callback(entry))
    run_button.pack(side=tk.RIGHT, padx=5)

    root.mainloop()

def run_translation_callback(entry):
    """実行ボタンが押されたときの処理を行います。

    エントリ上に保持されているフルパス（`entry.full_path`）を優先的に用いて
    `material.run_translate.run_translation` に処理を委譲します。手動入力時は
    `entry.get()` の値が使われます。
    """
    file_path = getattr(entry, "full_path", entry.get())
    run_translate.run_translation(file_path)

def run_demo_callback():
    """デモ実行ボタンの処理を行います。

    現在は `material.demo_runner.run_demo()` を呼び出します。必要に応じて前後処理を追加してください。
    """
    demo_runner.run_demo()

# ファイル選択ボタンの処理
def select_file(entry_widget):
    """ファイル選択ダイアログを開き、選択したパスを Entry にセットします。

    エントリにはフルパスを格納しますが、表示位置は末尾（ファイル名側）が見える
    ようにスクロールしておきます。実際のフルパスは `entry_widget.full_path` に保持されます。
    """
    path = filedialog.askopenfilename(filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")])
    if path:
        # エントリにフルパスを保持し、テキストはフルパスで挿入
        entry_widget.full_path = path
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, path)
        # 表示を末尾側に移動（ファイル名が見えるようにする）
        try:
            entry_widget.update_idletasks()
            entry_widget.icursor(tk.END)
            entry_widget.xview_moveto(1.0)
        except Exception:
            # 古い Tk バージョンなどで失敗しても致命的ではない
            pass
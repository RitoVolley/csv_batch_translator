# CSV一括翻訳ツール（DeepL API連携・GUI付き）

CSVファイル内のテキストを **DeepL API でまとめて翻訳** し、翻訳後のCSVを自動生成する
Python製のデスクトップツールです。プログラミングをしない方でも使えるよう、
**Tkinter製のGUI（画面操作）** を備えています。

英語のデータを日本語にまとめて変換したい場合などに、ファイルを選んでボタンを押すだけで
一括翻訳が完了します。実務での利用を想定し、**APIキーの安全な管理・文字コードの自動判定・
エラーログ出力** に配慮しています。

## 画面

メインウィンドウは「デモ実行 / API登録」ボタン、ファイル選択欄、実行ボタンで構成されています。

<!-- スクリーンショットは docs/screenshot.png として追加予定 -->

## 主な機能

- **CSVの一括翻訳**: CSV内の全セルを翻訳し、`元のファイル名_translated.csv` として同じ場所に出力
- **GUI操作**: ファイル選択ダイアログから対象CSVを指定し、ボタン1つで翻訳実行
- **APIキーのGUI登録**: 「API登録」画面からDeepLのAPIキーを入力・保存（`.env` に保存）
- **バッチ処理**: DeepL APIの文字数制限（1リクエスト5,000字）に合わせて自動分割して送信
- **Free / Pro 自動判定**: APIキーの種別（`:fx` 終端）を見て、無料版・有料版のエンドポイントを自動選択
- **文字コード自動判定**: `charset-normalizer` により、UTF-8 / Shift_JIS など混在環境でも自動で読み込み
- **エラーログ出力**: 失敗時の内容を `error.log` に記録（タイムアウト・API失敗・読み書き失敗など）

## 翻訳の方向

既定では **英語（EN）→ 日本語（JA）** で翻訳します。
（`material/run_translate.py` の `DEFAULT_SOURCE_LANG` / `DEFAULT_TARGET_LANG` で変更可能）

## セットアップ

### 1. 必要環境

| 項目 | バージョン |
|------|------------|
| Python | 3.10 以上 |
| OS | Windows / macOS（Tkinterが利用できる環境） |

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

主な依存: `requests`（API通信）/ `charset-normalizer`（文字コード判定）

## 使い方

### 1. ツールを起動する

```bash
python csv_batch_translator.py
```

### 2. APIキーを登録する（初回のみ）

1. 画面上部の「**API登録**」ボタンをクリック
2. DeepLのAPIキーを入力して「保存」
   （キーは、ツールと同じ場所にある `.env` ファイルに保存されます）

### 3. CSVを翻訳する

1. 「**選択**」ボタンから翻訳したいCSVファイルを選ぶ
2. 「**実行**」ボタンをクリック
3. 翻訳が完了すると、同じフォルダに `元のファイル名_translated.csv` が出力されます

## APIキーの安全管理について

- APIキーは **`.env` ファイルで管理** し、`.gitignore` で除外しています。
  GitHub上には機密情報を一切含めない設計です。
- APIキーの種別（無料/有料）はキーの形式から自動判定するため、利用者の設定は不要です。

## DeepL APIキーの取得手順

1. DeepL API のページを開く: <https://www.deepl.com/pro-api>
2. 画面右上の「ログイン」から、DeepLアカウントにログインする
3. ログイン後、右上のアカウントアイコン →「アカウント」を選択する
4. 「APIキーと制限」タブに移動し、APIキーを確認する
   - タブが表示されていない場合は、右上の「Start free trial」から **「API Free」プラン** を選択
     （※ Pro版にアップグレードしなければ料金は発生しません）
   - キーが未生成の場合は、新しいAPIキーを生成する
5. 表示されたAPIキーをコピーし、本ツールの「API登録」画面に貼り付けて保存する

## 制限事項

- 本ツールの利用には **DeepLのAPIキー** が必要です。
- 翻訳できる文字数は、DeepLの契約プラン（無料版は月50万文字など）の上限に従います。
- 翻訳対象はCSVの**全セル**です。翻訳不要な列がある場合は、事前に分けてご利用ください。
- 出力ファイルの文字コードは **UTF-8** です。

## 技術スタック

- **言語**: Python 3.10+
- **GUI**: Tkinter
- **API通信**: requests（DeepL API v2）
- **文字コード判定**: charset-normalizer
- **設定管理**: `.env`（APIキー）

## プロジェクト構成

```
csv_batch_translator/
├── csv_batch_translator.py        # エントリポイント（GUI起動）
├── material/
│   ├── user_screen_operation.py   # メイン画面（GUI構築）
│   ├── api_register.py            # APIキー登録画面・.env読み書き
│   ├── run_translate.py           # 翻訳処理本体（CSV読込・DeepL呼出・出力）
│   └── demo_runner.py             # デモ実行
├── requirements.txt
├── .env                           # APIキー（.gitignoreで除外）
└── README.md
```

## ライセンス

MIT License

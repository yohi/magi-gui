# MAGI GUI

magi-core 合議エンジンのための Streamlit GUI フロントエンド。

## 必須要件 (Requirements)

- Python 3.11以上
- ローカルの magi-core チェックアウトが `../magi-core` に存在すること

## セットアップ (Setup)

```bash
# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# または: .venv\Scripts\activate  # Windows

# uv でインストール (推奨)
uv pip install -e .

# または pip でインストール
pip install -e .
```

## 実行 (Run)

```bash
# CLI コマンドを使用
magi-gui

# または Streamlit で直接実行
streamlit run src/magi_gui/app.py
```

## 設定 (Configuration)

GUI のサイドバーで以下の設定が可能です:

- **Gemini API Key**: Google Gemini APIキー (必須)
- **Model**: `gemini-1.5-pro` または `gemini-1.5-flash` を選択
- **Debate Rounds**: 議論のラウンド数 (1-5)

## 環境変数 (Environment Variables)

アプリケーション実行時、自動的に以下の環境変数が設定されます:

- `MAGI_DEFAULT_PROVIDER=gemini`
- `MAGI_GEMINI_API_KEY` - あなたの API キー
- `MAGI_GEMINI_MODEL` - 選択されたモデル
- `MAGI_GEMINI_ENDPOINT=https://generativelanguage.googleapis.com`

## 使い方 (Usage)

1. サイドバーに Gemini API キーを入力します
2. 使用するモデルを選択します
3. 必要に応じて議論のラウンド数を調整します
4. テキストエリアに議題(プロンプト)を入力します
5. "INITIALIZE" をクリックして合議エンジンを実行します
6. 結果を確認します: Thinking (思考), Debate (議論), Voting (投票), Final Decision (最終判定)

## ドキュメント (Documentation)

- [Google AI Studio アプリケーション開発ガイド](docs/GOOGLE_AI_STUDIO_GUIDE.md) - Google AI Studio を活用してアプリケーションをプロトタイプ・構築する方法のガイド。

## プロジェクト構成 (Project Structure)

```text
magi-gui/
├── pyproject.toml          # プロジェクト設定
├── README.md               # このファイル
├── .streamlit/
│   └── config.toml         # Streamlit テーマ設定
└── src/
    └── magi_gui/
        ├── __init__.py     # パッケージ初期化
        ├── main.py         # CLI ランチャー
        ├── app.py          # Streamlit アプリケーション本体
        └── assets/
            └── style.css   # カスタム CSS スタイル
```

## エラーハンドリング (Error Handling)

GUI は `MagiException` エラーを捕捉し、以下を表示します:
- エラーコード (例: `CONFIG_001`)
- エラーメッセージ

一般的な例外も捕捉され、ユーザーフレンドリーなメッセージで表示されます。

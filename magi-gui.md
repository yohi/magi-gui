# **MAGI GUI (Gemini Edition) 設計・仕様書**

Version: 1.0.0  
Status: Draft  
Target Framework: Python 3.11+ / Streamlit  
Dependency: magi-core

## **1\. プロジェクト概要**

### **1.1 目的**

CLIツールである magi-core の合議エンジンを利用し、Webブラウザ上で動作するグラフィカルなインターフェースを提供する。特に Google Gemini (1.5 Pro/Flash) をバックエンドモデルとして採用し、3賢者（MELCHIOR, BALTHASAR, CASPER）による議論プロセスを視覚的に体験できるアプリケーションを構築する。

### **1.2 設計思想**

* **疎結合 (Decoupled)**: magi-core をライブラリとしてインポートし、GUI側のロジックとCore側のロジックを分離する。  
* **パッケージ化 (Packageable)**: 単体で pip install magi-gui (または uv add) 可能なPythonパッケージとして構成する。  
* **設定の柔軟性**: APIキーやモデル設定をGUI上および環境変数の双方から注入可能にする。

## **2\. システムアーキテクチャ**

### **2.1 コンポーネント構成**

コード スニペット

graph TB  
    User((User)) \--\>|Browser Access| GUI\[MAGI GUI (Streamlit)\]  
      
    subgraph "magi-gui Package"  
        GUI \--\>|Import| Wrapper\[Launcher (main.py)\]  
        GUI \--\>|Config| Session\[Session State\]  
    end  
      
    subgraph "magi-core Library"  
        GUI \--\>|Execute| Engine\[Consensus Engine\]  
        Engine \--\>|3 Agents| Personas\[Melchior/Balthasar/Casper\]  
        Personas \--\>|API Call| Provider\[Gemini Provider\]  
    end  
      
    Provider \--\>|HTTPS| GoogleAI\[Google AI Studio API\]

### **2.2 依存関係**

* **Runtime**: Python 3.11+  
* **Frontend**: streamlit\>=1.40.0  
* **Core Logic**: magi\>=0.1.0 (magi-core)  
* **Network**: httpx (Gemini API通信用)

## **3\. ディレクトリ・パッケージ構成**

magi-core とは別のルートディレクトリを持つ、独立したパッケージ構造とします。

Plaintext

magi-gui/  
├── pyproject.toml           \# 依存管理・エントリーポイント定義  
├── README.md                \# 利用マニュアル  
└── src/  
    └── magi\_gui/  
        ├── \_\_init\_\_.py  
        ├── main.py          \# CLI起動用ラッパー (entrypoint)  
        ├── app.py           \# Streamlit アプリケーション本体  
        └── assets/          \# (Optional) CSS, 画像などの静的リソース  
            └── style.css

### **3.1 pyproject.toml 定義**

magi-core を依存関係として定義し、コマンドラインツール magi-gui を登録します。

Ini, TOML

\[project\]  
name \= "magi-gui"  
version \= "0.1.0"  
description \= "MAGI System GUI Frontend for Gemini"  
requires-python \= "\>=3.11"  
dependencies \= \[  
    "streamlit\>=1.40.0",  
    "httpx\>=0.27.0",  
    "magi",  \# PyPI公開前は tool.uv.sources 等でローカルパスを指定  
\]

\[project.scripts\]  
magi-gui \= "magi\_gui.main:main"

## **4\. 機能要件**

### **4.1 メイン機能**

1. **合議の実行**: ユーザー入力（議題）に対し、3賢者による議論と投票を実行し、最終判定を表示する。  
2. **プロセス可視化**:  
   * **Thinking Phase**: 3賢者それぞれの初期思考を並列表示。  
   * **Debate Phase**: ラウンドごとの議論（反論・補足）を時系列またはタブ形式で表示。  
   * **Voting Phase**: 各賢者の投票内容（承認/否決/条件付）と理由、および最終的な合議結果を表示。

### **4.2 設定機能 (Sidebar)**

1. **API Key管理**: Google AI Studio API Key の入力（環境変数 MAGI\_GEMINI\_API\_KEY がある場合はデフォルト値として表示）。  
2. **モデル選択**: gemini-1.5-pro / gemini-1.5-flash の切り替え。  
3. **議論設定**: Debate Rounds（議論の往復回数）の指定（1〜5回）。

## **5\. UI/UX 設計**

Streamlitのカラム機能を利用し、MAGIシステムの特徴である「3つの視点」を強調するレイアウトとします。

### **5.1 画面レイアウト概略**

| エリア | コンテンツ | 備考 |
| :---- | :---- | :---- |
| **Header** | タイトルロゴ "MAGI SYSTEM (Gemini Edition)" | 中央揃え、赤/黒基調 |
| **Input Area** | テキストエリア（議題入力）、実行ボタン | 画面上部 |
| **Status Bar** | 進捗状況（Thinking... / Debating...） | スピナー表示 |
| **Phase 1** | **\[MELCHIOR\]** | **\[BALTHASAR\]** |
| **Phase 2** | ラウンドごとの議論ログ | Expander（折りたたみ）形式推奨 |
| **Phase 3** | **最終判定 (APPROVED / DENIED)** | 大きく表示、色分け（緑/赤） |
| **Table** | 投票内訳テーブル | 誰が何に投票したかの一覧 |

### **5.2 スタイル定義 (CSS)**

MAGIシステムの世界観を再現するため、以下の配色ルールを適用します（st.markdown でCSS注入）。

* **MELCHIOR (科学)**: 青系 (\#0099cc)  
* **BALTHASAR (母性)**: オレンジ/黄系 (\#ff9900)  
* **CASPER (女)**: 赤/紫系 (\#cc00cc)  
* **背景**: ダークモード推奨 (\#0e1117)  
* **フォント**: 等幅フォントまたはシステムフォント（未来的な印象）

## **6\. 実装詳細**

### **6.1 src/magi\_gui/main.py (ランチャー)**

streamlit run コマンドを内部的に呼び出すラッパー関数。

Python

import sys  
from pathlib import Path  
from streamlit.web import cli as stcli

def main():  
    app\_path \= Path(\_\_file\_\_).parent / "app.py"  
    \# 実行引数を構築: streamlit run /path/to/app.py \[args...\]  
    sys.argv \= \["streamlit", "run", str(app\_path)\] \+ sys.argv\[1:\]  
    sys.exit(stcli.main())

### **6.2 src/magi\_gui/app.py (GUIロジック)**

ConsensusEngine とのインターフェース部分。非同期処理を適切に扱う必要があります。

**主要ロジックフロー:**

1. **初期化**: st.set\_page\_config でレイアウト設定。  
2. **設定読み込み**: サイドバーからAPIキー等の入力を取得。  
3. **イベントハンドリング**: 「INITIALIZE」ボタン押下を検知。  
4. **環境変数注入**: os.environ\["MAGI\_GEMINI\_API\_KEY"\] 等に値をセット（ProviderContext が環境変数を参照するため）。  
5. **エンジン実行**:  
   Python  
   \# Configオブジェクトの生成と設定  
   config \= Config()  
   config.debate\_rounds \= user\_rounds  
   config.model \= user\_model

   \# エンジン初期化と実行  
   engine \= ConsensusEngine(config=config)  
   result \= asyncio.run(engine.execute(user\_prompt))

6. **結果レンダリング**:  
   * result.thinking\_results\[PersonaType.MELCHIOR\].content などを取り出し、対応するカラムに表示。  
   * result.final\_decision の値に応じて表示色を変更（Decision.APPROVED \-\> 緑, etc.）。

## **7\. 開発・デプロイ手順**

### **7.1 ローカル開発環境のセットアップ**

magi-core が隣接ディレクトリにある場合の開発フロー。

Bash

\# プロジェクト作成  
mkdir magi-gui && cd magi-gui  
uv init

\# 依存関係の追加 (magi-coreをeditableモードで参照)  
\# pyproject.toml の \[tool.uv.sources\] に記述を追加してから  
uv sync

### **7.2 実行**

Bash

\# 開発中  
uv run magi-gui

### **7.3 配布**

PyPIへの公開、またはGitリポジトリとしての配布が可能。ユーザーは以下のコマンドでインストール・実行できる。

Bash

\# インストール  
pip install git+https://github.com/yourname/magi-gui.git

\# 実行  
magi-gui

## **8\. 将来の拡張性 (Future Work)**

* **リアルタイムストリーミング**: ConsensusEngine のストリーミング出力をStreamlitの st.write\_stream に適合させるアダプタの実装。  
* **PDF/画像入力**: Geminiのマルチモーダル機能を活かし、ファイルアップローダーを追加して engine.execute に画像データを渡す拡張。  
* **レポート出力**: 合議結果をMarkdownファイルとしてダウンロードする機能。

---

この設計書に基づき実装を進めることで、Coreのロジックを汚染することなく、メンテナンス性の高いGUIアプリケーションを構築できます。
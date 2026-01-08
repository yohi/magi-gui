
# Google AI Studio を活用したアプリケーション開発ガイド

このドキュメントでは、Google AI Studio でプロトタイプを作成し、それを Python アプリケーション (magi-gui) として実装するまでの流れを解説します。
本ガイドは、[Google AI Studio Quickstart](https://ai.google.dev/gemini-api/docs/ai-studio-quickstart?hl=ja) の内容に基づいています。

## 1. Google AI Studio とは

Google AI Studio は、Google の最新の生成 AI モデル (Gemini 2.0, 1.5 Pro/Flash 等) をWebブラウザ上で素早く試作・実験できる開発者向け環境です。

URL: [https://aistudio.google.com/](https://aistudio.google.com/)

## 2. 開発フロー概要

1.  **API Key の取得**: Google AI Studio で API キーを発行。
2.  **プロンプト作成**: ブラウザ上で「Chat」プロンプトを作成し、動作を調整。
3.  **コード化**: "Get Code" 機能で Python コードを取得し、アプリに組み込み。
4.  **UI 実装**: Streamlit などで GUI を作成。

## 3. ステップ・バイ・ステップ手順

### Step 1: API Key の取得

1.  [Google AI Studio](https://aistudio.google.com/) にアクセスし、ログインします。
2.  画面左側のサイドバーにある **"Get API key"**（鍵のアイコン）をクリックします。
3.  **"Create API key"** をクリックし、Google Cloud プロジェクトと紐付けてキーを作成します。
    * *注意: 初回作成時はプロジェクトの作成画面が表示される場合があります。*
4.  取得したキーをコピーし、`.env` ファイル等に保存します。

### Step 2: プロンプトの作成とSystem Instructionsの設定

新しいインターフェースでは、「Create new」ボタンではなく、サイドバーやホーム画面から直接形式を選択します。

1.  **プロンプトの新規作成**:
    -  **方法A**: 画面左上の **"Create new"** (青い「＋」アイコン) をクリックし、**"Chat prompt"** を選択。
    -  **方法B**: 画面左側のサイドバーから **"Chat"** タブを選択し、リスト上部の「＋」または新規作成アイコンをクリック。
    -  **方法C**: ホーム画面上の **"Chat prompt"** カードをクリック。

2.  **System Instructions (システム指示) の入力**:
    - 画面上部にある **"System Instructions"** というセクション（または「＋」ボタン）をクリックして展開します。
    - ここに MAGI システムの人格定義（MELCHIOR, BALTHASAR, CASPER の役割）を入力します。

3.  **モデルの選択とテスト**:
    - 右側の **Run settings** パネルで、**Model** (例: `gemini-1.5-flash`) を選択します。
    - 画面下部のチャット入力欄 ("Type something...") にテスト用の議題を入力し、**Run** ボタンで動作を確認します。

### Step 3: Python コードへのエクスポート (Google Gen AI SDK)

プロンプトができたら、コードとしてエクスポートします。現在は新しい SDK (`google-genai`) が推奨されています。

1.  画面右上の **"Get code"**（`< >` アイコン）をクリックします。
2.  タブから **Python** を選択します。
3.  表示されたコードをコピーします。

### Step 4: アプリケーションへの組み込み

新しい SDK `google-genai` を使用して実装します。

**ライブラリのインストール:**

```bash
pip install -U google-genai
```

**実装例 (`google-genai` SDK版):**

```python
from google import genai
from google.genai import types

class GeminiAdapter:
    def __init__(self, api_key, system_instruction):
        # クライアント初期化 (v1.0以降の形式)
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-1.5-flash"
        self.config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )

    def generate_content(self, prompt):
        # テキスト生成の実行
        response = self.client.models.generate_content(
            model=self.model_name,
            config=self.config,
            contents=prompt
        )
        return response.text
```

### Step 5: Streamlit での GUI 化 (magi-gui)

`magi-gui` では、このアダプターを使用して3つのモデル（賢者）からの回答を非同期で取得し、表示します。

```python
import streamlit as st
import asyncio

# (中略: アダプターの初期化など)

async def main():
    st.title("MAGI System")
    user_input = st.text_area("議題を入力")
    
    if st.button("審議開始"):
        # 3賢者の並列実行イメージ
        results = await asyncio.gather(
            melchior.generate_content_async(user_input),
            balthasar.generate_content_async(user_input),
            casper.generate_content_async(user_input)
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"### MELCHIOR\n{results[0]}")
        with col2:
            st.markdown(f"### BALTHASAR\n{results[1]}")
        with col3:
            st.markdown(f"### CASPER\n{results[2]}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. 参考情報

- **Google AI Studio Quickstart**: [https://ai.google.dev/gemini-api/docs/ai-studio-quickstart?hl=ja](https://ai.google.dev/gemini-api/docs/ai-studio-quickstart?hl=ja)
- **Google Gen AI SDK for Python**: [https://github.com/googleapis/python-genai](https://github.com/googleapis/python-genai)

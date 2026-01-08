# Google AI Studio を活用したアプリケーション開発ガイド

このドキュメントでは、Google AI Studio でプロトタイプを作成し、それを Python アプリケーション (magi-gui) として実装するまでの流れを解説します。

## 1. Google AI Studio とは

Google AI Studio は、Google の最新の生成 AI モデル (Gemini 1.5 Pro, Flash, Gemini 2.0 など) をWebブラウザ上で素早く試作・実験できる開発者向け環境です。

**主な機能:**

- **Prompts**: チャット形式(Chat)やフリーフォームでプロンプトを設計。
- **System Instructions**: AI の役割や振る舞いを定義 (今回の MAGI システムの核心部分)。
- **Get Code**: 作成したプロンプト設定を Python, JavaScript, cURL などのコードとしてエクスポート。

URL: [https://aistudio.google.com/](https://aistudio.google.com/)

## 2. 開発フロー概要

1.  **API Key の取得**: Google AI Studio で API キーを発行（Google Cloud プロジェクトと連携）。
2.  **プロンプト設計 (Prototyping)**: ブラウザ上で期待通りの応答が返るまで調整。
3.  **コード化 (Integration)**: "Get Code" 機能で Python コードを取得し、アプリに組み込み。
4.  **UI 実装 (Application)**: Streamlit などで GUI を作成。

## 3. ステップ・バイ・ステップ手順

### Step 1: API Key の取得

1.  [Google AI Studio](https://aistudio.google.com/) にアクセスし、Google アカウントでログイン。
2.  画面左上のサイドバーにある **"Get API key"** (鍵アイコン) をクリック。
3.  **"Create API key"** を押し、連携する Google Cloud プロジェクトを選択します（通常は "Create API key in new project" で新規作成）。
4.  取得したキーは、開発環境の `.env` ファイルや環境変数 `GEMINI_API_KEY` (本プロジェクトでは `MAGI_GEMINI_API_KEY`) として保存します。

### Step 2: MAGI システムのプロトタイピング

MAGI システムのような「役割を持ったAI」を作るには、**System Instructions** が重要です。

1.  画面左上の **"Create new"** (または **"+"** アイコン) -> **"Chat prompt"** を選択。
2.  画面上部（または "System Instructions" セクションを展開）の入力欄に、各賢者 (MELCHIOR, BALTHASAR, CASPER) の人格定義を入力します。
    * *例: MELCHIOR の場合*
        ```text
        あなたは MELCHIOR (メルキオール) です。
        科学者としての視点から、論理的かつ客観的に物事を分析します。
        感情を排し、データと事実に基づいた判断を行ってください。
        ...
        ```
3.  画面右側の **Run settings** でモデル (Gemini 1.5 Flash, Gemini 1.5 Pro 等) を選択し、Temperature (創造性) を調整します。
4.  下部の User 入力欄にテスト用の議題 (例:「人類補完計画について」) を入力し、Run ボタンで応答を確認します。

### Step 3: Python コードへのエクスポート

プロンプトの挙動に満足したら、それをコードとして取り出します。
**注意:** Google AI Studio は現在、新しい **Google Gen AI SDK** (`google-genai`) のコードを出力します。

1.  画面右上の **Get code** ボタン (< > アイコン) をクリック。
2.  言語タブから **Python** を選択。
3.  表示されたコードをコピーします。

### Step 4: Python アプリケーションへの組み込み

取得したコードを関数やクラスにラップして、アプリケーションから使いやすくします。
`magi-gui` や `magi-core` では、これを `GeminiAdapter` クラスとして実装しています。

**必要なライブラリ:**

従来の `google-generativeai` ではなく、新しい SDK を使用します。

```bash
pip install google-genai
```

**実装例 (概念コード - 新しいSDK):**

```python
import os
from google import genai
from google.genai import types

class GeminiAdapter:
    def __init__(self, api_key, system_instruction):
        # クライアントの初期化
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-1.5-flash"
        self.config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )

    def generate_content(self, prompt):
        response = self.client.models.generate_content(
            model=self.model_name,
            config=self.config,
            contents=prompt
        )
        return response.text
```

### Step 5: Streamlit での GUI 化

AI のロジックができたら、Streamlit で画面を作ります。

```python
import streamlit as st
import asyncio

st.title("MAGI System")
user_input = st.text_area("議題を入力")

if st.button("審議開始"):
    # 非同期処理で3賢者を並列実行する例（magi-guiの実装イメージ）
    async def run_magi():
        melchior_res = await melchior_adapter.generate_content_async(user_input)
        balthasar_res = await balthasar_adapter.generate_content_async(user_input)
        casper_res = await casper_adapter.generate_content_async(user_input)
        st.write("MELCHIOR:", melchior_res)
        st.write("BALTHASAR:", balthasar_res)
        st.write("CASPER:", casper_res)

    asyncio.run(run_magi())

```

## 4. Tips

**モデルの選択**:

- `Gemini 1.5 Pro`: 高精度、複雑な推論向き。
- `Gemini 1.5 Flash`: 高速、低コスト。チャットや単純なタスク向き。

**Safety Settings**:

- 暴力的な表現やヘイトスピーチに対するフィルタ設定も、AI Studio 上の "Run settings" (または "Safety settings") で調整可能です。

**SDKのバージョン**:

- 本ガイドでは最新の `google-genai` (v1.0以降) を使用しています。古い記事にある `google-generativeai` とは互換性がない部分があるため注意してください。

---

このガイドを参考に、独自のシステムプロンプトを作成し、オリジナルの AI アプリケーションを開発してみてください。

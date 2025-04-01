# Easy ai Trans

画面に表示されたテキストを翻訳してくれる小型ツール。  
翻訳ログは半透明ウィンドウに表示、スクリーンショット＆GPT-4o or Geminiで処理。

# 使用にはOpenAI（有料）/Gemini(無料可)のAPIキーが必要です！
- 通知アイコン右クリック→設定からAPIキーを入力  
- ボタンでモデル一覧を取得  
- 好きなモデルを選択
- ※コスト的には1翻訳0.002$位・・・？  
テストで38回投げて0.09$とかなってるからもっと安いかも・・・

## 機能

- カメラボタンで画面全体キャプチャ → 翻訳
- ↓ボタンでウィンドウが覆っている領域キャプチャ → 翻訳
- 翻訳ログは実行ファイルのあるディレクトリ/history下に自動保存（画像＋テキスト）
- 通知領域常駐・設定は通知領域右クリックから
- マルチディスプレイ対応

### 予定
- メイン画面タブUIにして動的にプロバイダ切り替えた方が便利そう・・・？

## 動きがおかしくなったら
config.iniがおかしいかも？  
一度config.iniを消してから実行ファイル立ち上げると自動生成されます  

## 必要ライブラリ

```bash
pip install -r requirements.txt

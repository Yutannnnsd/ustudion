# Studio U Yuta

VS Codeで編集しながら進めるための、トップページだけの最小構成です。

## 開き方

```bash
code /Users/yutanakazawa/Documents/Codex/2026-10-11Yuta/new-chat/outputs/studio-u-yuta-portfolio
```

動的表示にしたので、`index.html` を直接開くのではなく、下のコマンドでサーバーを起動してください。

```bash
python3 app.py
```

ブラウザで `http://127.0.0.1:8138/` を開くと表示できます。VS Codeでは `Terminal` → `Run Task...` → `Start Studio U site` でも起動できます。

## 触るファイル

- `app.py`: 画像フォルダを読み取ってページを動的生成
- `index.html`: トップページ
- `still.html`: 静的表示用の予備ファイル
- `personal.html`: 静的表示用の予備ファイル
- `work.html`: 静的表示用の予備ファイル
- `assets/styles.css`: 余白、位置、文字サイズ
- `assets/top-still.png`: トップ画像

## 写真フォルダ

- `assets/images/still/`
- `assets/images/personal/`
- `assets/images/work/`

写真を入れたら、ブラウザを更新してください。`app.py` がフォルダ内の画像を自動で読み取ります。

## 作品タイトル

各カテゴリページでは、画像ファイル名が作品タイトルに自動反映されます。

```html
<img src="assets/images/still/blue-vase.jpg" alt="" />
```

この場合、画面には `title  blue vase` と表示されます。英字の大文字・小文字はファイル名のまま反映されます。HTMLを書き換えなくても、フォルダに画像を追加してブラウザを更新すれば反映されます。

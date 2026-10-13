# GitHub Pages + お名前.com 公開手順

## 1. GitHub に push

GitHub で新しいリポジトリを作成し、このフォルダを push します。

```bash
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

## 2. GitHub Pages を有効化

GitHub のリポジトリで:

1. Settings
2. Pages
3. Source: Deploy from a branch
4. Branch: `main`
5. Folder: `/docs`
6. Save

## 3. 独自ドメインを使う場合

ドメイン名が決まったら、以下のどちらかで `docs/CNAME` を作ります。

```bash
CUSTOM_DOMAIN=example.com python3 build_static.py
git add docs/CNAME docs
git commit -m "Add custom domain"
git push
```

または GitHub の Pages 設定画面の Custom domain に入力します。

## 4. お名前.com の DNS

ルートドメイン `example.com` を使う場合:

- A レコードを4つ追加
  - `185.199.108.153`
  - `185.199.109.153`
  - `185.199.110.153`
  - `185.199.111.153`

`www.example.com` を使う場合:

- CNAME レコードを追加
  - ホスト名: `www`
  - VALUE: `YOUR_USER.github.io`

DNS反映後、GitHub Pages の Enforce HTTPS を有効化します。

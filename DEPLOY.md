# Vercel + お名前.com 公開手順

## 1. GitHub に push

GitHub で新しいリポジトリを作成し、このフォルダを push します。

```bash
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

## 2. Vercel に接続

Vercel で新規プロジェクトを作成し、GitHub リポジトリを import します。

- Framework Preset: Other
- Build Command: `python3 build_static.py`
- Output Directory: `docs`

この2つは `vercel.json` にも入れてあるため、Vercel 側で自動反映されます。

## 3. 独自ドメインを使う場合

Vercel の Project Settings > Domains でドメインを追加します。
Vercel が表示する DNS レコードを、お名前.com の DNS 設定に追加します。

代表的な設定は以下です。

ルートドメイン `example.com` を使う場合:

- A レコード
  - ホスト名: `@`
  - VALUE: `76.76.21.21`

`www.example.com` を使う場合:

- CNAME レコードを追加
  - ホスト名: `www`
  - VALUE: `cname.vercel-dns.com`

DNS反映後、Vercel の Domains 画面で Valid になるのを確認します。

## 4. 更新方法

サイトを変更したら、commit して GitHub に push します。
Vercel は push を検知して自動で再デプロイします。

# 用語メモアプリ PostgreSQL版

PythonのGUIライブラリ `tkinter` と、PostgreSQL接続ライブラリ `psycopg` を使って作成する、学習用の用語メモアプリです。

このアプリは、SQLとデータベース操作の基礎を、実際に動くGUIアプリを作りながら理解することを目的としています。

## 作成の目的

このプロジェクトでは、次の内容を学びます。

- PythonからPostgreSQLへ接続する方法
- `psycopg` を使ったSQLの実行
- `tkinter` を使ったGUIアプリの作成
- データベースの基本操作であるCRUD
  - INSERT：データを追加する
  - SELECT：データを表示・検索する
  - UPDATE：データを修正する
  - DELETE：データを削除する
- `.env` ファイルを使った接続情報の管理
- Git / GitHub を使ったソースコード管理

## アプリの概要

用語、意味、カテゴリを登録できるメモアプリです。

主な機能は以下の通りです。

- 用語の追加
- 用語一覧の表示
- キーワード検索
- 選択した用語の修正
- 選択した用語の削除

## 使用技術

- Python
- tkinter
- PostgreSQL
- psycopg
- python-dotenv
- Git / GitHub

## データベース構成

使用するテーブル名は `terms` です。

```sql
CREATE TABLE IF NOT EXISTS terms (
    id SERIAL PRIMARY KEY,
    term TEXT NOT NULL,
    meaning TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

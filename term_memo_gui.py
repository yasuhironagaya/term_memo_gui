# coding: utf-8
import tkinter as tk
from tkinter import ttk, messagebox

import psycopg


# =====================================
# PostgreSQL 接続設定
# =====================================
DB_CONFIG = {
    "host": "localhost",
    "dbname": "sql_study",
    "user": "postgres",
    "password": "postgres",
}


# =====================================
# データベース関連
# =====================================
def get_connection():
    """
    PostgreSQLへ接続する関数
    """
    return psycopg.connect(**DB_CONFIG)


def create_table():
    """
    terms テーブルがなければ作成する
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS terms (
                    id SERIAL PRIMARY KEY,
                    term TEXT NOT NULL,
                    meaning TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)


def fetch_terms(keyword=""):
    """
    用語一覧を取得する
    keyword がある場合は、term / meaning / category を検索する
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            if keyword:
                like_keyword = f"%{keyword}%"
                cur.execute("""
                    SELECT id, term, meaning, category, created_at
                    FROM terms
                    WHERE term ILIKE %s
                       OR meaning ILIKE %s
                       OR category ILIKE %s
                    ORDER BY id;
                """, (like_keyword, like_keyword, like_keyword))
            else:
                cur.execute("""
                    SELECT id, term, meaning, category, created_at
                    FROM terms
                    ORDER BY id;
                """)

            return cur.fetchall()


def insert_term(term, meaning, category):
    """
    用語を追加する
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO terms (term, meaning, category)
                VALUES (%s, %s, %s);
            """, (term, meaning, category))


def update_term(term_id, term, meaning, category):
    """
    用語を修正する
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE terms
                SET term = %s,
                    meaning = %s,
                    category = %s
                WHERE id = %s;
            """, (term, meaning, category, term_id))


def delete_term(term_id):
    """
    用語を削除する
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM terms
                WHERE id = %s;
            """, (term_id,))


# =====================================
# GUIアプリ本体
# =====================================
class TermMemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("用語メモアプリ PostgreSQL版")
        self.root.geometry("900x600")

        self.selected_id = None

        self.create_widgets()
        self.load_terms()

    def create_widgets(self):
        """
        画面部品を作成する
        """

        # -----------------------------
        # 入力エリア
        # -----------------------------
        input_frame = ttk.LabelFrame(self.root, text="用語入力")
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="用語").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.term_entry = ttk.Entry(input_frame, width=40)
        self.term_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="カテゴリ").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.category_entry = ttk.Entry(input_frame, width=25)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="意味").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.meaning_text = tk.Text(input_frame, width=80, height=4)
        self.meaning_text.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # -----------------------------
        # ボタンエリア
        # -----------------------------
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="追加", command=self.add_term).pack(side="left", padx=5)
        ttk.Button(button_frame, text="修正", command=self.edit_term).pack(side="left", padx=5)
        ttk.Button(button_frame, text="削除", command=self.remove_term).pack(side="left", padx=5)
        ttk.Button(button_frame, text="入力クリア", command=self.clear_inputs).pack(side="left", padx=5)
        ttk.Button(button_frame, text="一覧更新", command=self.load_terms).pack(side="left", padx=5)

        # -----------------------------
        # 検索エリア
        # -----------------------------
        search_frame = ttk.LabelFrame(self.root, text="検索")
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="キーワード").pack(side="left", padx=5)

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(search_frame, text="検索", command=self.search_terms).pack(side="left", padx=5)
        ttk.Button(search_frame, text="検索クリア", command=self.clear_search).pack(side="left", padx=5)

        # -----------------------------
        # 一覧表示エリア
        # -----------------------------
        list_frame = ttk.LabelFrame(self.root, text="用語一覧")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "term", "meaning", "category", "created_at")

        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("term", text="用語")
        self.tree.heading("meaning", text="意味")
        self.tree.heading("category", text="カテゴリ")
        self.tree.heading("created_at", text="作成日時")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("term", width=150)
        self.tree.column("meaning", width=350)
        self.tree.column("category", width=120)
        self.tree.column("created_at", width=160)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_terms(self):
        """
        terms テーブルの内容を一覧表示する
        """
        self.clear_tree()

        try:
            rows = fetch_terms()

            for row in rows:
                self.tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("エラー", f"一覧の読み込みに失敗しました。\n\n{e}")

    def search_terms(self):
        """
        キーワードで検索する
        """
        keyword = self.search_entry.get().strip()

        self.clear_tree()

        try:
            rows = fetch_terms(keyword)

            for row in rows:
                self.tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("エラー", f"検索に失敗しました。\n\n{e}")

    def add_term(self):
        """
        入力された用語を追加する
        """
        term = self.term_entry.get().strip()
        category = self.category_entry.get().strip()
        meaning = self.meaning_text.get("1.0", "end").strip()

        if not term:
            messagebox.showwarning("入力確認", "用語を入力してください。")
            return

        if not meaning:
            messagebox.showwarning("入力確認", "意味を入力してください。")
            return

        try:
            insert_term(term, meaning, category)
            messagebox.showinfo("完了", "用語を追加しました。")
            self.clear_inputs()
            self.load_terms()

        except Exception as e:
            messagebox.showerror("エラー", f"追加に失敗しました。\n\n{e}")

    def edit_term(self):
        """
        選択した用語を修正する
        """
        if self.selected_id is None:
            messagebox.showwarning("選択確認", "修正する用語を一覧から選択してください。")
            return

        term = self.term_entry.get().strip()
        category = self.category_entry.get().strip()
        meaning = self.meaning_text.get("1.0", "end").strip()

        if not term:
            messagebox.showwarning("入力確認", "用語を入力してください。")
            return

        if not meaning:
            messagebox.showwarning("入力確認", "意味を入力してください。")
            return

        try:
            update_term(self.selected_id, term, meaning, category)
            messagebox.showinfo("完了", "用語を修正しました。")
            self.clear_inputs()
            self.load_terms()

        except Exception as e:
            messagebox.showerror("エラー", f"修正に失敗しました。\n\n{e}")

    def remove_term(self):
        """
        選択した用語を削除する
        """
        if self.selected_id is None:
            messagebox.showwarning("選択確認", "削除する用語を一覧から選択してください。")
            return

        result = messagebox.askyesno(
            "削除確認",
            "選択した用語を削除してもよろしいですか？"
        )

        if not result:
            return

        try:
            delete_term(self.selected_id)
            messagebox.showinfo("完了", "用語を削除しました。")
            self.clear_inputs()
            self.load_terms()

        except Exception as e:
            messagebox.showerror("エラー", f"削除に失敗しました。\n\n{e}")

    def on_select(self, event):
        """
        一覧で選択した行を入力欄に表示する
        """
        selected_items = self.tree.selection()

        if not selected_items:
            return

        item_id = selected_items[0]
        values = self.tree.item(item_id, "values")

        self.selected_id = values[0]
        term = values[1]
        meaning = values[2]
        category = values[3]

        self.term_entry.delete(0, "end")
        self.term_entry.insert(0, term)

        self.category_entry.delete(0, "end")
        self.category_entry.insert(0, category)

        self.meaning_text.delete("1.0", "end")
        self.meaning_text.insert("1.0", meaning)

    def clear_inputs(self):
        """
        入力欄をクリアする
        """
        self.selected_id = None

        self.term_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.meaning_text.delete("1.0", "end")

        self.tree.selection_remove(self.tree.selection())

    def clear_search(self):
        """
        検索欄をクリアして全件表示する
        """
        self.search_entry.delete(0, "end")
        self.load_terms()

    def clear_tree(self):
        """
        一覧表示をクリアする
        """
        for item in self.tree.get_children():
            self.tree.delete(item)


# =====================================
# 起動処理
# =====================================
if __name__ == "__main__":
    try:
        create_table()

        root = tk.Tk()
        app = TermMemoApp(root)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("起動エラー", f"アプリの起動に失敗しました。\n\n{e}")

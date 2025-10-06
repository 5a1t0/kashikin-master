import sqlite3

def check_database_content():
    """データベースから全件を取得し、問題数を表示する"""
    conn = None
    try:
        # データベースに接続
        conn = sqlite3.connect('kashikin.db')
        # 結果を辞書形式で取得できるように設定
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()

        # questionsテーブルの全レコードを取得
        cursor.execute("SELECT year, genre, question, answer FROM questions ORDER BY year DESC, genre ASC")
        questions = cursor.fetchall()

        if not questions:
            print("▶ データベースに問題は登録されていません。")
            return

        print(f"==================================================")
        print(f" データベース確認結果: 全 {len(questions)} 件 ")
        print(f"==================================================")

        # 最初の数件を詳細に表示
        for i, q in enumerate(questions):
            if i < 10:  # 例として最初の10件のみ詳細表示
                print(f"--- 問題 {i+1} ---")
                print(f"年度: {q['year']}")
                print(f"ジャンル: {q['genre']}")
                print(f"問題文（冒頭）: {q['question'][:50]}...")
                print(f"正答: {q['answer']}")
        
        if len(questions) > 10:
             print(f"\n...他 {len(questions) - 10} 件の問題が登録されています。")
        
    except sqlite3.Error as e:
        print(f"データベースエラーが発生しました: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    check_database_content()
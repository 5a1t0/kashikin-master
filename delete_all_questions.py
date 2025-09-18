import sqlite3

def delete_all_questions():
    """データベースの questions テーブルから全ての問題を削除する"""
    try:
        conn = sqlite3.connect('kashikin.db')
        cursor = conn.cursor()

        # questions テーブルのすべてのレコードを削除する
        cursor.execute("DELETE FROM questions")
        
        # データベースへの変更を確定する
        conn.commit()
        print("データベースの全ての問題を削除しました。")

    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    delete_all_questions()
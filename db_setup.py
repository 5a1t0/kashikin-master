import sqlite3
from data import quizzes

def setup_database():
    """データベースをセットアップし、既存の問題データを挿入する"""
    conn = sqlite3.connect('kashikin.db')
    cursor = conn.cursor()

    # テーブルの作成（問題ID、年度、ジャンル、問題文、正答、解説）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT NOT NULL,
            genre TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            commentary TEXT NOT NULL
        )
    ''')
    
    # 既存のデータを挿入
    # データベースにデータがなければ挿入
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    if count == 0:
        for year, genres in quizzes.items():
            for genre, question_list in genres.items():
                for q in question_list:
                    cursor.execute('''
                        INSERT INTO questions (year, genre, question, answer, commentary)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (year, genre, q['question'], q['answer'], q['commentary']))
    
    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == '__main__':
    setup_database()
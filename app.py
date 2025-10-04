from flask import Flask, render_template, request, jsonify
import sqlite3
import random

app = Flask(__name__)

# 改行コードをHTMLの<br>タグに変換するフィルタ（変更なし）
@app.template_filter('nl2br')
def nl2br(s):
    return s.replace('\n', '<br>')

def get_db_connection():
    """SQLiteデータベースに接続する"""
    conn = sqlite3.connect('kashikin.db')
    conn.row_factory = sqlite3.Row  # 辞書形式で結果を取得
    return conn

# トップページ
@app.route('/')
def index():
    conn = get_db_connection()
    # データベースから年度とジャンルのリストを取得
    years_db = conn.execute("SELECT DISTINCT year FROM questions ORDER BY year DESC").fetchall()
    genres_db = conn.execute("SELECT DISTINCT genre FROM questions ORDER BY genre ASC").fetchall()
    conn.close()

    years = [row['year'] for row in years_db]
    # 全年度選択肢を追加
    years.insert(0, "全年度")

    genres = [row['genre'] for row in genres_db]
    
    return render_template('index.html', years=years, genres=genres)

# クイズページ（変更なし）
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# クイズデータ取得API
@app.route('/api/quiz', methods=['POST'])
def get_quiz():
    data = request.json
    year = data.get('year')
    genre = data.get('genre')

    conn = get_db_connection()
    
    # SQLクエリの構築
    if year == "全年度":
        # 全年度を対象とする
        questions_db = conn.execute("SELECT * FROM questions WHERE genre = ?", (genre,)).fetchall()
    else:
        # 特定の年度とジャンルを対象とする
        questions_db = conn.execute("SELECT * FROM questions WHERE year = ? AND genre = ?", (year, genre)).fetchall()
        
    conn.close()

    selected_quizzes = []
    if questions_db:
        for q in questions_db:
            q_dict = dict(q)
            # 問題文と解説文の改行をHTMLの<br>タグに変換
            q_dict['question'] = q_dict['question'].replace('\n', '<br>')
            q_dict['commentary'] = q_dict['commentary'].replace('\n', '<br>')
            selected_quizzes.append(q_dict)

    # ランダム出題（シャッフル）
    random.shuffle(selected_quizzes)
    
    if not selected_quizzes:
        return jsonify({"error": "指定された条件に一致する問題が見つかりません。"})

    return jsonify(selected_quizzes)

if __name__ == '__main__':
    # アプリケーション起動時にデータベースをセットアップ
    from db_setup import setup_database
    setup_database()
    app.run(host='0.0.0.0', port=5000)
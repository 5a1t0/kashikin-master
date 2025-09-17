from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# 改行コードをHTMLの<br>タグに変換するフィルタ
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
    years = conn.execute("SELECT DISTINCT year FROM questions ORDER BY year DESC").fetchall()
    genres = conn.execute("SELECT DISTINCT genre FROM questions ORDER BY genre ASC").fetchall()
    conn.close()

    years = [row['year'] for row in years]
    genres = [row['genre'] for row in genres]
    
    return render_template('index.html', years=years, genres=genres)

# クイズページ
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
    questions = conn.execute("SELECT * FROM questions WHERE year = ? AND genre = ?", (year, genre)).fetchall()
    conn.close()

    selected_quizzes = []
    if questions:
        for q in questions:
            q_dict = dict(q)
            q_dict['question'] = q_dict['question'].replace('\n', '<br>')
            q_dict['commentary'] = q_dict['commentary'].replace('\n', '<br>')
            selected_quizzes.append(q_dict)
    
    if not selected_quizzes:
        return jsonify({"error": "指定された条件に一致する問題が見つかりません。"})

    return jsonify(selected_quizzes)

if __name__ == '__main__':
    # アプリケーション起動時にデータベースをセットアップ
    from db_setup import setup_database
    setup_database()
    app.run(host='0.0.0.0', port=5000)
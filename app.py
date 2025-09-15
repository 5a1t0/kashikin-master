# app.py

from flask import Flask, render_template, request, jsonify
from data import quizzes

app = Flask(__name__)

# 改行コードをHTMLの<br>タグに変換するフィルタ
@app.template_filter('nl2br')
def nl2br(s):
    return s.replace('\n', '<br>')

# トップページ
@app.route('/')
def index():
    # 年度とジャンルのリストを取得
    years = sorted(list(quizzes.keys()))
    genres = sorted(list(set(g for q in quizzes.values() for g in q)))
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

    # 年度とジャンルに基づいて問題を抽出
    selected_quizzes = []
    if year and year in quizzes:
        if genre and genre in quizzes[year]:
            # 問題文と解説文の改行をHTMLの<br>タグに変換
            for q in quizzes[year][genre]:
                q_copy = q.copy()
                q_copy['question'] = q_copy['question'].replace('\n', '<br>')
                q_copy['commentary'] = q_copy['commentary'].replace('\n', '<br>')
                selected_quizzes.append(q_copy)
    
    if not selected_quizzes:
        return jsonify({"error": "指定された条件に一致する問題が見つかりません。"})

    return jsonify(selected_quizzes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
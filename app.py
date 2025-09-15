# app.py

from flask import Flask, render_template, request, jsonify
from data import quizzes  # 問題データをインポート

app = Flask(__name__)

# トップページ
@app.route('/')
def index():
    # 年度とジャンルのリストを取得
    years = sorted(list(quizzes.keys()))
    genres = sorted(list(set(g for q in quizzes.values() for g in q)))
    return render_template('index.html', years=years, genres=genres)

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
            selected_quizzes = quizzes[year][genre]
    
    if not selected_quizzes:
        return jsonify({"error": "指定された条件に一致する問題が見つかりません。"})

    return jsonify(selected_quizzes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
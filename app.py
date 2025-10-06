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

# --- 修正後のソートキー関数 ---
def get_sort_key(year_str):
    """
    和暦の文字列からソート用のキー(年数, 元号コード)を生成する。
    「元年」を「1」に変換して数値としてソートする。
    元号コードは降順にソートするため、新しい元号ほど小さい数値を割り当てる。
    """
    # 年度表記から「年度」と「元年」を削除し、数値に変換
    clean_str = year_str.replace("年度", "").replace("元年", "1").strip()
    
    if "令和" in clean_str:
        year_num = int(clean_str.replace("令和", "").strip() or 1)
        # 令和を最も新しい元号としてコード1を割り当てる
        return (year_num, 1) 
    
    elif "平成" in clean_str:
        year_num = int(clean_str.replace("平成", "").strip() or 1)
        # 平成を令和の次に新しい元号としてコード2を割り当てる
        return (year_num, 2)
        
    else:
        # その他の元号や数値表記
        try:
            return (int(clean_str), 99)
        except ValueError:
            return (0, 99) 

# トップページ
@app.route('/')
def index():
    conn = get_db_connection()
    years_db = conn.execute("SELECT DISTINCT year FROM questions").fetchall()
    genres_db = conn.execute("SELECT DISTINCT genre FROM questions ORDER BY genre ASC").fetchall()
    conn.close()

    years = [row['year'] for row in years_db]
    
    # 🚨 カスタムソートキーを使って降順にソートする 🚨
    # key=get_sort_key: ソート基準を数値変換されたタプルにする
    # reverse=True: 年数が大きい順（新しい順）にする
    years_sorted = sorted(years, key=get_sort_key, reverse=True) 

    # '全年度'選択肢をリストの先頭に追加
    years_sorted.insert(0, "全年度")

    genres = [row['genre'] for row in genres_db]
    
    return render_template('index.html', years=years_sorted, genres=genres)

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
    
    # SQLクエリの構築
    if year == "全年度":
        questions_db = conn.execute("SELECT * FROM questions WHERE genre = ?", (genre,)).fetchall()
    else:
        questions_db = conn.execute("SELECT * FROM questions WHERE year = ? AND genre = ?", (year, genre)).fetchall()
        
    conn.close()

    selected_quizzes = []
    if questions_db:
        for q in questions_db:
            q_dict = dict(q)
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
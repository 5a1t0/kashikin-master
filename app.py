from flask import Flask, render_template, request, jsonify
import sqlite3
import random
import html

app = Flask(__name__)

# 改行コードをHTMLの<br>タグに変換するフィルタ（変更なし）
@app.template_filter('nl2br')
def nl2br(s):
    return s.replace('\n', '<br>')

def get_db_connection():
    """SQLiteデータベースに接続する"""
    import os
    # Use absolute path to ensure the correct DB file is opened regardless of current working directory
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, 'kashikin.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 辞書形式で結果を取得
    return conn

# --- 修正後のソートキー関数 ---
def get_sort_key(year_str):
    """
    和暦の文字列からソート用のキー(年数, 元号コード)を生成する。
    「元年」を「1」に変換して数値としてソートする。
    元号コードは降順にソートするため、新しい元号ほど小さい数値を割り当てる。
    """
    # 正しく降順ソートするため、和暦（元号＋年）をグレゴリオ年に変換して返す。
    # 例: 令和5年 -> 2018 + 5 = 2023, 平成30年 -> 1988 + 30 = 2018
    s = (year_str or "").replace("年度", "").replace("元年", "1").replace("年", "").strip()

    # helper: extract first integer from string
    import re
    def extract_num(text):
        m = re.search(r"(\d+)", text)
        return int(m.group(1)) if m else None

    # era base year offsets (gregorian = base + era_year)
    era_bases = {
        "令和": 2018,  # 令和1 -> 2019
        "平成": 1988,  # 平成1 -> 1989
        "昭和": 1925,  # 昭和1 -> 1926
    }

    # support shorthands like 'R5', 'Reiwa5', 'H30', 'Heisei30' (case-insensitive)
    m = re.search(r'(?i)\bre?iwa\s*(\d+)\b', year_str or '') or re.search(r'(?i)\bR\s*(\d+)\b', year_str or '')
    if m:
        num = int(m.group(1))
        return (era_bases['令和'] + num, 0)
    m = re.search(r'(?i)\bheisei\s*(\d+)\b', year_str or '') or re.search(r'(?i)\bH\s*(\d+)\b', year_str or '')
    if m:
        num = int(m.group(1))
        return (era_bases['平成'] + num, 0)
    m = re.search(r'(?i)\bshowa\s*(\d+)\b', year_str or '') or re.search(r'(?i)\bS\s*(\d+)\b', year_str or '')
    if m:
        num = int(m.group(1))
        return (era_bases['昭和'] + num, 0)

    # detect kanji era names first
    for era, base in era_bases.items():
        if era in (year_str or ''):
            num = extract_num(year_str)
            if not num:
                num = 1
            return (base + num, 0)  # 0 as era-code priority

    # fallback: if the string contains a number, treat it as a (probably western) year or year number
    num = extract_num(s)
    if num:
        # if it's small (e.g. 24, 30) we can't be sure; but return the number to allow ordering
        # assume numbers >= 1000 are full gregorian years
        if num >= 1000:
            return (num, 0)
        # treat small numbers as-is (e.g., "30年度")
        return (num, 1)

    # final fallback: put unknowns at the end
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

    # DEBUG: print years to server console to help diagnose missing options in browser
    try:
        print('DEBUG years_sorted:', years_sorted)
    except Exception:
        pass

    genres = [row['genre'] for row in genres_db]
    
    return render_template('index.html', years=years_sorted, genres=genres)

# クイズページ
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')


@app.route('/debug/years')
def debug_years():
    """Debug endpoint: return years and counts as JSON (sorted newest->oldest)."""
    conn = get_db_connection()
    rows = conn.execute("SELECT year, COUNT(*) as cnt FROM questions GROUP BY year").fetchall()
    conn.close()

    years = [r['year'] for r in rows]
    counts = {r['year']: r['cnt'] for r in rows}
    years_sorted = sorted(years, key=get_sort_key, reverse=True)
    return jsonify({
        'years_sorted': years_sorted,
        'counts': counts
    })


@app.route('/debug/info')
def debug_info():
    """Return runtime info to help debug which app file is running and available routes."""
    import os
    # list registered routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    return jsonify({
        'app_file': __file__,
        'cwd': os.getcwd(),
        'routes': sorted(routes)
    })

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
            # XSS 対策: サーバ側でまず HTML エスケープし、その後改行のみ <br> に変換して安全にレンダリング
            safe_question = html.escape(q_dict.get('question', ''))
            safe_commentary = html.escape(q_dict.get('commentary', ''))
            q_dict['question'] = safe_question.replace('\n', '<br>')
            q_dict['commentary'] = safe_commentary.replace('\n', '<br>')
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
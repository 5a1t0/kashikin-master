import sqlite3

# データベースに接続
conn = sqlite3.connect('kashikin.db')
cursor = conn.cursor()

# 令和5年度から令和元年度までの問題を取得（ID順）
years = ['令和5年度', '令和4年度', '令和3年度', '令和2年度', '令和元年度']

for year in years:
    print(f"\n{'='*50}")
    print(f"{year}")
    print(f"{'='*50}")
    
    cursor.execute("""
        SELECT answer 
        FROM questions 
        WHERE year = ? 
        ORDER BY id
    """, (year,))
    
    answers = cursor.fetchall()
    
    # 解答を1行で表示
    answer_list = [row[0] for row in answers]
    print(' '.join(answer_list))
    print(f"合計: {len(answer_list)}問")

conn.close()

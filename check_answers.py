import sqlite3

# データベースに接続
conn = sqlite3.connect('kashikin.db')
cursor = conn.cursor()

# 令和5年度から令和元年度までの問題を抽出
cursor.execute("""
    SELECT year, genre, question, answer 
    FROM questions 
    WHERE year IN ('令和5年度', '令和4年度', '令和3年度', '令和2年度', '令和元年度') 
    ORDER BY year DESC, id
""")

results = cursor.fetchall()

print("=" * 120)
print(f"{'年度':<12} {'ジャンル':<15} {'問題（抜粋）':<40} {'答え':<5}")
print("=" * 120)

for row in results:
    year = row[0]
    genre = row[1]
    question = row[2][:40].replace('\n', ' ')  # 改行を削除して40文字まで表示
    answer = row[3]
    print(f"{year:<12} {genre:<15} {question:<40} {answer:<5}")

print("=" * 120)
print(f"合計: {len(results)}問")

conn.close()

import sqlite3

conn = sqlite3.connect('kashikin.db')
cursor = conn.cursor()

# 令和5年度 第42問
cursor.execute("""
    SELECT year, question, answer 
    FROM questions 
    WHERE year = '令和5年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 41
""")
r5 = cursor.fetchone()

# 令和3年度 第26問
cursor.execute("""
    SELECT year, question, answer 
    FROM questions 
    WHERE year = '令和3年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 25
""")
r3 = cursor.fetchone()

print("=" * 80)
print("令和5年度 第42問")
print("=" * 80)
print(f"問題: {r5[1][:100]}...")
print(f"解答: {r5[2]}")

print("\n" + "=" * 80)
print("令和3年度 第26問")
print("=" * 80)
print(f"問題: {r3[1][:100]}...")
print(f"解答: {r3[2]}")

conn.close()

import sqlite3

conn = sqlite3.connect('kashikin.db')
cursor = conn.cursor()

# 修正前の確認
cursor.execute("""
    SELECT id, year, question, answer 
    FROM questions 
    WHERE year = '令和5年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 41
""")
result = cursor.fetchone()
print(f"修正前:")
print(f"令和5年度 第42問")
print(f"問題: {result[2][:80]}...")
print(f"現在の解答: {result[3]}")

# 修正実行
cursor.execute("""
    UPDATE questions 
    SET answer = '④' 
    WHERE year = '令和5年度' 
    AND id = (
        SELECT id FROM questions 
        WHERE year = '令和5年度' 
        ORDER BY id 
        LIMIT 1 OFFSET 41
    )
""")

conn.commit()
print(f"\n✅ 令和5年度 第42問: {result[3]} → ④ に修正しました")

# 修正後の確認
cursor.execute("""
    SELECT answer 
    FROM questions 
    WHERE year = '令和5年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 41
""")
result = cursor.fetchone()
print(f"\n修正後の解答: {result[0]}")

conn.close()

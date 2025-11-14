import sqlite3

# データベースに接続
conn = sqlite3.connect('kashikin.db')
cursor = conn.cursor()

# 修正前の確認
print("=== 修正前の確認 ===")

# 令和5年度 第45問
cursor.execute("""
    SELECT id, year, question, answer 
    FROM questions 
    WHERE year = '令和5年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 44
""")
result = cursor.fetchone()
print(f"\n令和5年度 第45問:")
print(f"ID: {result[0]}")
print(f"問題: {result[2][:50]}...")
print(f"現在の解答: {result[3]}")

# 令和3年度 第26問
cursor.execute("""
    SELECT id, year, question, answer 
    FROM questions 
    WHERE year = '令和3年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 25
""")
result = cursor.fetchone()
print(f"\n令和3年度 第26問:")
print(f"ID: {result[0]}")
print(f"問題: {result[2][:50]}...")
print(f"現在の解答: {result[3]}")

# 修正実行
print("\n\n=== 修正実行 ===")

# 令和5年度 第45問を④に修正
cursor.execute("""
    UPDATE questions 
    SET answer = '④' 
    WHERE year = '令和5年度' 
    AND id = (
        SELECT id FROM questions 
        WHERE year = '令和5年度' 
        ORDER BY id 
        LIMIT 1 OFFSET 44
    )
""")
print("✅ 令和5年度 第45問: ③ → ④ に修正しました")

# 令和3年度 第26問を①に修正
cursor.execute("""
    UPDATE questions 
    SET answer = '①' 
    WHERE year = '令和3年度' 
    AND id = (
        SELECT id FROM questions 
        WHERE year = '令和3年度' 
        ORDER BY id 
        LIMIT 1 OFFSET 25
    )
""")
print("✅ 令和3年度 第26問: ③ → ① に修正しました")

# 変更を確定
conn.commit()

# 修正後の確認
print("\n\n=== 修正後の確認 ===")

# 令和5年度 第45問
cursor.execute("""
    SELECT id, year, question, answer 
    FROM questions 
    WHERE year = '令和5年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 44
""")
result = cursor.fetchone()
print(f"\n令和5年度 第45問:")
print(f"修正後の解答: {result[3]}")

# 令和3年度 第26問
cursor.execute("""
    SELECT id, year, question, answer 
    FROM questions 
    WHERE year = '令和3年度' 
    ORDER BY id 
    LIMIT 1 OFFSET 25
""")
result = cursor.fetchone()
print(f"\n令和3年度 第26問:")
print(f"修正後の解答: {result[3]}")

conn.close()
print("\n\n✅ 修正完了しました！")

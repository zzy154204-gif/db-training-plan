"""
培养方案数据库系统 — 初始化与数据导入脚本

用法:
  1. 先确保 PostgreSQL 已安装并启动
  2. 运行: python init_db.py
"""

import psycopg2
import csv
import os
from getpass import getpass

# ========== 配置 ==========
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "training_plan",
    "user": "postgres",
    # 会在运行时提示输入密码
}

CSV_PATH = r"C:\Users\张宗元\db-project\data\processed\courses.csv"

# ========== SQL ==========

CREATE_TABLES_SQL = """
-- 学院表
CREATE TABLE IF NOT EXISTS college (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 专业表
CREATE TABLE IF NOT EXISTS major (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    college_id INTEGER NOT NULL REFERENCES college(id),
    total_credits INTEGER DEFAULT 0,
    UNIQUE(name, college_id)
);

-- 课程表
CREATE TABLE IF NOT EXISTS course (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    credits DECIMAL(4,1) NOT NULL,
    type VARCHAR(20) DEFAULT '必修',
    UNIQUE(code, name)
);

-- 专业-课程关联表（多对多）
CREATE TABLE IF NOT EXISTS major_course (
    id SERIAL PRIMARY KEY,
    major_id INTEGER NOT NULL REFERENCES major(id),
    course_id INTEGER NOT NULL REFERENCES course(id),
    semester INTEGER DEFAULT 0,
    UNIQUE(major_id, course_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_course_code ON course(code);
CREATE INDEX IF NOT EXISTS idx_course_name ON course(name);
CREATE INDEX IF NOT EXISTS idx_major_name ON major(name);
CREATE INDEX IF NOT EXISTS idx_major_course_major ON major_course(major_id);
CREATE INDEX IF NOT EXISTS idx_major_course_course ON major_course(course_id);
"""

# ========== 示例查询 SQL ==========

EXAMPLE_QUERIES = """
-- 1. 查询某专业的必修课列表（以金融学类为例）
SELECT c.name, c.credits, c.type
FROM course c
JOIN major_course mc ON c.id = mc.course_id
JOIN major m ON mc.major_id = m.id
WHERE m.name = '金融学类' AND c.type = '必修'
ORDER BY mc.semester;

-- 2. 查询某门课程的学分、学时信息
SELECT c.name, c.credits, c.code
FROM course c
WHERE c.name LIKE '%高等数学%';

-- 3. 查询某专业的总学分要求
SELECT m.name, SUM(c.credits) as total_credits
FROM major m
JOIN major_course mc ON m.id = mc.major_id
JOIN course c ON mc.course_id = c.id
WHERE m.name = '金融学类'
GROUP BY m.name;

-- 4. 查询开设某门课程的所有专业
SELECT DISTINCT m.name as major, col.name as college
FROM course c
JOIN major_course mc ON c.id = mc.course_id
JOIN major m ON mc.major_id = m.id
JOIN college col ON m.college_id = col.id
WHERE c.name LIKE '%概率论%';

-- 5. 查询某学院下所有专业的培养方案概览
SELECT m.name as major, COUNT(DISTINCT c.id) as course_count,
       SUM(c.credits) as total_credits
FROM major m
JOIN major_course mc ON m.id = mc.major_id
JOIN course c ON mc.course_id = c.id
WHERE m.college_id = (SELECT id FROM college WHERE name = '金融学院')
GROUP BY m.name;

-- 6. 关键词模糊搜索课程
SELECT DISTINCT c.code, c.name, c.credits, c.type,
       m.name as major, col.name as college
FROM course c
JOIN major_course mc ON c.id = mc.course_id
JOIN major m ON mc.major_id = m.id
JOIN college col ON m.college_id = col.id
WHERE c.name LIKE '%数据%'
ORDER BY c.name;
"""


def import_data(conn):
    """从 CSV 导入课程数据"""
    cur = conn.cursor()

    # 清空旧数据
    cur.execute("DELETE FROM major_course")
    cur.execute("DELETE FROM major")
    cur.execute("DELETE FROM course")
    cur.execute("DELETE FROM college")

    # 读取 CSV
    courses = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            courses.append(row)

    print(f"读取到 {len(courses)} 条课程记录")

    # 导入学院
    colleges = set()
    for c in courses:
        colleges.add(c["college"])
    for col_name in colleges:
        cur.execute("INSERT INTO college (name) VALUES (%s) ON CONFLICT DO NOTHING", (col_name,))
    print(f"导入 {len(colleges)} 个学院")

    # 导入专业
    majors = {}
    for c in courses:
        key = (c["college"], c["major"])
        if key not in majors:
            cur.execute("""
                INSERT INTO major (name, college_id)
                VALUES (%s, (SELECT id FROM college WHERE name = %s))
                ON CONFLICT (name, college_id) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """, (c["major"], c["college"]))
            majors[key] = cur.fetchone()[0]
    print(f"导入 {len(majors)} 个专业")

    # 导入课程
    course_map = {}  # (code, name) -> id
    count = 0
    for c in courses:
        key = (c["course_code"], c["course_name"])
        if key not in course_map:
            try:
                cur.execute("""
                    INSERT INTO course (code, name, credits, type)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (code, name) DO UPDATE SET credits = EXCLUDED.credits
                    RETURNING id
                """, (c["course_code"], c["course_name"], float(c["credits"]), c["type"]))
                course_map[key] = cur.fetchone()[0]
                count += 1
            except Exception as e:
                print(f"  跳过课程 {key}: {e}")

    print(f"导入 {count} 门课程")

    # 导入专业-课程关联
    rel_count = 0
    for c in courses:
        major_key = (c["college"], c["major"])
        course_key = (c["course_code"], c["course_name"])
        if major_key in majors and course_key in course_map:
            semester = int(c.get("semester", 0) or 0)
            try:
                cur.execute("""
                    INSERT INTO major_course (major_id, course_id, semester)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (majors[major_key], course_map[course_key], semester))
                rel_count += 1
            except Exception as e:
                pass

    print(f"导入 {rel_count} 条专业-课程关联")

    conn.commit()
    print("数据导入完成！")


def verify_data(conn):
    """验证数据"""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM college")
    print(f"\n学院数: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM major")
    print(f"专业数: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM course")
    print(f"课程数: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM major_course")
    print(f"关联数: {cur.fetchone()[0]}")

    print("\n=== 学院及专业列表 ===")
    cur.execute("""
        SELECT col.name, m.name, COUNT(mc.id) as courses
        FROM college col
        JOIN major m ON m.college_id = col.id
        LEFT JOIN major_course mc ON mc.major_id = m.id
        GROUP BY col.name, m.name
        ORDER BY col.name, m.name
    """)
    for row in cur.fetchall():
        print(f"  {row[0]} | {row[1]} ({row[2]} 门课程)")


def main():
    print("=== 培养方案数据库系统 - 初始化 ===\n")

    # 获取数据库密码
    password = os.environ.get("PGPASSWORD")
    if not password:
        password = getpass("请输入 PostgreSQL 密码 (postgres 用户): ")

    if not password.strip():
        print("\n[提示] 如果 PostgreSQL 未设置密码或使用其他认证方式，")
        print("请修改 DB_CONFIG 中的配置。\n")

    DB_CONFIG["password"] = password

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()

        print("连接数据库成功！")

        # 创建表
        print("\n创建表...")
        cur.execute(CREATE_TABLES_SQL)
        print("表创建完成！")

        # 导入数据
        print("\n导入数据...")
        import_data(conn)

        # 验证
        print("\n验证数据...")
        verify_data(conn)

        # 打印示例查询
        print("\n=== 示例查询 SQL ===")
        print("以下 SQL 可在 psql 或 pgAdmin 中运行：")
        print(EXAMPLE_QUERIES)

        cur.close()
        conn.close()
        print("\n初始化完成！")

    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保:")
        print("  1. PostgreSQL 已安装并启动")
        print("  2. 已创建 training_plan 数据库: 在 psql 中运行 CREATE DATABASE training_plan;")
        print("  3. 密码正确")
        print("\nWindows 上启动 PostgreSQL:")
        print("  pg_ctl start -D \"C:\\Program Files\\PostgreSQL\\16\\data\"")
        print("  或搜索 '服务' -> 找到 PostgreSQL 服务 -> 启动")


if __name__ == "__main__":
    main()

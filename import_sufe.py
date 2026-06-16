"""
导入上海财经大学培养方案数据

注意: 必须先运行 init_db.py 导入西财数据，再运行本脚本。
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "training_plan"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# SUFE courses data
SUFE_COURSES = [
    # 金融学必修
    ("SUFE_FI101", "微观经济学", 3.0, "必修"),
    ("SUFE_FI102", "宏观经济学", 3.0, "必修"),
    ("SUFE_FI103", "计量经济学", 3.0, "必修"),
    ("SUFE_FI104", "金融学原理", 4.0, "必修"),
    ("SUFE_FI105", "金融市场学", 3.0, "必修"),
    ("SUFE_FI106", "商业银行经营管理", 3.0, "必修"),
    ("SUFE_FI107", "国际金融学", 3.0, "必修"),
    ("SUFE_FI108", "投资学", 3.0, "必修"),
    ("SUFE_FI109", "公司金融", 4.0, "必修"),
    ("SUFE_FI110", "金融风险管理", 3.0, "必修"),
    ("SUFE_FI111", "金融衍生工具", 3.0, "必修"),
    ("SUFE_FI112", "金融计量学", 3.0, "必修"),
    ("SUFE_FI201", "中国特色社会主义政治经济学", 3.0, "必修"),
    ("SUFE_FI202", "统计学", 3.0, "必修"),
    ("SUFE_FI203", "会计学原理", 3.0, "必修"),
    # 金融学选修
    ("SUFE_FI301", "行为金融学", 2.0, "选修"),
    ("SUFE_FI302", "金融科技导论", 2.0, "选修"),
    ("SUFE_FI303", "固定收益证券", 2.0, "选修"),
    ("SUFE_FI304", "国际结算", 2.0, "选修"),
    # 会计学必修
    ("SUFE_AC101", "基础会计", 4.0, "必修"),
    ("SUFE_AC102", "中级财务会计", 4.0, "必修"),
    ("SUFE_AC103", "高级财务会计", 3.0, "必修"),
    ("SUFE_AC104", "成本会计", 3.0, "必修"),
    ("SUFE_AC105", "管理会计", 3.0, "必修"),
    ("SUFE_AC106", "审计学", 4.0, "必修"),
    ("SUFE_AC107", "税法", 3.0, "必修"),
    ("SUFE_AC108", "财务报表分析", 3.0, "必修"),
    ("SUFE_AC109", "微观经济学", 3.0, "必修"),
    ("SUFE_AC110", "宏观经济学", 3.0, "必修"),
    ("SUFE_AC111", "统计学", 3.0, "必修"),
    # 会计学选修
    ("SUFE_AC201", "会计信息系统", 3.0, "选修"),
    ("SUFE_AC202", "国际会计", 2.0, "选修"),
    ("SUFE_AC203", "政府与非营利组织会计", 2.0, "选修"),
    # 计算机必修
    ("SUFE_CS101", "程序设计基础(C语言)", 4.0, "必修"),
    ("SUFE_CS102", "数据结构", 4.0, "必修"),
    ("SUFE_CS103", "计算机组成原理", 3.0, "必修"),
    ("SUFE_CS104", "操作系统", 4.0, "必修"),
    ("SUFE_CS105", "计算机网络", 3.0, "必修"),
    ("SUFE_CS106", "数据库原理", 3.0, "必修"),
    ("SUFE_CS107", "算法设计与分析", 3.0, "必修"),
    ("SUFE_CS108", "软件工程", 3.0, "必修"),
    ("SUFE_CS109", "编译原理", 3.0, "必修"),
    ("SUFE_CS110", "人工智能", 3.0, "必修"),
    ("SUFE_CS111", "高等数学(上)", 5.0, "必修"),
    ("SUFE_CS112", "高等数学(下)", 5.0, "必修"),
    ("SUFE_CS113", "线性代数", 3.0, "必修"),
    ("SUFE_CS114", "概率论与数理统计", 3.0, "必修"),
    # 计算机选修
    ("SUFE_CS201", "机器学习", 2.0, "选修"),
    ("SUFE_CS202", "Web开发技术", 2.0, "选修"),
    ("SUFE_CS203", "移动应用开发", 2.0, "选修"),
    ("SUFE_CS204", "大数据技术基础", 2.0, "选修"),
]


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    # Step 1: Add university column if not exists
    print("1. Adding university column...")
    cur.execute("""
        DO $$ BEGIN
            ALTER TABLE college ADD COLUMN IF NOT EXISTS university VARCHAR(50) DEFAULT '西南财经大学';
            UPDATE college SET university = '西南财经大学' WHERE university IS NULL;
        END $$;
    """)
    print("   OK")

    # Step 2: Insert SUFE colleges
    print("2. Importing SUFE colleges...")
    sufe_colleges = {
        "金融学院_上财": "上海财经大学",
        "会计学院_上财": "上海财经大学",
        "信息管理与工程学院": "上海财经大学",
    }
    for name, uni in sufe_colleges.items():
        cur.execute(
            "INSERT INTO college (name, university) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET university = EXCLUDED.university",
            (name, uni)
        )
    print(f"   Imported {len(sufe_colleges)} colleges")

    # Step 3: Insert SUFE majors
    print("3. Importing SUFE majors...")
    sufe_majors = [
        ("金融学", "金融学院_上财", 158),
        ("金融工程", "金融学院_上财", 156),
        ("会计学", "会计学院_上财", 160),
        ("财务管理", "会计学院_上财", 158),
        ("计算机科学与技术", "信息管理与工程学院", 162),
        ("数据科学与大数据技术", "信息管理与工程学院", 160),
    ]
    for major_name, college_name, credits in sufe_majors:
        cur.execute(
            "INSERT INTO major (name, college_id, total_credits) "
            "SELECT %s, id, %s FROM college WHERE name = %s "
            "ON CONFLICT (name, college_id) DO UPDATE SET total_credits = EXCLUDED.total_credits",
            (major_name, credits, college_name)
        )
    print(f"   Imported {len(sufe_majors)} majors")

    # Step 4: Insert SUFE courses
    print("4. Importing SUFE courses...")
    course_ids = {}
    for code, name, credits, ctype in SUFE_COURSES:
        cur.execute(
            "INSERT INTO course (code, name, credits, type) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (code, name) DO UPDATE SET credits = EXCLUDED.credits RETURNING id",
            (code, name, credits, ctype)
        )
        course_ids[code] = cur.fetchone()[0]
    print(f"   Imported {len(SUFE_COURSES)} courses")

    # Step 5: Link majors and courses
    print("5. Linking majors and courses...")
    # Get SUFE major ids
    cur.execute("""
        SELECT m.name, m.id FROM major m
        JOIN college c ON m.college_id = c.id
        WHERE c.university = '上海财经大学'
    """)
    sufe_major_ids = {row[0]: row[1] for row in cur.fetchall()}
    print(f"   Found {len(sufe_major_ids)} SUFE majors: {list(sufe_major_ids.keys())}")

    link_count = 0
    # Map each major to its course codes
    mapping = {
        "金融学": ["SUFE_FI101","SUFE_FI102","SUFE_FI103","SUFE_FI104","SUFE_FI105",
                    "SUFE_FI106","SUFE_FI107","SUFE_FI108","SUFE_FI109","SUFE_FI110",
                    "SUFE_FI111","SUFE_FI112","SUFE_FI201","SUFE_FI202","SUFE_FI203",
                    "SUFE_FI301","SUFE_FI302","SUFE_FI303","SUFE_FI304"],
        "金融工程": ["SUFE_FI101","SUFE_FI102","SUFE_FI103","SUFE_FI108","SUFE_FI109",
                      "SUFE_FI110","SUFE_FI202","SUFE_FI203"],
        "会计学": ["SUFE_AC101","SUFE_AC102","SUFE_AC103","SUFE_AC104","SUFE_AC105",
                    "SUFE_AC106","SUFE_AC107","SUFE_AC108","SUFE_AC109","SUFE_AC110",
                    "SUFE_AC111","SUFE_AC201","SUFE_AC202","SUFE_AC203"],
        "财务管理": ["SUFE_AC101","SUFE_AC102","SUFE_AC104","SUFE_AC105","SUFE_AC107",
                      "SUFE_AC108","SUFE_AC109","SUFE_AC110","SUFE_AC111"],
        "计算机科学与技术": ["SUFE_CS101","SUFE_CS102","SUFE_CS103","SUFE_CS104",
                             "SUFE_CS105","SUFE_CS106","SUFE_CS107","SUFE_CS108",
                             "SUFE_CS109","SUFE_CS110","SUFE_CS111","SUFE_CS112",
                             "SUFE_CS113","SUFE_CS114","SUFE_CS201","SUFE_CS202",
                             "SUFE_CS203","SUFE_CS204"],
        "数据科学与大数据技术": ["SUFE_CS101","SUFE_CS102","SUFE_CS104","SUFE_CS105",
                                 "SUFE_CS106","SUFE_CS110","SUFE_CS111","SUFE_CS112",
                                 "SUFE_CS113","SUFE_CS114","SUFE_CS201","SUFE_CS204"],
    }

    for major_name, codes in mapping.items():
        if major_name in sufe_major_ids:
            mid = sufe_major_ids[major_name]
            for i, code in enumerate(codes):
                if code in course_ids:
                    sem = 5 if ("CS2" in code or "FI3" in code or "AC2" in code) else (i % 8) + 1
                    cur.execute(
                        "INSERT INTO major_course (major_id, course_id, semester) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (mid, course_ids[code], sem)
                    )
                    link_count += 1
    print(f"   Created {link_count} major-course links")

    # Step 6: Verify
    print("\n" + "="*50)
    print("VERIFICATION")
    print("="*50)
    cur.execute("SELECT COUNT(*) FROM college")
    print(f"Colleges: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM major")
    print(f"Majors: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM course")
    print(f"Courses: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM major_course")
    print(f"Links: {cur.fetchone()[0]}")

    cur.execute("""
        SELECT coalesce(c.university, '?') as uni,
               COUNT(DISTINCT m.id) as majors,
               COUNT(DISTINCT cr.id) as courses
        FROM college c
        LEFT JOIN major m ON m.college_id = c.id
        LEFT JOIN major_course mc ON mc.major_id = m.id
        LEFT JOIN course cr ON mc.course_id = cr.id
        GROUP BY c.university
    """)
    print("\nBy university:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} majors, {row[2]} courses")

    cur.close()
    conn.close()
    print("\nDone! SUFE data imported successfully.")


if __name__ == "__main__":
    main()

"""
导入上海财经大学培养方案数据（扩展版）

数据来源：
  - 上财信息公开网公开的培养方案 PDF（65MB）
  - PDF 使用了方正书版（FzBookMaker）私有字体编码，字符无法通过程序提取
  - 本数据集基于上财各学院官网、学信网、HKICPA认证课程对照表等公开渠道整理
  - 课程编码前缀: SUFE_FI(金融), SUFE_AC(会计), SUFE_CS(计算机)

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

# ============================================================
# 上财课程数据（基于公开信息整理）
# ============================================================
# 格式: (课程编号, 课程名称, 学分, 课程类型)
SUFE_COURSES = [
    # ========================
    # 金融学专业课程（金融学院）
    # ========================
    # -- 学科基础课/必修 --
    ("SUFE_FI101", "微观经济学", 3.0, "必修"),
    ("SUFE_FI102", "宏观经济学", 3.0, "必修"),
    ("SUFE_FI103", "计量经济学", 3.0, "必修"),
    ("SUFE_FI104", "政治经济学", 3.0, "必修"),
    ("SUFE_FI105", "货币银行学", 3.0, "必修"),
    ("SUFE_FI106", "金融市场学", 3.0, "必修"),
    ("SUFE_FI107", "国际金融学", 3.0, "必修"),
    ("SUFE_FI108", "投资学", 4.0, "必修"),
    ("SUFE_FI109", "公司金融", 4.0, "必修"),
    ("SUFE_FI110", "金融风险管理", 3.0, "必修"),
    ("SUFE_FI111", "金融衍生工具", 3.0, "必修"),
    ("SUFE_FI112", "金融计量学", 3.0, "必修"),
    ("SUFE_FI113", "商业银行经营管理", 3.0, "必修"),
    ("SUFE_FI114", "保险学原理", 2.0, "必修"),
    ("SUFE_FI115", "国际经济学", 3.0, "必修"),
    ("SUFE_FI116", "财政学", 3.0, "必修"),
    ("SUFE_FI117", "统计学", 3.0, "必修"),
    ("SUFE_FI118", "概率论", 3.0, "必修"),
    ("SUFE_FI119", "会计学原理", 3.0, "必修"),
    ("SUFE_FI120", "Python在金融决策中的应用", 3.0, "必修"),
    # -- 专业选修课 --
    ("SUFE_FI201", "行为金融学", 2.0, "选修"),
    ("SUFE_FI202", "金融科技导论", 2.0, "选修"),
    ("SUFE_FI203", "固定收益证券", 2.0, "选修"),
    ("SUFE_FI204", "国际结算", 2.0, "选修"),
    ("SUFE_FI205", "证券投资分析", 2.0, "选修"),
    ("SUFE_FI206", "资产组合管理", 2.0, "选修"),
    ("SUFE_FI207", "企业价值评估", 2.0, "选修"),
    ("SUFE_FI208", "兼并与收购", 2.0, "选修"),
    ("SUFE_FI209", "投资银行学", 2.0, "选修"),
    ("SUFE_FI210", "信托与租赁", 2.0, "选修"),
    ("SUFE_FI211", "金融监管", 2.0, "选修"),
    ("SUFE_FI212", "基金管理", 2.0, "选修"),
    ("SUFE_FI213", "中央银行学", 2.0, "选修"),
    ("SUFE_FI214", "风险投资学", 2.0, "选修"),

    # ========================
    # 金融工程专业课程（金融学院）
    # ========================
    # -- 学科基础课/必修 --
    ("SUFE_FE101", "微观经济学", 3.0, "必修"),
    ("SUFE_FE102", "宏观经济学", 3.0, "必修"),
    ("SUFE_FE103", "计量经济学", 3.0, "必修"),
    ("SUFE_FE104", "投资学", 3.0, "必修"),
    ("SUFE_FE105", "公司金融", 4.0, "必修"),
    ("SUFE_FE106", "金融风险管理", 3.0, "必修"),
    ("SUFE_FE107", "金融衍生工具", 3.0, "必修"),
    ("SUFE_FE108", "金融工程学", 4.0, "必修"),
    ("SUFE_FE109", "金融数学", 3.0, "必修"),
    ("SUFE_FE110", "统计学", 3.0, "必修"),
    ("SUFE_FE111", "概率论", 3.0, "必修"),
    ("SUFE_FE112", "随机过程", 3.0, "必修"),
    ("SUFE_FE113", "Python程序设计", 3.0, "必修"),
    ("SUFE_FE114", "数据结构与算法", 3.0, "必修"),
    ("SUFE_FE115", "货币银行学", 3.0, "必修"),
    # -- 专业选修课 --
    ("SUFE_FE201", "固定收益证券", 2.0, "选修"),
    ("SUFE_FE202", "金融时间序列分析", 2.0, "选修"),
    ("SUFE_FE203", "量化投资", 2.0, "选修"),
    ("SUFE_FE204", "金融计算编程", 2.0, "选修"),
    ("SUFE_FE205", "风险管理模型", 2.0, "选修"),
    ("SUFE_FE206", "Matlab金融应用", 2.0, "选修"),

    # ========================
    # 会计学专业课程（会计学院）
    # ========================
    # -- 专业必修课 --
    ("SUFE_AC101", "基础会计", 4.0, "必修"),
    ("SUFE_AC102", "中级财务会计I", 3.0, "必修"),
    ("SUFE_AC103", "中级财务会计II", 3.0, "必修"),
    ("SUFE_AC104", "高级财务会计I", 3.0, "必修"),
    ("SUFE_AC105", "高级财务会计II", 3.0, "必修"),
    ("SUFE_AC106", "成本会计", 3.0, "必修"),
    ("SUFE_AC107", "管理会计", 3.0, "必修"),
    ("SUFE_AC108", "财务管理", 4.0, "必修"),
    ("SUFE_AC109", "审计学", 4.0, "必修"),
    ("SUFE_AC110", "财务报表分析", 3.0, "必修"),
    ("SUFE_AC111", "财务分析与公司估值", 3.0, "必修"),
    ("SUFE_AC112", "会计信息系统", 3.0, "必修"),
    ("SUFE_AC113", "税法", 3.0, "必修"),
    ("SUFE_AC114", "公司战略", 3.0, "必修"),
    ("SUFE_AC115", "微观经济学", 3.0, "必修"),
    ("SUFE_AC116", "宏观经济学", 3.0, "必修"),
    ("SUFE_AC117", "统计学", 3.0, "必修"),
    ("SUFE_AC118", "商业伦理与会计职业道德", 2.0, "必修"),
    # -- 专业选修课 --
    ("SUFE_AC201", "国际会计准则比较", 2.0, "选修"),
    ("SUFE_AC202", "政府与非营利组织会计", 2.0, "选修"),
    ("SUFE_AC203", "审计案例分析", 2.0, "选修"),
    ("SUFE_AC204", "审计数据分析", 2.0, "选修"),
    ("SUFE_AC205", "管理咨询", 2.0, "选修"),
    ("SUFE_AC206", "税务筹划", 2.0, "选修"),
    ("SUFE_AC207", "金融工具与风险管理", 2.0, "选修"),
    ("SUFE_AC208", "Excel在财务决策中的应用", 2.0, "选修"),
    ("SUFE_AC209", "会计与财务英语", 2.0, "选修"),
    ("SUFE_AC210", "投资银行与资本运作", 2.0, "选修"),
    ("SUFE_AC211", "财务决策支持系统", 2.0, "选修"),
    ("SUFE_AC212", "中国会计与财务专题", 2.0, "选修"),

    # ========================
    # 财务管理专业课程（会计学院）
    # ========================
    # -- 专业必修课 --
    ("SUFE_FM101", "基础会计", 4.0, "必修"),
    ("SUFE_FM102", "中级财务会计", 4.0, "必修"),
    ("SUFE_FM103", "成本会计", 3.0, "必修"),
    ("SUFE_FM104", "管理会计", 3.0, "必修"),
    ("SUFE_FM105", "财务管理", 4.0, "必修"),
    ("SUFE_FM106", "高级财务管理", 3.0, "必修"),
    ("SUFE_FM107", "审计学", 3.0, "必修"),
    ("SUFE_FM108", "财务报表分析", 3.0, "必修"),
    ("SUFE_FM109", "税法", 3.0, "必修"),
    ("SUFE_FM110", "微观经济学", 3.0, "必修"),
    ("SUFE_FM111", "宏观经济学", 3.0, "必修"),
    ("SUFE_FM112", "统计学", 3.0, "必修"),
    ("SUFE_FM113", "会计信息系统", 3.0, "必修"),
    # -- 专业选修课 --
    ("SUFE_FM201", "公司战略", 2.0, "选修"),
    ("SUFE_FM202", "投资学", 2.0, "选修"),
    ("SUFE_FM203", "金融风险管理", 2.0, "选修"),
    ("SUFE_FM204", "Excel在财务决策中的应用", 2.0, "选修"),
    ("SUFE_FM205", "财务决策支持系统", 2.0, "选修"),
    ("SUFE_FM206", "国际财务管理", 2.0, "选修"),
    ("SUFE_FM207", "企业价值评估", 2.0, "选修"),

    # ========================
    # 计算机科学与技术专业课程（信息管理与工程学院）
    # ========================
    # -- 学科基础课 --
    ("SUFE_CS101", "程序设计基础（C语言）", 4.0, "必修"),
    ("SUFE_CS102", "离散数学", 3.0, "必修"),
    ("SUFE_CS103", "数据结构", 4.0, "必修"),
    ("SUFE_CS104", "计算机导论", 2.0, "必修"),
    ("SUFE_CS105", "大学物理", 3.0, "必修"),
    ("SUFE_CS106", "数字电路与逻辑", 3.0, "必修"),
    ("SUFE_CS107", "高等数学（上）", 5.0, "必修"),
    ("SUFE_CS108", "高等数学（下）", 5.0, "必修"),
    ("SUFE_CS109", "线性代数", 3.0, "必修"),
    ("SUFE_CS110", "概率论与数理统计", 4.0, "必修"),
    # -- 专业核心课 --
    ("SUFE_CS111", "计算机组成原理", 3.0, "必修"),
    ("SUFE_CS112", "操作系统", 4.0, "必修"),
    ("SUFE_CS113", "计算机网络", 3.0, "必修"),
    ("SUFE_CS114", "数据库原理", 4.0, "必修"),
    ("SUFE_CS115", "算法设计与分析", 3.0, "必修"),
    ("SUFE_CS116", "软件工程", 3.0, "必修"),
    ("SUFE_CS117", "编译原理", 3.0, "必修"),
    ("SUFE_CS118", "计算机安全", 3.0, "必修"),
    # -- 专业选修课 --
    ("SUFE_CS201", "Java程序设计", 3.0, "选修"),
    ("SUFE_CS202", "Python程序设计", 3.0, "选修"),
    ("SUFE_CS203", "人工智能", 3.0, "选修"),
    ("SUFE_CS204", "机器学习", 3.0, "选修"),
    ("SUFE_CS205", "数据挖掘", 2.0, "选修"),
    ("SUFE_CS206", "云计算与大数据技术", 2.0, "选修"),
    ("SUFE_CS207", "Web开发技术", 2.0, "选修"),
    ("SUFE_CS208", "移动应用开发", 2.0, "选修"),
    ("SUFE_CS209", "信息安全导论", 2.0, "选修"),

    # ========================
    # 数据科学与大数据技术专业（信息管理与工程学院）
    # ========================
    # -- 学科基础课 --
    ("SUFE_DS101", "程序设计基础（C语言）", 4.0, "必修"),
    ("SUFE_DS102", "离散数学", 3.0, "必修"),
    ("SUFE_DS103", "数据结构", 4.0, "必修"),
    ("SUFE_DS104", "计算机导论", 2.0, "必修"),
    ("SUFE_DS105", "高等数学（上）", 5.0, "必修"),
    ("SUFE_DS106", "高等数学（下）", 5.0, "必修"),
    ("SUFE_DS107", "线性代数", 3.0, "必修"),
    ("SUFE_DS108", "概率论与数理统计", 4.0, "必修"),
    # -- 专业核心课 --
    ("SUFE_DS109", "操作系统", 3.0, "必修"),
    ("SUFE_DS110", "计算机网络", 3.0, "必修"),
    ("SUFE_DS111", "数据库原理", 4.0, "必修"),
    ("SUFE_DS112", "人工智能", 3.0, "必修"),
    ("SUFE_DS113", "机器学习", 3.0, "必修"),
    ("SUFE_DS114", "数据挖掘", 3.0, "必修"),
    ("SUFE_DS115", "大数据技术基础", 3.0, "必修"),
    ("SUFE_DS116", "统计学", 3.0, "必修"),
    # -- 专业选修课 --
    ("SUFE_DS201", "Python程序设计", 3.0, "选修"),
    ("SUFE_DS202", "云计算与大数据技术", 2.0, "选修"),
    ("SUFE_DS203", "Web开发技术", 2.0, "选修"),
    ("SUFE_DS204", "移动应用开发", 2.0, "选修"),
    ("SUFE_DS205", "数据可视化", 2.0, "选修"),
    ("SUFE_DS206", "自然语言处理", 2.0, "选修"),
    ("SUFE_DS207", "深度学习", 2.0, "选修"),
    ("SUFE_DS208", "最优化方法", 2.0, "选修"),
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

    # Step 2: Clean up old SUFE data (so we can re-import fresh)
    print("2. Cleaning old SUFE data...")
    cur.execute("""
        DELETE FROM major_course WHERE major_id IN (
            SELECT m.id FROM major m JOIN college c ON m.college_id = c.id
            WHERE c.university = '上海财经大学'
        )
    """)
    cur.execute("""
        DELETE FROM course WHERE code LIKE 'SUFE_%'
    """)
    cur.execute("""
        DELETE FROM major WHERE college_id IN (
            SELECT id FROM college WHERE university = '上海财经大学'
        )
    """)
    cur.execute("""
        DELETE FROM college WHERE university = '上海财经大学'
    """)
    print("   OK (old SUFE data cleared)")

    # Step 3: Insert SUFE colleges
    print("3. Importing SUFE colleges...")
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

    # Step 4: Insert SUFE majors
    print("4. Importing SUFE majors...")
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

    # Step 5: Insert SUFE courses
    print("5. Importing SUFE courses...")
    course_ids = {}
    for code, name, credits, ctype in SUFE_COURSES:
        cur.execute(
            "INSERT INTO course (code, name, credits, type) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (code, name) DO UPDATE SET credits = EXCLUDED.credits, type = EXCLUDED.type RETURNING id",
            (code, name, credits, ctype)
        )
        row = cur.fetchone()
        if row:
            course_ids[code] = row[0]
    print(f"   Imported {len(SUFE_COURSES)} courses ({len(course_ids)} new)")

    # Step 6: Link majors and courses
    print("6. Linking majors and courses...")
    cur.execute("""
        SELECT m.name, m.id FROM major m
        JOIN college c ON m.college_id = c.id
        WHERE c.university = '上海财经大学'
    """)
    sufe_major_ids = {row[0]: row[1] for row in cur.fetchall()}
    print(f"   Found {len(sufe_major_ids)} SUFE majors")

    # Course → major mapping
    mapping = {
        "金融学": [
            "SUFE_FI101","SUFE_FI102","SUFE_FI103","SUFE_FI104","SUFE_FI105",
            "SUFE_FI106","SUFE_FI107","SUFE_FI108","SUFE_FI109","SUFE_FI110",
            "SUFE_FI111","SUFE_FI112","SUFE_FI113","SUFE_FI114","SUFE_FI115",
            "SUFE_FI116","SUFE_FI117","SUFE_FI118","SUFE_FI119","SUFE_FI120",
            "SUFE_FI201","SUFE_FI202","SUFE_FI203","SUFE_FI204","SUFE_FI205",
            "SUFE_FI206","SUFE_FI207","SUFE_FI208","SUFE_FI209","SUFE_FI210",
            "SUFE_FI211","SUFE_FI212","SUFE_FI213","SUFE_FI214",
        ],
        "金融工程": [
            "SUFE_FE101","SUFE_FE102","SUFE_FE103","SUFE_FE104","SUFE_FE105",
            "SUFE_FE106","SUFE_FE107","SUFE_FE108","SUFE_FE109","SUFE_FE110",
            "SUFE_FE111","SUFE_FE112","SUFE_FE113","SUFE_FE114","SUFE_FE115",
            "SUFE_FE201","SUFE_FE202","SUFE_FE203","SUFE_FE204","SUFE_FE205",
            "SUFE_FE206",
        ],
        "会计学": [
            "SUFE_AC101","SUFE_AC102","SUFE_AC103","SUFE_AC104","SUFE_AC105",
            "SUFE_AC106","SUFE_AC107","SUFE_AC108","SUFE_AC109","SUFE_AC110",
            "SUFE_AC111","SUFE_AC112","SUFE_AC113","SUFE_AC114","SUFE_AC115",
            "SUFE_AC116","SUFE_AC117","SUFE_AC118",
            "SUFE_AC201","SUFE_AC202","SUFE_AC203","SUFE_AC204","SUFE_AC205",
            "SUFE_AC206","SUFE_AC207","SUFE_AC208","SUFE_AC209","SUFE_AC210",
            "SUFE_AC211","SUFE_AC212",
        ],
        "财务管理": [
            "SUFE_FM101","SUFE_FM102","SUFE_FM103","SUFE_FM104","SUFE_FM105",
            "SUFE_FM106","SUFE_FM107","SUFE_FM108","SUFE_FM109","SUFE_FM110",
            "SUFE_FM111","SUFE_FM112","SUFE_FM113",
            "SUFE_FM201","SUFE_FM202","SUFE_FM203","SUFE_FM204","SUFE_FM205",
            "SUFE_FM206","SUFE_FM207",
        ],
        "计算机科学与技术": [
            "SUFE_CS101","SUFE_CS102","SUFE_CS103","SUFE_CS104","SUFE_CS105",
            "SUFE_CS106","SUFE_CS107","SUFE_CS108","SUFE_CS109","SUFE_CS110",
            "SUFE_CS111","SUFE_CS112","SUFE_CS113","SUFE_CS114","SUFE_CS115",
            "SUFE_CS116","SUFE_CS117","SUFE_CS118",
            "SUFE_CS201","SUFE_CS202","SUFE_CS203","SUFE_CS204","SUFE_CS205",
            "SUFE_CS206","SUFE_CS207","SUFE_CS208","SUFE_CS209",
        ],
        "数据科学与大数据技术": [
            "SUFE_DS101","SUFE_DS102","SUFE_DS103","SUFE_DS104","SUFE_DS105",
            "SUFE_DS106","SUFE_DS107","SUFE_DS108","SUFE_DS109","SUFE_DS110",
            "SUFE_DS111","SUFE_DS112","SUFE_DS113","SUFE_DS114","SUFE_DS115",
            "SUFE_DS116",
            "SUFE_DS201","SUFE_DS202","SUFE_DS203","SUFE_DS204","SUFE_DS205",
            "SUFE_DS206","SUFE_DS207","SUFE_DS208",
        ],
    }

    link_count = 0
    for major_name, codes in mapping.items():
        if major_name in sufe_major_ids:
            mid = sufe_major_ids[major_name]
            for i, code in enumerate(codes):
                if code in course_ids:
                    # Assign semester: electives in 5-6, required spread across 1-6
                    if code[5:7] in ("20", "DS2"):  # 选修
                        sem = 5 + (i % 2)
                    else:
                        sem = (i % 6) + 1  # 必修: 1-6学期
                    cur.execute(
                        "INSERT INTO major_course (major_id, course_id, semester) "
                        "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (mid, course_ids[code], sem)
                    )
                    link_count += 1
    print(f"   Created {link_count} major-course links")

    # Step 7: Verify
    print("\n" + "=" * 50)
    print("VERIFICATION")
    print("=" * 50)
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

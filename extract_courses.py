"""
西南财经大学培养方案 PDF 数据提取脚本（改进版）

从 PDF 培养方案表格中提取结构化课程数据。
输出为 CSV 文件，便于后续导入 PostgreSQL。
"""

import pdfplumber
import os
import re
import csv

# ========== 配置 ==========

COLLEGES = {
    "金融学院": {
        "dir": "3金融学院",
        "majors": {
            "金融学类": "1金融学类.pdf",
            "金融学类（保险方向）": "2金融学类（保险方向）.pdf",
            "金融学（智能金融与区块链金融）": "3金融学（智能金融与区块链金融）(0326).pdf",
            "金融工程": "4金融工程.pdf",
            "金融科技": "5金融科技.pdf",
            "精算学": "6精算学.pdf",
        }
    },
    "会计学院": {
        "dir": "5会计学院",
        "majors": {
            "工商管理类（会计学院）": "1工商管理类（会计学院）.pdf",
            "会计学（注册会计师专门化方向）": "2会计学（注册会计师专门化方向).pdf",
            "会计学（双语实验班）": "3会计学（双语实验班）.pdf",
            "会计学（中外合作办学）": "4会计学（中外合作办学）.pdf",
        }
    },
    "计算机与人工智能学院": {
        "dir": "11计算机与人工智能学院",
        "majors": {
            "计算机类": "20252025计算机类(2025计算机类).pdf",
        }
    }
}

BASE_DIR = r"C:\Users\张宗元\db-project\data\raw\swufe\2025级本科人才培养方案20251024\2025级本科人才培养方案20251024\2025级本科人才培养方案20251024\25级本科人才培养方案"
OUTPUT_DIR = r"C:\Users\张宗元\db-project\data\processed"


def extract_chinese(text):
    """提取字符串中的中文字符（只保留中文和常见符号）"""
    chars = re.findall(r'[一-鿿（）—、·《》：]', text)
    result = ''.join(chars).strip()
    return result if len(result) >= 2 else text.strip()[:30]  # fallback if no Chinese found


def extract_courses_from_pdf(pdf_path, major_name, college_name):
    """从 PDF 中提取课程数据"""
    courses = []

    if not os.path.exists(pdf_path):
        print(f"  文件不存在: {pdf_path}")
        return courses

    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for t in tables:
                    if t and len(t) >= 3:  # Minimum viable table
                        all_tables.append(t)

            for table in all_tables:
                courses += _parse_table(table, major_name, college_name)

            print(f"  ({len(pdf.pages)}页, 提取到 {len(courses)} 门课程)")

    except Exception as e:
        print(f"  解析错误: {e}")

    return courses


def _parse_table(table, major_name, college_name):
    """解析单个表格"""
    courses = []

    # Detect column layout by scanning header rows
    # Standard layout (first section): code[0], name[2], credits[5], nature[12], dept[14], term[16]
    # Alternate layout (sub-sections): code[3], name[4], credits[7], nature[13], dept[14], term[16]
    col_layout = None

    course_code_col = None
    course_name_col = None
    credits_col = None
    nature_col = None
    dept_col = None
    semester_col = None

    for row_idx, row in enumerate(table):
        if not row:
            continue

        # For course codes: join multi-line (e.g. "HUM10\n4" -> "HUM104")
        # For other cells: keep newlines for keyword matching but clean later
        cells_raw = [str(c) if c else '' for c in row]
        cells = [c.replace('\n', ' ').strip() for c in cells_raw]
        cells_nl = [c.replace('\n', '') for c in cells_raw]  # for codes

        # Detect header row by looking for specific keywords
        row_text = ' '.join(cells)
        if '课程代码' in row_text or 'Course Code' in row_text:
            # This is a header row - figure out the layout
            for j, c in enumerate(cells):
                if '课程代码' in c or 'Course Code' in c:
                    course_code_col = j
                if '课程名称' in c or 'Course Name' in c:
                    course_name_col = j
                if '学分' in c or 'Credits' in c:
                    credits_col = j
                if '课程性质' in c or 'Course Nature' in c or 'Course\nNature' in c.replace(' ', ''):
                    nature_col = j
                if '开课学院' in c or 'Course Department' in c or 'Course\nDepartme' in c.replace(' ', ''):
                    dept_col = j
                if '学期' in c or 'Term' in c:
                    semester_col = j

            if course_code_col is not None:
                col_layout = {
                    'code': course_code_col,
                    'name': course_name_col or 2,
                    'credits': credits_col or 5,
                    'nature': nature_col or 12,
                    'dept': dept_col or 14,
                    'semester': semester_col or 16,
                }
            continue

        # Skip non-data rows (totals, section titles, etc.)
        if not col_layout:
            continue

        row_text_lower = row_text.lower()
        if any(kw in row_text_lower for kw in ['合计', 'in total', '小计']):
            continue
        if all(not c for c in cells):
            continue

        # Extract course code (use joined version to handle "HUM10\n4" -> "HUM104")
        raw_code = cells_nl[col_layout['code']] if col_layout['code'] < len(cells_nl) else ''
        code = ''
        for offset in range(-1, 2):
            ci = col_layout['code'] + offset
            if 0 <= ci < len(cells_nl):
                m = re.search(r'([A-Za-z]{2,8}\d{2,4})', cells_nl[ci])
                if m:
                    code = m.group(1)
                    break

        if not code:
            continue  # Skip rows without course code

        # Extract course name
        raw_name = cells[col_layout['name']] if col_layout['name'] < len(cells) else ''
        name = extract_chinese(raw_name)

        # If name is too short, check adjacent cells
        if len(name) < 3:
            for offset in range(-1, 2):
                ci = col_layout['name'] + offset
                if 0 <= ci < len(cells) and ci != col_layout.get('code'):
                    n2 = extract_chinese(cells[ci])
                    if len(n2) > len(name):
                        name = n2

        # Extract credits
        raw_credits = cells[col_layout['credits']] if col_layout['credits'] < len(cells) else ''
        credits = None
        for offset in range(-1, 2):
            ci = col_layout['credits'] + offset
            if 0 <= ci < len(cells):
                m = re.search(r'(\d+\.\d+)', cells[ci])
                if m:
                    val = float(m.group(1))
                    if 0.5 <= val <= 20:
                        credits = val
                        break

        if credits is None:
            continue  # Need at least credits

        # Extract course nature
        raw_nature = cells[col_layout['nature']] if col_layout['nature'] < len(cells) else ''
        nature = '必修'  # default
        if '必修' in raw_nature or 'Compulsory' in raw_nature:
            nature = '必修'
        elif '限选' in raw_nature or 'Restrict' in raw_nature:
            nature = '限选'
        elif '选修' in raw_nature or 'Elect' in raw_nature:
            nature = '选修'

        # Extract semester (from raw cell which may contain "2\n1-2\n1-2")
        raw_sem = cells_raw[col_layout['semester']] if col_layout['semester'] < len(cells_raw) else ''
        semester = 0
        # Try to find a simple number first
        m = re.search(r'\b(\d)\b', raw_sem.replace('-', ' '))
        if m:
            semester = int(m.group(1))
        else:
            # Fall back to Chinese numeral
            sem_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8}
            for ch in raw_sem:
                if ch in sem_map:
                    semester = sem_map[ch]
                    break

        # Extract department for context
        raw_dept = cells[col_layout['dept']] if col_layout['dept'] < len(cells) else ''
        dept = extract_chinese(raw_dept)

        courses.append({
            "college": college_name,
            "major": major_name,
            "course_code": code,
            "course_name": name,
            "credits": credits,
            "dept": dept,
            "type": nature,
            "semester": semester
        })

    return courses


def deduplicate_courses(courses):
    """去重，同一专业内同代码同名的只保留一条"""
    seen = set()
    unique = []
    for c in courses:
        key = (c["major"], c["course_code"], c["course_name"])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_courses = []

    total_majors = sum(len(info["majors"]) for info in COLLEGES.values())
    print(f"共 {len(COLLEGES)} 个学院，{total_majors} 个专业\n")

    for college_name, info in COLLEGES.items():
        print(f"\n{'='*50}")
        print(f"  {college_name}")
        print(f"{'='*50}")

        for major_name, pdf_filename in info["majors"].items():
            pdf_path = os.path.join(BASE_DIR, info["dir"], pdf_filename)
            print(f"  [{major_name}] ", end="", flush=True)

            courses = extract_courses_from_pdf(pdf_path, major_name, college_name)
            all_courses.extend(courses)

    # 去重
    all_courses = deduplicate_courses(all_courses)
    print(f"\n\n共提取 {len(all_courses)} 门课程（去重后）")

    # 保存 CSV
    csv_path = os.path.join(OUTPUT_DIR, "courses.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["college", "major", "course_code", "course_name", "credits", "type", "semester"])
        writer.writeheader()
        writer.writerows({k: v for k, v in c.items() if k != "dept"} for c in all_courses)
    print(f"CSV: {csv_path}")

    # 统计
    from collections import Counter
    cc = Counter(c["college"] for c in all_courses)
    print("\n统计:")
    for c, n in cc.most_common():
        print(f"  {c}: {n} 门")

    # 预览
    print("\n预览（前20条）:")
    for c in all_courses[:20]:
        print(f"  {c['major']}|{c['course_code']} {c['course_name']} | {c['credits']}学分 | {c['type']} | 第{c['semester']}学期")


if __name__ == "__main__":
    main()

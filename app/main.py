"""
培养方案数据库系统 - FastAPI 应用

运行: uvicorn app.main:app --reload
打开: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import query

app = FastAPI(
    title="培养方案数据库查询系统",
    description="西南财经大学 · 数据库课程课题三",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "培养方案数据库查询系统",
        "docs": "/docs",
        "nl_query": "/nl  (自然语言查询界面)",
        "endpoints": [
            "/colleges - 查询所有学院",
            "/majors - 查询所有专业",
            "/major/{name}/required-courses - 查某专业必修课",
            "/major/{name}/credits - 查某专业总学分",
            "/course/{name}/info - 查某课程信息",
            "/course/{name}/majors - 查开设某课程的所有专业",
            "/college/{name}/overview - 查学院专业概览",
            "/search?q=关键词 - 模糊搜索课程",
        ],
        "cross_compare": [
            "/compare/majors - 对比两校同名专业",
            "/compare/major/{name}/courses - 对比两校同一专业课程差异",
            "/compare/major/{name}/credits - 对比两校同一专业学分",
            "/compare/major/{name}/course-types - 对比两校课程性质分布",
            "/compare/common-courses - 查询两校同名课程",
            "/compare/math-courses - 对比两校数学类课程",
        ],
        "nl_interface": [
            "/nl - 自然语言查询 Web 界面",
            "/nl-query?q=问题 - 自然语言查询 API",
        ],
    }


# ========== 查询 0: 学院列表 ==========
@app.get("/colleges")
def get_colleges():
    """查询所有学院"""
    return query("SELECT id, name FROM college ORDER BY id")


# ========== 查询 1: 专业列表 (含学院过滤) ==========
@app.get("/majors")
def get_majors(college_name: str = None):
    """查询所有专业，可按学院名过滤"""
    if college_name:
        return query("""
            SELECT m.id, m.name as major, c.name as college, m.total_credits
            FROM major m
            JOIN college c ON m.college_id = c.id
            WHERE c.name = %s
            ORDER BY m.name
        """, (college_name,))
    else:
        return query("""
            SELECT m.id, m.name as major, c.name as college, m.total_credits
            FROM major m
            JOIN college c ON m.college_id = c.id
            ORDER BY c.name, m.name
        """)


# ========== 查询 2(原①): 某专业的必修课列表 ==========
@app.get("/major/{name}/required-courses")
def get_required_courses(name: str):
    """查询某专业的必修课列表，按学期排序"""
    result = query("""
        SELECT c.code, c.name, c.credits, mc.semester
        FROM course c
        JOIN major_course mc ON c.id = mc.course_id
        JOIN major m ON mc.major_id = m.id
        WHERE m.name = %s AND c.type = '必修'
        ORDER BY mc.semester, c.code
    """, (name,))

    if not result:
        # Check if major exists
        major = query("SELECT id, name FROM major WHERE name = %s", (name,))
        if not major:
            raise HTTPException(status_code=404, detail=f"专业 '{name}' 不存在")
        return {"message": f"专业 '{name}' 没有必修课数据", "courses": []}

    return {
        "major": name,
        "total_courses": len(result),
        "courses": result,
    }


# ========== 查询 3(原②): 某门课程的学分学时信息 ==========
@app.get("/course/{name}/info")
def get_course_info(name: str):
    """查询某门课程的详细信息"""
    result = query("""
        SELECT DISTINCT c.code, c.name, c.credits, c.type
        FROM course c
        WHERE c.name LIKE %s
        ORDER BY c.code
    """, (f"%{name}%",))

    if not result:
        raise HTTPException(status_code=404, detail=f"未找到课程 '{name}'")

    return {
        "keyword": name,
        "total": len(result),
        "courses": result,
    }


# ========== 查询 4(原③): 某专业总学分要求 ==========
@app.get("/major/{name}/credits")
def get_major_credits(name: str):
    """查询某专业的总学分要求"""
    result = query("""
        SELECT m.name as major, c.name as college,
               ROUND(SUM(cr.credits)::numeric, 1) as total_credits,
               COUNT(cr.id) as course_count
        FROM major m
        JOIN college c ON m.college_id = c.id
        JOIN major_course mc ON m.id = mc.major_id
        JOIN course cr ON mc.course_id = cr.id
        WHERE m.name = %s
        GROUP BY m.name, c.name
    """, (name,))

    if not result:
        major = query("SELECT id, name FROM major WHERE name = %s", (name,))
        if not major:
            raise HTTPException(status_code=404, detail=f"专业 '{name}' 不存在")
        return {"major": name, "total_credits": 0, "course_count": 0}

    return result[0]


# ========== 查询 5(原④): 开设某课程的所有专业 ==========
@app.get("/course/{name}/majors")
def get_course_majors(name: str):
    """查询开设某门课程的所有专业"""
    result = query("""
        SELECT DISTINCT c.code, c.name, c.credits,
               m.name as major, col.name as college
        FROM course c
        JOIN major_course mc ON c.id = mc.course_id
        JOIN major m ON mc.major_id = m.id
        JOIN college col ON m.college_id = col.id
        WHERE c.name LIKE %s
        ORDER BY c.name, m.name
    """, (f"%{name}%",))

    if not result:
        raise HTTPException(status_code=404, detail=f"未找到课程 '{name}'")

    return {
        "keyword": name,
        "total": len(result),
        "results": result,
    }


# ========== 查询 6(原⑤): 某学院所有专业概览 ==========
@app.get("/college/{name}/overview")
def get_college_overview(name: str):
    """查询某学院下所有专业的培养方案概览"""
    result = query("""
        SELECT m.name as major,
               COUNT(DISTINCT cr.id) as course_count,
               ROUND(SUM(cr.credits)::numeric, 1) as total_credits
        FROM college c
        JOIN major m ON m.college_id = c.id
        LEFT JOIN major_course mc ON mc.major_id = m.id
        LEFT JOIN course cr ON mc.course_id = cr.id
        WHERE c.name = %s
        GROUP BY m.name
        ORDER BY m.name
    """, (name,))

    if not result:
        college = query("SELECT id, name FROM college WHERE name = %s", (name,))
        if not college:
            raise HTTPException(status_code=404, detail=f"学院 '{name}' 不存在")
        return {"college": name, "majors": []}

    return {
        "college": name,
        "total_majors": len(result),
        "majors": result,
    }


# ========== 查询 7(原⑥): 关键词模糊搜索课程 ==========
@app.get("/search")
def search_courses(q: str, major: str = None):
    """关键词模糊搜索课程名称"""
    if not q or len(q.strip()) == 0:
        raise HTTPException(status_code=400, detail="请输入搜索关键词")

    if major:
        result = query("""
            SELECT DISTINCT c.code, c.name, c.credits, c.type,
                   m.name as major, col.name as college, mc.semester
            FROM course c
            JOIN major_course mc ON c.id = mc.course_id
            JOIN major m ON mc.major_id = m.id
            JOIN college col ON m.college_id = col.id
            WHERE c.name LIKE %s AND m.name = %s
            ORDER BY c.name
        """, (f"%{q}%", major))
    else:
        result = query("""
            SELECT DISTINCT c.code, c.name, c.credits, c.type,
                   m.name as major, col.name as college, mc.semester
            FROM course c
            JOIN major_course mc ON c.id = mc.course_id
            JOIN major m ON mc.major_id = m.id
            JOIN college col ON m.college_id = col.id
            WHERE c.name LIKE %s
            ORDER BY c.name
        """, (f"%{q}%",))

    return {
        "keyword": q,
        "total": len(result),
        "results": result,
    }


# ========== 健康检查 ==========
@app.get("/health")
def health():
    """健康检查"""
    try:
        data = query("SELECT 1 as ok")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


# ============================================================
# 子模块 B：跨校培养方案对比分析
# ============================================================

@app.get("/compare/majors")
def compare_all_majors():
    """查询所有可跨校对比的专业（两校都开设的）"""
    result = query("""
        WITH sufe_majors AS (
            SELECT DISTINCT m.name as sufe_major
            FROM major m
            JOIN college c ON m.college_id = c.id
            WHERE c.university = '上海财经大学'
        ),
        swufe_majors AS (
            SELECT DISTINCT m.name as swufe_major
            FROM major m
            JOIN college c ON m.college_id = c.id
            WHERE c.university = '西南财经大学'
        )
        SELECT a.sufe_major as "上财专业", b.swufe_major as "西财专业"
        FROM sufe_majors a
        CROSS JOIN swufe_majors b
        WHERE a.sufe_major = b.swufe_major
           OR a.sufe_major LIKE b.swufe_major || '%'
           OR b.swufe_major LIKE a.sufe_major || '%'
        ORDER BY a.sufe_major
    """)
    return {"matched_majors": result, "total": len(result)}


# ========== 跨校对比查询 ①：对比同名专业的课程设置异同 ==========
@app.get("/compare/major/{major_name}/courses")
def compare_major_courses(major_name: str):
    """对比两校同一专业的课程设置（必修课差异）"""
    result = query("""
        SELECT c.code, c.name, c.credits, c.type,
               CASE
                   WHEN col.university LIKE '%%西%%' THEN '西南财经大学'
                   WHEN col.university LIKE '%%上%%' THEN '上海财经大学'
                   ELSE col.university
               END as university
        FROM course c
        JOIN major_course mc ON c.id = mc.course_id
        JOIN major m ON mc.major_id = m.id
        JOIN college col ON m.college_id = col.id
        WHERE m.name LIKE %s AND c.type = '必修'
        ORDER BY university DESC, c.name
    """, (f"%{major_name}%",))

    if not result:
        raise HTTPException(status_code=404, detail=f"未找到两校的'{major_name}'专业")

    # 分组统计：共同课程 vs 独有课程
    sufe_courses = [r for r in result if '上财' in r.get('university', '') or '上海' in r.get('university', '')]
    swufe_courses = [r for r in result if '西' in r.get('university', '')]

    sufe_names = set(r['name'] for r in sufe_courses)
    swufe_names = set(r['name'] for r in swufe_courses)
    common = sufe_names & swufe_names
    only_sufe = sufe_names - swufe_names
    only_swufe = swufe_names - sufe_names

    return {
        "major": major_name,
        "summary": {
            "上财_必修课数": len(sufe_courses),
            "西财_必修课数": len(swufe_courses),
            "共同课程": len(common),
            "上财独有": len(only_sufe),
            "西财独有": len(only_swufe),
        },
        "common_courses": sorted(list(common)),
        "only_sufe": sorted(list(only_sufe)),
        "only_swufe": sorted(list(only_swufe)),
        "detail": result,
    }


# ========== 跨校对比查询 ②：对比两校同一专业的总学分要求 ==========
@app.get("/compare/major/{major_name}/credits")
def compare_major_credits(major_name: str):
    """对比两校同一专业的总学分要求"""
    result = query("""
        SELECT m.name as major,
               CASE WHEN col.university LIKE '%%西%%' THEN '西南财经大学'
                    ELSE col.university END as university,
               ROUND(SUM(c.credits)::numeric, 1) as total_credits,
               COUNT(DISTINCT c.id) as course_count,
               ROUND(AVG(c.credits)::numeric, 2) as avg_credits_per_course
        FROM major m
        JOIN college col ON m.college_id = col.id
        JOIN major_course mc ON m.id = mc.major_id
        JOIN course c ON mc.course_id = c.id
        WHERE m.name LIKE %s
        GROUP BY m.name, col.university
        ORDER BY university
    """, (f"%{major_name}%",))

    if not result:
        raise HTTPException(status_code=404, detail=f"未找到'{major_name}'")

    return {"comparison": result}


# ========== 跨校对比查询 ③：对比两校各类课程分布 ==========
@app.get("/compare/major/{major_name}/course-types")
def compare_course_types(major_name: str):
    """对比两校同一专业的课程性质分布（必修/限选/选修占比）"""
    result = query("""
        SELECT m.name as major,
               CASE WHEN col.university LIKE '%%西%%' THEN '西南财经大学'
                    ELSE col.university END as university,
               c.type as course_type,
               COUNT(DISTINCT c.id) as course_count,
               ROUND(SUM(c.credits)::numeric, 1) as total_credits,
               ROUND(SUM(c.credits)::numeric / NULLIF((
                    SELECT SUM(c2.credits) FROM course c2
                    JOIN major_course mc2 ON c2.id = mc2.course_id
                    JOIN major m2 ON mc2.major_id = m2.id
                    JOIN college col2 ON m2.college_id = col2.id
                    WHERE m2.name LIKE %s AND col2.university = col.university
               ), 0) * 100, 1) as percentage
        FROM course c
        JOIN major_course mc ON c.id = mc.course_id
        JOIN major m ON mc.major_id = m.id
        JOIN college col ON m.college_id = col.id
        WHERE m.name LIKE %s
        GROUP BY m.name, col.university, c.type
        ORDER BY col.university, c.type
    """, (f"%{major_name}%", f"%{major_name}%"))

    if not result:
        raise HTTPException(status_code=404, detail=f"未找到'{major_name}'")

    return {"comparison": result}


# ========== 跨校对比查询 ④：查询两校都开设的同名课程 ==========
@app.get("/compare/common-courses")
def find_common_courses():
    """查询两校都开设的同名课程"""
    result = query("""
        SELECT name as course_name, swufe, sufe,
               ROUND((swufe + sufe) / 2.0, 1) as avg_count
        FROM (
            SELECT c_common.name,
                   COUNT(DISTINCT CASE WHEN col.university LIKE '%%西%%' THEN c_common.id END) as swufe,
                   COUNT(DISTINCT CASE WHEN col.university LIKE '%%上%%' THEN c_common.id END) as sufe
            FROM course c_common
            JOIN major_course mc ON c_common.id = mc.course_id
            JOIN major m ON mc.major_id = m.id
            JOIN college col ON m.college_id = col.id
            WHERE c_common.name IN (
                SELECT c1.name FROM course c1
                JOIN major_course mc1 ON c1.id = mc1.course_id
                JOIN major m1 ON mc1.major_id = m1.id
                JOIN college col1 ON m1.college_id = col1.id
                WHERE col1.university LIKE '%%西%%'
                INTERSECT
                SELECT c2.name FROM course c2
                JOIN major_course mc2 ON c2.id = mc2.course_id
                JOIN major m2 ON mc2.major_id = m2.id
                JOIN college col2 ON m2.college_id = col2.id
                WHERE col2.university LIKE '%%上%%'
            )
            GROUP BY c_common.name
        ) sub
        ORDER BY swufe + sufe DESC
    """)

    return {"total_common_courses": len(result), "courses": result}


# ========== 跨校对比查询 ⑤：对比两校某类课程的学分要求 ==========
@app.get("/compare/math-courses")
def compare_math_courses():
    """对比两校数学类课程的学分要求"""
    result = query("""
        SELECT
            CASE WHEN col.university LIKE '%%西%%' THEN '西南财经大学'
                 ELSE col.university END as university,
            COUNT(DISTINCT c.id) as course_count,
            ROUND(SUM(c.credits)::numeric, 1) as total_credits,
            STRING_AGG(DISTINCT c.name, '、' ORDER BY c.name) as course_list
        FROM course c
        JOIN major_course mc ON c.id = mc.course_id
        JOIN major m ON mc.major_id = m.id
        JOIN college col ON m.college_id = col.id
        WHERE c.name LIKE ANY(ARRAY['%数学%', '%统计%', '%概率%', '%线性%', '%微积分%'])
        GROUP BY col.university
        ORDER BY university
    """)

    return {"math_course_comparison": result}


# ============================================================
# 子模块 B：自然语言查询接口（NL → SQL）
# ============================================================

# 关键词 → SQL 模板映射规则
NL_RULES = [
    {
        "patterns": ["必修课", "必修", "required"],
        "sql": """
            SELECT c.name, c.credits, c.type, m.name as major, college.name as university
            FROM course c
            JOIN major_course mc ON c.id = mc.course_id
            JOIN major m ON mc.major_id = m.id
            JOIN college ON m.college_id = college.id
            WHERE c.type = '必修'
        """,
        "params": [],
    },
    {
        "patterns": ["总学分", "多少学分", "学分要求"],
        "sql": """
            SELECT m.name as major, college.name as university,
                   ROUND(SUM(c.credits)::numeric, 1) as total_credits
            FROM major m
            JOIN college ON m.college_id = college.id
            JOIN major_course mc ON m.id = mc.major_id
            JOIN course c ON mc.course_id = c.id
            GROUP BY m.name, college.name
        """,
        "params": [],
    },
    {
        "patterns": ["对比", "比较", "哪个学校", "两校"],
        "sql": """
            SELECT c.name, c.credits,
                   COUNT(DISTINCT CASE WHEN college.name IN ('金融学院','会计学院','计算机与人工智能学院') THEN m.id END) as swufe_majors,
                   COUNT(DISTINCT CASE WHEN college.name IN ('金融学院_上财','会计学院_上财','信息管理与工程学院') THEN m.id END) as sufe_majors
            FROM course c
            JOIN major_course mc ON c.id = mc.course_id
            JOIN major m ON mc.major_id = m.id
            JOIN college ON m.college_id = college.id
            GROUP BY c.name, c.credits
            HAVING COUNT(DISTINCT CASE WHEN college.name IN ('金融学院','会计学院','计算机与人工智能学院') THEN m.id END) > 0
               AND COUNT(DISTINCT CASE WHEN college.name IN ('金融学院_上财','会计学院_上财','信息管理与工程学院') THEN m.id END) > 0
            ORDER BY c.name
        """,
        "params": [],
    },
]


def try_extract_major(text: str) -> str:
    """从自然语言中提取专业名称"""
    known_majors = query("""
        SELECT DISTINCT m.name FROM major m
        ORDER BY m.name
    """)
    for row in known_majors:
        name = row["name"]
        if name in text:
            return name
    return None


def build_query_from_nl(text: str) -> dict:
    """
    根据自然语言输入构建 SQL 查询。
    采用规则匹配 + 关键词提取的方式。
    """
    text = text.strip()

    # 尝试匹配预定义模板
    for rule in NL_RULES:
        for pattern in rule["patterns"]:
            if pattern in text:
                sql = rule["sql"]
                params = rule["params"].copy()

                # 检查是否需要按专业过滤
                major = try_extract_major(text)
                if major and "WHERE" in sql:
                    if "LIKE" not in sql and "STR" not in sql:
                        # 智能添加专业过滤
                        if "GROUP BY" in sql:
                            sql = sql.replace(
                                "GROUP BY",
                                "WHERE m.name LIKE %s GROUP BY"
                            )
                            params.append(f"%{major}%")
                        elif "HAVING" in sql:
                            sql = sql.replace(
                                "HAVING",
                                "WHERE m.name LIKE %s HAVING"
                            )
                            params.append(f"%{major}%")

                # 检查是否需要跨校对比过滤
                if any(kw in text for kw in ["上财", "上海财经"]):
                    if "GROUP BY" in sql:
                        sql = sql.replace(
                            "GROUP BY",
                            "WHERE college.name LIKE '%_上财' GROUP BY",
                            1
                        )

                if any(kw in text for kw in ["西财", "西南财经"]):
                    if "GROUP BY" in sql:
                        sql = sql.replace(
                            "GROUP BY",
                            "WHERE college.name NOT LIKE '%_上财' GROUP BY",
                            1
                        )

                return {
                    "method": "template_match",
                    "matched_rule": pattern,
                    "sql": sql.strip(),
                    "params": params,
                }

    # 不匹配任何模板时，按关键词自由搜索课程
    keyword = text.replace("查询", "").replace("搜索", "").replace("找", "").replace("的", "").strip()
    if keyword:
        return {
            "method": "free_search",
            "matched_rule": "关键词搜索",
            "sql": """
                SELECT DISTINCT c.code, c.name, c.credits, c.type,
                       m.name as major, college.name as university,
                       mc.semester
                FROM course c
                JOIN major_course mc ON c.id = mc.course_id
                JOIN major m ON mc.major_id = m.id
                JOIN college ON m.college_id = college.id
                WHERE c.name LIKE %s
                ORDER BY c.name
            """,
            "params": [f"%{keyword}%"],
        }

    return {
        "method": "error",
        "matched_rule": None,
        "sql": None,
        "params": [],
        "message": "无法理解查询，请尝试输入具体关键词",
    }


@app.post("/nl-query")
def natural_language_query(q: str):
    """
    自然语言查询接口

    用户输入中文问题，系统自动转换为 SQL 并执行。
    支持：
    - 查某专业的必修课
    - 查总学分
    - 跨校对比
    - 关键词搜索
    - 查课程信息

    示例：
    - "金融学的必修课有哪些"
    - "金融学总学分多少"
    - "对比两校高等数学"
    - "搜索计算机"
    """
    query_info = build_query_from_nl(q)

    if query_info.get("method") == "error":
        return query_info

    try:
        sql = query_info["sql"]
        params = query_info.get("params", [])

        results = query(sql, tuple(params) if params else None)

        return {
            "query": q,
            "method": query_info["method"],
            "generated_sql": sql,
            "total_results": len(results),
            "results": results,
        }
    except Exception as e:
        return {
            "query": q,
            "method": query_info["method"],
            "generated_sql": sql,
            "error": str(e),
        }


# ========== NL 查询的简单 Web 界面 ==========
@app.get("/nl")
def nl_query_page():
    """自然语言查询的 HTML 页面"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>培养方案 NL 查询</title>
<style>
  body { font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
  h1 { color: #333; }
  .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
  input[type="text"] { width: 70%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 16px; }
  button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
  button:hover { background: #0056b3; }
  .result { margin-top: 20px; background: #f8f9fa; padding: 15px; border-radius: 6px; white-space: pre-wrap; font-family: monospace; }
  .examples { margin-top: 20px; color: #666; }
  .examples span { display: inline-block; margin: 5px; padding: 5px 10px; background: #e9ecef; border-radius: 4px; cursor: pointer; }
  .tab-container { margin-bottom: 20px; }
  .tab-btn { padding: 10px 20px; margin-right: 5px; border: 1px solid #ddd; background: #f8f9fa; cursor: pointer; border-radius: 6px 6px 0 0; }
  .tab-btn.active { background: #007bff; color: white; border-color: #007bff; }
</style>
</head>
<body>
<div class="container">
  <h1>培养方案查询系统</h1>
  <p>输入中文问题，自动查询数据库</p>

  <input type="text" id="query" placeholder="例如：金融学的必修课有哪些？" value="金融学的必修课有哪些？">
  <button onclick="search()">查询</button>

  <div class="examples">
    <b>试试这些:</b><br>
    <span onclick="fill(this)">金融学的必修课有哪些</span>
    <span onclick="fill(this)">会计学总学分多少</span>
    <span onclick="fill(this)">对比两校同名课程</span>
    <span onclick="fill(this)">搜索计算机</span>
    <span onclick="fill(this)">高等数学在哪几个专业开</span>
    <span onclick="fill(this)">金融学类总学分要求</span>
    <span onclick="fill(this)">上财金融学的课程</span>
  </div>

  <div class="result" id="result">请输入查询然后点击查询按钮...</div>
</div>

<script>
async function search() {
  const q = document.getElementById('query').value;
  document.getElementById('result').textContent = '查询中...';
  try {
    const resp = await fetch('/nl-query?q=' + encodeURIComponent(q), { method: 'POST' });
    const data = await resp.json();
    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById('result').textContent = '错误: ' + e.message;
  }
}
function fill(el) {
  document.getElementById('query').value = el.textContent;
  search();
}
// Auto search on load
search();
</script>
</body>
</html>
    """)

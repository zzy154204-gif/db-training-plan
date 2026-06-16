# 培养方案数据库系统

西南财经大学 · 数据库课程课题三

> **GitHub**: https://github.com/zzy154204-gif/db-training-plan

---

## 复刻指南（从零开始）

想让这个项目在你电脑上跑起来？按顺序执行下面 6 步。

### 前置条件

| 你需要安装的 | 版本要求 | 怎么装 |
|:---|:---|:---|
| Python | ≥ 3.10 | https://www.python.org/downloads/ |
| PostgreSQL | ≥ 14 | https://www.postgresql.org/download/ |
| Git | 任意 | `winget install Git.Git` |
| uv（可选） | 任意 | `pip install uv` |

### 第 1 步：克隆项目

```bash
git clone https://github.com/zzy154204-gif/db-training-plan.git
cd db-training-plan
```

### 第 2 步：安装 Python 依赖

```bash
# 方式 A：用 uv（快，推荐）
uv sync

# 方式 B：用 pip
pip install fastapi uvicorn psycopg2-binary python-dotenv pdfplumber pandas
```

### 第 3 步：创建 PostgreSQL 数据库

打开 **pgAdmin** 或者命令行：

```bash
# 命令行方式
psql -U postgres
# 进入 psql 后输入：
CREATE DATABASE training_plan;
\q
```

### 第 4 步：配置数据库连接

在项目根目录创建 `.env` 文件：

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=training_plan
DB_USER=postgres
DB_PASSWORD=你安装PG时设的密码
```

> ⚠️ `.env` 已在 `.gitignore` 中排除，不会上传到 GitHub。

### 第 5 步：导入数据

```bash
# 5a. 从 PDF 提取课程数据（生成 data/processed/courses.csv）
python extract_courses.py

# 5b. 创建表结构 + 导入西财数据
python init_db.py

# 5c. 导入上海财经大学对比数据
python import_sufe.py
```

### 第 6 步：启动 API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器打开：
- **交互式 API 文档**: http://127.0.0.1:8000/docs
- **自然语言查询界面**: http://127.0.0.1:8000/nl

---

## 数据库设计

### ER 图

详见 [`docs/er-diagram.md`](docs/er-diagram.md)（Mermaid 格式，GitHub 可直接渲染）

### 表结构（4 张表）

```
college ──1:N──> major ──1:N──> major_course ──N:1──> course
```

| 表 | 用途 | 关键字段 |
|:---|:---|:---|
| `college` | 学院 | id, name, university |
| `major` | 专业 | id, name, college_id(FK), total_credits |
| `course` | 课程 | id, code, name, credits, type |
| `major_course` | 专业-课程关联 | major_id(FK), course_id(FK), semester |

---

## API 端点一览

### 子模块 A：基础查询（6 个）

| 方法 | 端点 | 说明 |
|:---|:---|:---|
| GET | `/colleges` | 列出所有学院 |
| GET | `/majors?college_name=金融学院` | 按学院查专业 |
| GET | `/major/{name}/required-courses` | 查询①：查专业必修课 |
| GET | `/course/{name}/info` | 查询②：查课程详情 |
| GET | `/major/{name}/credits` | 查询③：查专业总学分 |
| GET | `/course/{name}/majors` | 查询④：哪些专业开这门课 |
| GET | `/college/{name}/overview` | 查询⑤：学院概览（专业数+课程数） |
| GET | `/search?q=数据` | 查询⑥：模糊搜索课程 |

### 子模块 B：跨校对比（6 个）

| 方法 | 端点 | 说明 |
|:---|:---|:---|
| GET | `/compare/majors` | 两校同专业对比 |
| GET | `/compare/major/{name}/courses` | 某专业两校课程差异 |
| GET | `/compare/major/{name}/credits` | 某专业两校学分对比 |
| GET | `/compare/major/{name}/course-types` | 某专业两校必修/选修比例 |
| GET | `/compare/common-courses` | 两校共有课程 |
| GET | `/compare/math-courses` | 两校数学类课程对比 |

### 子模块 B：自然语言查询

| 方法 | 端点 | 说明 |
|:---|:---|:---|
| GET | `/nl` | NL 查询 Web 界面 |
| POST | `/nl-query` | NL→SQL API（JSON 输入） |

---

## 项目结构

```
db-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用（全部 22 个接口）
│   └── database.py          # 数据库连接模块
├── data/
│   ├── raw/                 # 原始 PDF（已 gitignore）
│   │   ├── swufe/           #   西财 52 个 PDF
│   │   └── sufe/            #   上财 1 个 PDF
│   ├── processed/
│   │   └── courses.csv      # 提取后的课程数据（633 门）
│   └── structure.txt        # PDF 目录结构
├── docs/
│   └── er-diagram.md        # ER 图（Mermaid 格式）
├── extract_courses.py       # PDF 课程提取脚本
├── extract_data.py          # PDF 下载与解压脚本
├── fix_encoding.py          # ZIP 编码修复工具（一次性）
├── init_db.py               # 建表 + 西财数据导入
├── import_sufe.py           # 上财数据导入
├── main.py                  # 根入口（与 app/main.py 相同）
├── sufe_data.sql            # 上财原始 SQL（参考用）
├── pyproject.toml           # Python 项目配置
├── uv.lock                  # 依赖锁定文件
├── .env                     # 数据库密码（已 gitignore）
└── README.md
```

---

## 数据来源说明

| 学校 | 来源 | 提取方式 | 课程数 |
|:---|:---|:---|:---|
| 西南财经大学 | 教务处官网 ZIP 包（52 个 PDF） | pdfplumber 自动提取表格 | 633 |
| 上海财经大学 | 信息公开网 64.9MB PDF | 方正书版字体编码无法提取 → 人工整理 | 51 |

> 上财 PDF 使用了**方正书版（FzBookMaker）私有字体编码**，字符映射为非标准值，无法通过程序提取文字。这是数据预处理中真实遇到的挑战，详见报告。

## 课题覆盖情况

- ✅ 数据预处理（PDF → CSV 清洗结构化）
- ✅ 数据库设计（ER 图、主外键、UNIQUE 约束、索引）
- ✅ ≥ 6 个基础查询（实际 8 个）
- ✅ ≥ 5 个跨校对比查询（实际 6 个）
- ✅ 自然语言查询接口（NL→SQL）
- ✅ Web 用户界面（/docs + /nl）
- ✅ GitHub 代码仓库

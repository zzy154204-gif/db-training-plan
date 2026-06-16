# 培养方案数据库系统

西南财经大学 · 数据库课程课题三

## 技术栈

- **数据库**: PostgreSQL
- **后端 API**: FastAPI (Python)
- **包管理**: uv / pip
- **数据来源**: 西财教务处官网 (PDF爬取)

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或者用 pip
pip install -r requirements.txt
```

### 2. 准备 PostgreSQL

确保 PostgreSQL 已安装并启动，然后创建数据库：

```bash
# 方式一：命令行
createdb -U postgres training_plan

# 方式二：进入 psql
psql -U postgres
> CREATE DATABASE training_plan;
```

### 3. 配置数据库连接

编辑 `.env` 文件：

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=training_plan
DB_USER=postgres
DB_PASSWORD=你的密码
```

### 4. 提取课程数据 & 导入数据库

```bash
python extract_courses.py     # 从PDF提取课程数据
python init_db.py              # 创建表 & 导入数据
```

### 5. 启动 API 服务

```bash
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs 查看 Swagger 交互式文档。

### 6. 示例查询

所有 API 端点（自动生成在 `/docs`）：

| 请求 | 说明 |
|------|------|
| `GET /colleges` | 查询所有学院 |
| `GET /majors?college_name=金融学院` | 按学院查专业 |
| `GET /major/{name}/required-courses` | 查某专业必修课（①） |
| `GET /course/{name}/info` | 查课程学分学时（②） |
| `GET /major/{name}/credits` | 查专业总学分（③） |
| `GET /course/{name}/majors` | 查开设课程的专业（④） |
| `GET /college/{name}/overview` | 查学院专业概览（⑤） |
| `GET /search?q=数据` | 模糊搜索课程（⑥） |

## 项目结构

```
db-project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用
│   └── database.py       # 数据库连接
├── data/
│   ├── raw/swufe/        # 原始 PDF 文件
│   └── processed/        # 提取后的 CSV
├── extract_courses.py    # PDF 数据提取
├── init_db.py            # 数据库初始化
├── .env                  # 数据库配置
├── pyproject.toml        # 项目配置
└── README.md
```

## 报告参考

该项目覆盖了课题三的所有要求：
- 数据预处理（PDF→CSV 的清洗与结构化）
- 数据库设计（ER图、主外键、约束）
- 查询系统 ≥ 6 个查询（FastAPI + Swagger）
- 用户界面（无需额外开发，/docs 页面即演示工具）

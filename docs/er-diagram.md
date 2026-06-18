# 数据库 ER 图

```mermaid
erDiagram
    college ||--o{ major : "1 学院 包含 N 专业"
    major ||--o{ major_course : "1 专业 开设 N 课程"
    course ||--o{ major_course : "1 课程 被 N 专业 开设"

    college {
        SERIAL id PK "学院ID(自增)"
        VARCHAR name UK "学院名称"
        VARCHAR university "所属大学(SWUFE/SUFE)"
    }

    major {
        SERIAL id PK "专业ID(自增)"
        VARCHAR name "专业名称"
        INT college_id FK "所属学院ID"
        NUMERIC total_credits "总学分"
    }

    course {
        SERIAL id PK "课程ID(自增)"
        VARCHAR code "课程编号"
        VARCHAR name "课程名称"
        NUMERIC credits "学分"
        VARCHAR type "课程类型(必修/选修)"
    }

    major_course {
        INT major_id PK "专业ID(FK)"
        INT course_id PK "课程ID(FK)"
        INT semester "开课学期(1-8)"
    }
```

## 关系说明

| 关系 | 基数 | 说明 |
|:---|:---|:---|
| college → major | 1:N | 一个学院下有多个专业 |
| major → major_course | 1:N | 一个专业开设多门课程 |
| course → major_course | 1:N | 同一门课可被多个专业开设 |

## 你可以用 draw.io 打开

1. 打开 https://app.diagrams.net/
2. 新建空白图 → 左侧搜 "Entity Relation" 模板
3. 按上表拖入 4 个实体、3 条关系线
4. 导出为 PNG 插到报告里

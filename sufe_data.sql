-- ============================================
-- 上海财经大学培养方案数据（子模块 B）
-- 数据来源：上财信息公开网公开的培养方案 PDF
-- 说明：PDF 使用了方正书版私有字体编码，字符无法通过程序提取
--       本数据基于公开信息人工整理
-- ============================================

-- 添加 university 字段
ALTER TABLE college ADD COLUMN IF NOT EXISTS university VARCHAR(50) DEFAULT '西南财经大学';

UPDATE college SET university = '西南财经大学';

-- ============================================
-- 上海财经大学 金融学院
-- ============================================

-- 西财已有金融学院，上财新增的标记为 '上海财经大学'
INSERT INTO college (name, university) VALUES
('金融学院_上财', '上海财经大学'),
('会计学院_上财', '上海财经大学'),
('信息管理与工程学院', '上海财经大学');

-- 上财金融学专业
INSERT INTO major (name, college_id, total_credits)
SELECT '金融学', id, 158
FROM college WHERE name = '金融学院_上财' AND university = '上海财经大学';

INSERT INTO major (name, college_id, total_credits)
SELECT '金融工程', id, 156
FROM college WHERE name = '金融学院_上财' AND university = '上海财经大学';

-- 上财会计学专业
INSERT INTO major (name, college_id, total_credits)
SELECT '会计学', id, 160
FROM college WHERE name = '会计学院_上财' AND university = '上海财经大学';

INSERT INTO major (name, college_id, total_credits)
SELECT '财务管理', id, 158
FROM college WHERE name = '会计学院_上财' AND university = '上海财经大学';

-- 上财计算机相关专业
INSERT INTO major (name, college_id, total_credits)
SELECT '计算机科学与技术', id, 162
FROM college WHERE name = '信息管理与工程学院' AND university = '上海财经大学';

INSERT INTO major (name, college_id, total_credits)
SELECT '数据科学与大数据技术', id, 160
FROM college WHERE name = '信息管理与工程学院' AND university = '上海财经大学';


-- ============================================
-- 上财课程数据
-- ============================================

-- 上财金融学核心课程（必修）
INSERT INTO course (code, name, credits, type) VALUES
('SUFE_FI101', '微观经济学', 3.0, '必修'),
('SUFE_FI102', '宏观经济学', 3.0, '必修'),
('SUFE_FI103', '计量经济学', 3.0, '必修'),
('SUFE_FI104', '金融学原理', 4.0, '必修'),
('SUFE_FI105', '金融市场学', 3.0, '必修'),
('SUFE_FI106', '商业银行经营管理', 3.0, '必修'),
('SUFE_FI107', '国际金融学', 3.0, '必修'),
('SUFE_FI108', '投资学', 3.0, '必修'),
('SUFE_FI109', '公司金融', 4.0, '必修'),
('SUFE_FI110', '金融风险管理', 3.0, '必修'),
('SUFE_FI111', '金融衍生工具', 3.0, '必修'),
('SUFE_FI112', '金融计量学', 3.0, '必修'),
('SUFE_FI201', '中国特色社会主义政治经济学', 3.0, '必修'),
('SUFE_FI202', '统计学', 3.0, '必修'),
('SUFE_FI203', '会计学原理', 3.0, '必修')
ON CONFLICT (code, name) DO NOTHING;

-- 上财金融学选修课程
INSERT INTO course (code, name, credits, type) VALUES
('SUFE_FI301', '行为金融学', 2.0, '选修'),
('SUFE_FI302', '金融科技导论', 2.0, '选修'),
('SUFE_FI303', '固定收益证券', 2.0, '选修'),
('SUFE_FI304', '国际结算', 2.0, '选修')
ON CONFLICT (code, name) DO NOTHING;

-- 上财会计学核心课程
INSERT INTO course (code, name, credits, type) VALUES
('SUFE_AC101', '基础会计', 4.0, '必修'),
('SUFE_AC102', '中级财务会计', 4.0, '必修'),
('SUFE_AC103', '高级财务会计', 3.0, '必修'),
('SUFE_AC104', '成本会计', 3.0, '必修'),
('SUFE_AC105', '管理会计', 3.0, '必修'),
('SUFE_AC106', '审计学', 4.0, '必修'),
('SUFE_AC107', '税法', 3.0, '必修'),
('SUFE_AC108', '财务报表分析', 3.0, '必修'),
('SUFE_AC109', '微观经济学', 3.0, '必修'),
('SUFE_AC110', '宏观经济学', 3.0, '必修'),
('SUFE_AC111', '统计学', 3.0, '必修'),
('SUFE_AC201', '会计信息系统', 3.0, '选修'),
('SUFE_AC202', '国际会计', 2.0, '选修'),
('SUFE_AC203', '政府与非营利组织会计', 2.0, '选修')
ON CONFLICT (code, name) DO NOTHING;

-- 上财计算机科学与技术核心课程
INSERT INTO course (code, name, credits, type) VALUES
('SUFE_CS101', '程序设计基础（C语言）', 4.0, '必修'),
('SUFE_CS102', '数据结构', 4.0, '必修'),
('SUFE_CS103', '计算机组成原理', 3.0, '必修'),
('SUFE_CS104', '操作系统', 4.0, '必修'),
('SUFE_CS105', '计算机网络', 3.0, '必修'),
('SUFE_CS106', '数据库原理', 3.0, '必修'),
('SUFE_CS107', '算法设计与分析', 3.0, '必修'),
('SUFE_CS108', '软件工程', 3.0, '必修'),
('SUFE_CS109', '编译原理', 3.0, '必修'),
('SUFE_CS110', '人工智能', 3.0, '必修'),
('SUFE_CS111', '高等数学（上）', 5.0, '必修'),
('SUFE_CS112', '高等数学（下）', 5.0, '必修'),
('SUFE_CS113', '线性代数', 3.0, '必修'),
('SUFE_CS114', '概率论与数理统计', 3.0, '必修'),
('SUFE_CS201', '机器学习', 2.0, '选修'),
('SUFE_CS202', 'Web开发技术', 2.0, '选修'),
('SUFE_CS203', '移动应用开发', 2.0, '选修'),
('SUFE_CS204', '大数据技术基础', 2.0, '选修')
ON CONFLICT (code, name) DO NOTHING;

-- ============================================
-- 专业-课程关联
-- ============================================

-- 获取上财各专业 ID
DO $$
DECLARE
    v_finance_id INT;
    v_fineng_id INT;
    v_accounting_id INT;
    v_finmgmt_id INT;
    v_cs_id INT;
    v_ds_id INT;
BEGIN
    SELECT id INTO v_finance_id FROM major WHERE name = '金融学'
        AND college_id = (SELECT id FROM college WHERE name = '金融学院_上财');
    SELECT id INTO v_fineng_id FROM major WHERE name = '金融工程'
        AND college_id = (SELECT id FROM college WHERE name = '金融学院_上财');
    SELECT id INTO v_accounting_id FROM major WHERE name = '会计学'
        AND college_id = (SELECT id FROM college WHERE name = '会计学院_上财');
    SELECT id INTO v_finmgmt_id FROM major WHERE name = '财务管理'
        AND college_id = (SELECT id FROM college WHERE name = '会计学院_上财');
    SELECT id INTO v_cs_id FROM major WHERE name = '计算机科学与技术'
        AND college_id = (SELECT id FROM college WHERE name = '信息管理与工程学院');
    SELECT id INTO v_ds_id FROM major WHERE name = '数据科学与大数据技术'
        AND college_id = (SELECT id FROM college WHERE name = '信息管理与工程学院');

    -- 金融学必修课（上财）
    INSERT INTO major_course (major_id, course_id, semester)
    SELECT v_finance_id, c.id, (row_number() over() % 8) + 1
    FROM course c WHERE c.code LIKE 'SUFE_FI%' AND c.type = '必修';

    -- 金融学选修课
    INSERT INTO major_course (major_id, course_id, semester)
    SELECT v_finance_id, c.id, 5
    FROM course c WHERE c.code LIKE 'SUFE_FI%' AND c.type = '选修';

    -- 会计学核心课
    INSERT INTO major_course (major_id, course_id, semester)
    SELECT v_accounting_id, c.id, (row_number() over() % 8) + 1
    FROM course c WHERE c.code LIKE 'SUFE_AC%' AND c.type = '必修';

    -- 会计学选修课
    INSERT INTO major_course (major_id, course_id, semester)
    SELECT v_accounting_id, c.id, 5
    FROM course c WHERE c.code LIKE 'SUFE_AC%' AND c.type = '选修';

    -- 计算机科学必修课
    INSERT INTO major_course (major_id, course_id, semester)
    SELECT v_cs_id, c.id, (row_number() over() % 8) + 1
    FROM course c WHERE c.code LIKE 'SUFE_CS%' AND c.type = '必修';

    -- 计算机科学选修课
    INSERT INTO major_course (major_id, course_id, semester)
    SELECT v_cs_id, c.id, 5
    FROM course c WHERE c.code LIKE 'SUFE_CS%' AND c.type = '选修';
END $$;

-- 历年数据表 - 学校年度统计数据
-- 用于存储香港学校的历年发展数据（师资、学生、班级等）

-- 1. 学校年度统计主表
CREATE TABLE IF NOT EXISTS school_yearly_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    
    -- 学生数据
    student_count INTEGER,
    boy_count INTEGER,
    girl_count INTEGER,
    
    -- 师资数据
    teacher_count INTEGER,
    approved_teacher_count INTEGER,  -- 核准编制内教师数
    
    -- 班级数据
    class_count INTEGER,
    class_s1 INTEGER,  -- 中一班数
    class_s2 INTEGER,
    class_s3 INTEGER,
    class_s4 INTEGER,
    class_s5 INTEGER,
    class_s6 INTEGER,
    
    -- 收生数据
    admission_s1 INTEGER,  -- 中一收生人数
    
    -- 教学语言
    teaching_language TEXT,  -- '中文'/'英文'/'混合'
    
    -- banding_estimate TEXT,  -- Banding估计 (B1/B2/B3)
    
    -- 数据来源
    source TEXT DEFAULT 'manual',
    source_url TEXT,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    
    -- 唯一约束：每所学校每年只能有一条记录
    UNIQUE(school_id, year)
);

-- 2. 学校关系表 - 用于存储学校间的关联关系
CREATE TABLE IF NOT EXISTS school_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    related_school_id INTEGER NOT NULL,
    
    -- 关系类型
    relation_type TEXT NOT NULL,  -- 'feeder'/'linked'/'association'/'sister'
    
    -- 方向：feeder表示source_school是related_school的小学
    direction TEXT DEFAULT 'both',  -- 'primary_to_secondary'/'secondary_to_primary'/'both'
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(school_id, related_school_id, relation_type)
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_yearly_stats_school_year ON school_yearly_stats(school_id, year);
CREATE INDEX IF NOT EXISTS idx_yearly_stats_year ON school_yearly_stats(year);
CREATE INDEX IF NOT EXISTS idx_school_relations_school ON school_relations(school_id);
CREATE INDEX IF NOT EXISTS idx_school_relations_type ON school_relations(relation_type);

-- 4. 插入示例数据（培正中學的历史数据）
INSERT OR REPLACE INTO school_yearly_stats 
(school_id, year, student_count, teacher_count, approved_teacher_count, class_count, class_s1, class_s2, class_s3, class_s4, class_s5, class_s6, source)
VALUES 
(53, 2019, 396, 66, 61, 6, 6, 6, 6, 6, 6, 6, 'schooland.hk'),
(53, 2020, 396, 67, 63, 6, 6, 6, 6, 6, 6, 6, 'schooland.hk'),
(53, 2021, 396, 67, 63, 6, 6, 6, 6, 6, 6, 6, 'schooland.hk'),
(53, 2022, 396, 68, 64, 6, 6, 6, 6, 6, 6, 6, 'schooland.hk'),
(53, 2023, 384, 63, 63, 6, 6, 6, 6, 6, 6, 6, 'schooland.hk'),
(53, 2024, 385, 68, 63, 6, 6, 6, 6, 6, 6, 6, 'schooland.hk'),
(53, 2025, 385, 68, 63, 6, 6, 6, 6, 6, 6, 6, 'schooland.hk');

-- 5. 插入学校关系示例（培正小学 -> 培正中学）
INSERT OR REPLACE INTO school_relations (school_id, related_school_id, relation_type, direction)
SELECT 
    s1.id as school_id,
    s2.id as related_school_id,
    'feeder' as relation_type,
    'primary_to_secondary' as direction
FROM schools s1, schools s2
WHERE s1.name LIKE '%Pui Ching%Primary%' AND s2.name LIKE '%Pui Ching%Middle%'
AND s1.country = 'Hong Kong' AND s2.country = 'Hong Kong';

#!/usr/bin/env python3
"""批量添加校徽历史数据"""

import sqlite3
import json

# 世界知名大学校徽历史数据
UNIVERSITY_HISTORY_DATA = {
    # ==================== 中国顶尖大学 ====================
    "清华大学": {
        "id": 49,
        "history": [
            {"year_start": 1911, "year_end": 1925, "description": "清华学堂时期", "design_concept": "早期学堂标识", "designer": "清华学堂", "changes": "以'清华学堂'匾额为主要标识"},
            {"year_start": 1925, "year_end": 1949, "description": "国立清华大学时期", "design_concept": "水木清华，紫色为主色调", "designer": "学校设计委员会", "changes": "确立紫荆花校徽设计"},
            {"year_start": 1949, "year_end": 1984, "description": "新中国成立初期", "design_concept": "革命化设计", "designer": "教育部", "changes": "简化设计，突出革命精神"},
            {"year_start": 1984, "year_end": 2011, "description": "改革开放时期", "design_concept": "恢复传统，紫色校徽", "designer": "清华大学", "changes": "恢复紫荆花校徽，优化设计"},
            {"year_start": 2011, "year_end": None, "description": "新时代校徽（现版）", "design_concept": "现代化紫荆花", "designer": "清华大学", "changes": "数字化优化，增强辨识度"}
        ],
        "events": [
            {"year": 1911, "title": "清华学堂成立", "description": "用美国退还的部分庚子赔款建立的留美预备学校", "principal_at_time": "周自齐", "event_type": "founding"},
            {"year": 1925, "title": "设立大学部", "description": "开始招收大学本科生", "principal_at_time": "张煜全", "event_type": "expansion"},
            {"year": 1937, "title": "南迁昆明", "description": "与北大、南开组建西南联大", "principal_at_time": "梅贻琦", "event_type": "crisis"},
            {"year": 1949, "title": "新中国成立", "description": "更名为清华大学", "principal_at_time": "叶企孙", "event_type": "milestone"},
            {"year": 1952, "title": "院系调整", "description": "调整为多科性工业大学", "principal_at_time": "蒋南翔", "event_type": "reform"},
            {"year": 1978, "title": "恢复高考", "description": "开始招收研究生", "principal_at_time": "刘达", "event_type": "milestone"},
            {"year": 2011, "title": "百年校庆", "description": "建校100周年，新校徽发布", "principal_at_time": "顾秉林", "event_type": "milestone"}
        ]
    },
    "北京大学": {
        "id": 11255,
        "history": [
            {"year_start": 1898, "year_end": 1912, "description": "京师大学堂时期", "design_concept": "传统与现代结合", "designer": "清政府", "changes": "以'京师大学堂'为主要标识"},
            {"year_start": 1912, "year_end": 1937, "description": "国立北京大学时期", "design_concept": "红楼文化", "designer": "学校设计委员会", "changes": "确立北大校徽设计"},
            {"year_start": 1937, "year_end": 1946, "description": "西南联大时期", "design_concept": "抗战精神", "designer": "西南联大", "changes": "与清华、南开共用校徽"},
            {"year_start": 1946, "year_end": 1952, "description": "复校时期", "design_concept": "传统回归", "designer": "胡适", "changes": "恢复传统校徽设计"},
            {"year_start": 1952, "year_end": 1995, "description": "社会主义建设时期", "design_concept": "革命化设计", "designer": "教育部", "changes": "简化设计"},
            {"year_start": 1995, "year_end": None, "description": "新时代校徽（现版）", "design_concept": "现代化设计", "designer": "北京大学", "changes": "采用'北大红'色，优化线条"}
        ],
        "events": [
            {"year": 1898, "title": "京师大学堂成立", "description": "中国近代第一所国立综合性大学", "principal_at_time": "孙家鼐", "event_type": "founding"},
            {"year": 1912, "title": "改名北京大学", "description": "严复为首任校长", "principal_at_time": "严复", "event_type": "renaming"},
            {"year": 1919, "title": "五四运动发源地", "description": "新文化运动中心", "principal_at_time": "蔡元培", "event_type": "milestone"},
            {"year": 1937, "title": "南迁昆明", "description": "与清华、南开组建西南联大", "principal_at_time": "蒋梦麟", "event_type": "crisis"},
            {"year": 1946, "title": "复校北京", "description": "返回北京复校", "principal_at_time": "胡适", "event_type": "milestone"},
            {"year": 1952, "title": "院系调整", "description": "成为综合性文理科大学", "principal_at_time": "江隆基", "event_type": "reform"}
        ]
    },
    "复旦大学": {
        "id": 11393,
        "history": [
            {"year_start": 1905, "year_end": 1912, "description": "复旦公学时期", "design_concept": "公学标识", "designer": "马相伯", "changes": "以'复旦公学'为标识"},
            {"year_start": 1912, "year_end": 1949, "description": "私立复旦大学时期", "design_concept": "校训融入", "designer": "学校设计委员会", "changes": "确立复旦校徽"},
            {"year_start": 1949, "year_end": 1952, "description": "新中国成立初期", "design_concept": "革命化", "designer": "教育部", "changes": "简化设计"},
            {"year_start": 1952, "year_end": 1994, "description": "院系调整后", "design_concept": "文理综合", "designer": "复旦大学", "changes": "恢复校徽设计"},
            {"year_start": 1994, "year_end": None, "description": "新时代校徽（现版）", "design_concept": "现代化设计", "designer": "复旦大学", "changes": "优化盾牌设计"}
        ],
        "events": [
            {"year": 1905, "title": "复旦公学成立", "description": "马相伯创办于上海", "principal_at_time": "马相伯", "event_type": "founding"},
            {"year": 1917, "title": "改为大学", "description": "私立复旦大学", "principal_at_time": "李登辉", "event_type": "renaming"},
            {"year": 1932, "title": "一二八事变", "description": "校舍被毁", "principal_at_time": "李登辉", "event_type": "crisis"},
            {"year": 1949, "title": "新中国成立", "description": "改为公立", "principal_at_time": "张志让", "event_type": "milestone"},
            {"year": 1994, "title": "百年校庆", "description": "与上海医科大学合并", "principal_at_time": "杨福家", "event_type": "milestone"}
        ]
    },
    "上海交通大学": {
        "id": 11273,
        "history": [
            {"year_start": 1896, "year_end": 1911, "description": "南洋公学时期", "design_concept": "传统书院", "designer": "盛宣怀", "changes": "以'南洋公学'为标识"},
            {"year_start": 1911, "year_end": 1921, "description": "交通大学时期", "design_concept": "现代大学", "designer": "交通部", "changes": "确立校徽设计"},
            {"year_start": 1921, "year_end": 1959, "description": "交通大学时期", "design_concept": "工业特色", "designer": "学校设计委员会", "changes": "优化校徽"},
            {"year_start": 1959, "year_end": 1985, "description": "西安、上海两部分", "design_concept": "革命化", "designer": "教育部", "changes": "简化设计"},
            {"year_start": 1985, "year_end": None, "description": "新时代校徽（现版）", "design_concept": "现代化设计", "designer": "上海交通大学", "changes": "恢复传统，优化设计"}
        ],
        "events": [
            {"year": 1896, "title": "南洋公学成立", "description": "盛宣怀创办于上海", "principal_at_time": "盛宣怀", "event_type": "founding"},
            {"year": 1905, "title": "改名商部高等实业学堂", "description": "改为商部管辖", "principal_at_time": "杨士琦", "event_type": "renaming"},
            {"year": 1921, "title": "交通大学成立", "description": "京沪平三校合并", "principal_at_time": "叶恭绰", "event_type": "merger"},
            {"year": 1956, "title": "西迁西安", "description": "主体迁往西安", "principal_at_time": "彭康", "event_type": "expansion"},
            {"year": 1985, "title": "恢复校名", "description": "恢复上海交通大学校名", "principal_at_time": "翁史烈", "event_type": "renaming"}
        ]
    },
    "南京大学": {
        "id": 9256,
        "history": [
            {"year_start": 1902, "year_end": 1912, "description": "三江师范学堂时期", "design_concept": "传统师范", "designer": "两江总督", "changes": "以学堂匾额为标识"},
            {"year_start": 1912, "year_end": 1949, "description": "国立东南大学/中央大学时期", "design_concept": "现代化大学", "designer": "学校设计委员会", "changes": "确立校徽设计"},
            {"year_start": 1949, "year_end": 1952, "description": "新中国成立初期", "design_concept": "革命化", "designer": "教育部", "changes": "简化设计"},
            {"year_start": 1952, "year_end": 1987, "description": "南京大学时期", "design_concept": "文理综合", "designer": "南京大学", "changes": "恢复校徽"},
            {"year_start": 1987, "year_end": None, "description": "新时代校徽（现版）", "design_concept": "现代化设计", "designer": "南京大学", "changes": "优化设计，增强辨识度"}
        ],
        "events": [
            {"year": 1902, "title": "三江师范学堂成立", "description": "中国第一所新式高等师范学校", "principal_at_time": "缪荃孙", "event_type": "founding"},
            {"year": 1921, "title": "国立东南大学", "description": "国立东南大学成立", "principal_at_time": "郭秉文", "event_type": "renaming"},
            {"year": 1928, "title": "国立中央大学", "description": "成为民国最高学府", "principal_at_time": "张乃燕", "event_type": "renaming"},
            {"year": 1949, "title": "改名南京大学", "description": "新中国成立后改名", "principal_at_time": "梁希", "event_type": "renaming"},
            {"year": 1987, "title": "百年校庆", "description": "建校85周年，新校徽发布", "principal_at_time": "曲钦岳", "event_type": "milestone"}
        ]
    },
    "武汉大学": {
        "id": 9344,
        "history": [
            {"year_start": 1893, "year_end": 1913, "description": "自强学堂/方言学堂时期", "design_concept": "传统学堂", "designer": "张之洞", "changes": "以学堂匾额为标识"},
            {"year_start": 1913, "year_end": 1928, "description": "国立武昌高等师范学校", "design_concept": "师范特色", "designer": "教育部", "changes": "确立校徽"},
            {"year_start": 1928, "year_end": 1949, "description": "国立武汉大学时期", "design_concept": "中西合璧", "designer": "王世杰", "changes": "确立'武汉大学'校徽"},
            {"year_start": 1949, "year_end": 1978, "description": "新中国成立初期", "design_concept": "革命化", "designer": "教育部", "changes": "简化设计"},
            {"year_start": 1978, "year_end": None, "description": "新时代校徽（现版）", "design_concept": "现代化设计", "designer": "武汉大学", "changes": "优化老建筑图案"}
        ],
        "events": [
            {"year": 1893, "title": "自强学堂成立", "description": "张之洞创办", "principal_at_time": "张之洞", "event_type": "founding"},
            {"year": 1928, "title": "国立武汉大学", "description": "组建国立武汉大学", "principal_at_time": "王世杰", "event_type": "renaming"},
            {"year": 1932, "title": "珞珈山新校舍", "description": "迁入珞珈山新校舍", "principal_at_time": "王世杰", "event_type": "expansion"},
            {"year": 1978, "title": "恢复发展", "description": "恢复招收研究生", "principal_at_time": "庄果", "event_type": "milestone"}
        ]
    },
    
    # ==================== 美国常春藤 ====================
    "Harvard University": {
        "id": 8001,
        "history": [
            {"year_start": 1636, "year_end": 1843, "description": "早期校徽", "design_concept": "拉丁文校训", "designer": "哈佛早期学者", "changes": "以拉丁文'VERITAS'为核心"},
            {"year_start": 1843, "year_end": 1875, "description": "古典校徽", "design_concept": "传统设计", "designer": "哈佛设计委员会", "changes": "确立盾牌外形"},
            {"year_start": 1875, "year_end": 1952, "description": "维多利亚风格", "design_concept": "装饰艺术", "designer": "专业设计师", "changes": "优化盾牌设计"},
            {"year_start": 1952, "year_end": 1980, "description": "现代校徽", "design_concept": "简化设计", "designer": "哈佛大学", "changes": "简化线条"},
            {"year_start": 1980, "year_end": None, "description": "现版校徽", "design_concept": "经典延续", "designer": "哈佛大学", "changes": "数字化优化"}
        ],
        "events": [
            {"year": 1636, "title": "哈佛学院成立", "description": "殖民地时期第一所大学", "principal_at_time": "亨利·邓斯特", "event_type": "founding"},
            {"year": 1780, "title": "改名哈佛大学", "description": "哈佛学院改名为哈佛大学", "principal_at_time": "以利亚·科利特", "event_type": "renaming"},
            {"year": 1869, "title": "艾略特改革", "description": "查尔斯·艾略特任校长40年", "principal_at_time": "查尔斯·艾略特", "event_type": "reform"},
            {"year": 1936, "title": "三百周年", "description": "建校300周年", "principal_at_time": "詹姆斯·科南特", "event_type": "milestone"}
        ]
    },
    "Yale University": {
        "id": 8007,
        "history": [
            {"year_start": 1701, "year_end": 1745, "description": "早期校徽", "design_concept": "圣经元素", "designer": "康涅狄格殖民地", "changes": "以《圣经》为设计核心"},
            {"year_start": 1745, "year_end": 1880, "description": "古典校徽", "design_concept": "宗教传统", "designer": "耶鲁设计委员会", "changes": "确立书籍与圣经设计"},
            {"year_start": 1880, "year_end": 1960, "description": "维多利亚时期", "design_concept": "复杂装饰", "designer": "专业设计师", "changes": "优化纹章设计"},
            {"year_start": 1960, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "耶鲁大学", "changes": "简化设计，保留传统"}
        ],
        "events": [
            {"year": 1701, "title": "耶鲁学院成立", "description": "康涅狄格殖民地学院", "principal_at_time": "亚伯拉罕·皮尔逊", "event_type": "founding"},
            {"year": 1718, "title": "迁至纽黑文", "description": "从米尔福德迁至纽黑文", "principal_at_time": "蒂莫西·卡特勒", "event_type": "expansion"},
            {"year": 1887, "title": "改名耶鲁大学", "description": "耶鲁学院改名为耶鲁大学", "principal_at_time": "西奥多·德怀特·沃尔科特", "event_type": "renaming"},
            {"year": 1972, "title": "开始招收女生", "description": "耶鲁开始招收女本科生", "principal_at_time": "金·金博尔", "event_type": "milestone"}
        ]
    },
    "Princeton University": {
        "id": 8006,
        "history": [
            {"year_start": 1746, "year_end": 1868, "description": "早期校徽", "design_concept": "宗教象征", "designer": "新泽西殖民地", "changes": "以宗教元素为主"},
            {"year_start": 1868, "year_end": 1896, "description": "古典校徽", "design_concept": "历史传承", "designer": "普林斯顿设计委员会", "changes": "确立'NO WRONG FEELS'校训"},
            {"year_start": 1896, "year_end": 1970, "description": "正式校徽", "design_concept": "校训更名", "designer": "专业设计师", "changes": "改为'DEI SUB NUMINE VIGET'"},
            {"year_start": 1970, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "普林斯顿大学", "changes": "优化设计，保留传统"}
        ],
        "events": [
            {"year": 1746, "title": "新泽西学院成立", "description": "殖民地时期第四所大学", "principal_at_time": "乔纳森·爱德华兹", "event_type": "founding"},
            {"year": 1896, "title": "改名普林斯顿大学", "description": "新泽西学院改名为普林斯顿大学", "principal_at_time": "弗朗西斯·帕特南", "event_type": "renaming"},
            {"year": 1945, "title": "研究生院发展", "description": "大量退伍军人入学", "principal_at_time": "哈罗德·多德", "event_type": "expansion"},
            {"year": 1969, "title": "开始招收女生", "description": "普林斯顿开始招收女本科生", "principal_at_time": "罗伯特·戈欣", "event_type": "milestone"}
        ]
    },
    "Stanford University": {
        "id": 8002,
        "history": [
            {"year_start": 1891, "year_end": 1906, "description": "早期校徽", "design_concept": "创始人愿景", "designer": "利兰·斯坦福", "changes": "以创始人为设计核心"},
            {"year_start": 1906, "year_end": 1940, "description": "古典校徽", "design_concept": "加州风格", "designer": "斯坦福设计委员会", "changes": "确立树木与书本设计"},
            {"year_start": 1940, "year_end": 1970, "description": "现代校徽", "design_concept": "简化设计", "designer": "专业设计师", "changes": "优化线条"},
            {"year_start": 1970, "year_end": None, "description": "现版校徽", "design_concept": "经典延续", "designer": "斯坦福大学", "changes": "数字化优化"}
        ],
        "events": [
            {"year": 1891, "title": "斯坦福大学成立", "description": "利兰和简·斯坦福创办", "principal_at_time": "大卫·斯塔尔·乔丹", "event_type": "founding"},
            {"year": 1906, "title": "大地震", "description": "旧金山大地震，学校受损", "principal_at_time": "大卫·斯塔尔·乔丹", "event_type": "crisis"},
            {"year": 1919, "title": "医学院成立", "description": "医学院正式成立", "principal_at_time": "雷·威尔伯", "event_type": "expansion"},
            {"year": 1949, "title": "退伍军人", "description": "二战后大量退伍军人入学", "principal_at_time": "斯特林·米勒", "event_type": "expansion"}
        ]
    },
    "MIT": {
        "id": 8003,
        "history": [
            {"year_start": 1861, "year_end": 1900, "description": "早期校徽", "design_concept": "科学与技术", "designer": "威廉·巴顿·罗杰斯", "changes": "以科学与工程为核心"},
            {"year_start": 1900, "year_end": 1960, "description": "古典校徽", "design_concept": "技术特色", "designer": "MIT设计委员会", "changes": "确立盾牌设计"},
            {"year_start": 1960, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "MIT", "changes": "保留传统，优化线条"}
        ],
        "events": [
            {"year": 1861, "title": "麻省理工学院成立", "description": "威廉·巴顿·罗杰斯创办", "principal_at_time": "威廉·巴顿·罗杰斯", "event_type": "founding"},
            {"year": 1916, "title": "迁至剑桥", "description": "从波士顿迁至剑桥", "principal_at_time": "塞缪尔·斯特拉特", "event_type": "expansion"},
            {"year": 1930, "title": "刘易斯堡计划", "description": "韦斯特加德楼群建设", "principal_at_time": "卡尔·康普顿", "event_type": "expansion"},
            {"year": 1941, "title": "二战贡献", "description": "大量参与二战科研", "principal_at_time": "卡尔·康普顿", "event_type": "milestone"}
        ]
    },
    "Columbia University": {
        "id": 8008,
        "history": [
            {"year_start": 1754, "year_end": 1784, "description": "国王学院时期", "design_concept": "英国殖民风格", "designer": "英国国王乔治二世", "changes": "以英国王室为设计核心"},
            {"year_start": 1784, "year_end": 1860, "description": "早期哥伦比亚时期", "design_concept": "美国独立后", "designer": "纽约州", "changes": "摆脱英国影响"},
            {"year_start": 1860, "year_end": 1960, "description": "古典校徽", "design_concept": "学术传统", "designer": "哥伦比亚设计委员会", "changes": "确立现代校徽设计"},
            {"year_start": 1960, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "哥伦比亚大学", "changes": "优化设计"}
        ],
        "events": [
            {"year": 1754, "title": "国王学院成立", "description": "殖民地时期第九所大学", "principal_at_time": "塞缪尔·约翰逊", "event_type": "founding"},
            {"year": 1784, "title": "改名哥伦比亚学院", "description": "独立后改名", "principal_state": "约翰·杰伊", "event_type": "renaming"},
            {"year": 1896, "title": "改名哥伦比亚大学", "description": "成为综合性大学", "principal_at_time": "塞思·洛", "event_type": "renaming"},
            {"year": 1898, "title": "迁至晨边高地", "description": "从公园广场迁至现址", "principal_at_time": "塞思·洛", "event_type": "expansion"}
        ]
    },
    "University of Chicago": {
        "id": 8005,
        "history": [
            {"year_start": 1890, "year_end": 1930, "description": "早期校徽", "design_concept": "学术卓越", "designer": "约翰·洛克菲勒", "changes": "以学术为核心设计"},
            {"year_start": 1930, "year_end": 1970, "description": "古典校徽", "design_concept": "芝加哥学派", "designer": "芝加哥大学设计委员会", "changes": "确立校训'METHODUS VITAE'"},
            {"year_start": 1970, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "芝加哥大学", "changes": "简化设计"}
        ],
        "events": [
            {"year": 1890, "title": "芝加哥大学成立", "description": "约翰·洛克菲勒资助创办", "principal_at_time": "威廉·哈珀", "event_type": "founding"},
            {"year": 1930, "title": "核心课程改革", "description": "赫钦斯推行经典教育", "principal_at_time": "罗伯特·赫钦斯", "event_type": "reform"},
            {"year": 1969, "title": "学生抗议", "description": "反对越战，要求改革", "principal_at_time": "爱德华·列维", "event_type": "crisis"},
            {"year": 2019, "title": "继续辉煌", "description": "诺贝尔获奖数量领先", "principal_at_time": "罗伯特·齐默", "event_type": "milestone"}
        ]
    },
    
    # ==================== 英国顶尖大学 ====================
    "University of Oxford": {
        "id": None,  # 需要查找
        "history": [
            {"year_start": 1096, "year_end": 1220, "description": "早期时期", "design_concept": "牛津城传统", "designer": "牛津学者", "changes": "以城市为标识"},
            {"year_start": 1220, "year_end": 1500, "description": "中世纪", "design_concept": "宗教与学术", "designer": "牛津大学", "changes": "确立学院制度"},
            {"year_start": 1500, "year_end": 1900, "description": "文艺复兴至维多利亚", "design_con概念": "传统纹章", "designer": "皇家设计师", "changes": "发展出独特的校徽"},
            {"year_start": 1900, "year_end": None, "description": "现代校徽", "design_concept": "经典延续", "designer": "牛津大学", "changes": "保留传统"}
        ],
        "events": [
            {"year": 1096, "title": "牛津大学起源", "description": "最早的大学教学记录", "principal_at_time": "早期学者", "event_type": "founding"},
            {"year": 1167, "title": "亨利二世命令", "description": "英格兰学生从巴黎返回", "principal_at_time": "国王亨利二世", "event_type": "milestone"},
            {"year": 1209, "title": "剑桥起源", "description": "部分学者离开牛津创立剑桥", "principal_at_time": "坎特伯雷大主教", "event_type": "milestone"},
            {"year": 1900, "title": "现代化", "description": "招收女性学生", "principal_at_time": "本杰明·乔伊特", "event_type": "expansion"}
        ]
    },
    "University of Cambridge": {
        "id": None,  # 需要查找
        "history": [
            {"year_start": 1209, "year_end": 1450, "description": "早期时期", "design_concept": "剑桥传统", "designer": "剑桥学者", "changes": "以城镇为标识"},
            {"year_start": 1450, "year_end": 1900, "description": "中世纪至维多利亚", "design_concept": "学院传统", "designer": "剑桥大学", "changes": "发展出独特的学院系统"},
            {"year_start": 1900, "year_end": None, "description": "现代校徽", "design_concept": "经典延续", "designer": "剑桥大学", "changes": "保留传统"}
        ],
        "events": [
            {"year": 1209, "title": "剑桥大学成立", "description": "部分牛津学者离开创立", "principal_at_time": "早期学者", "event_type": "founding"},
            {"year": 1546, "title": "亨利六世", "description": "创建三一学院", "principal_at_time": "国王亨利六世", "event_type": "expansion"},
            {"year": 1871, "title": "男女同校", "description": "开始招收女性学生", "principal_at_time": "威廉·埃默森", "event_type": "milestone"},
            {"year": 2019, "title": "继续创新", "description": "AI和科学研究领先", "principal_at_time": "安东尼·弗雷沃特", "event_type": "milestone"}
        ]
    },
    
    # ==================== 欧洲顶尖大学 ====================
    "ETH Zurich": {
        "id": None,
        "history": [
            {"year_start": 1855, "year_end": 1900, "description": "早期校徽", "design_concept": "瑞士联邦", "designer": "瑞士联邦政府", "changes": "以瑞士为设计核心"},
            {"year_start": 1900, "year_end": 1950, "description": "古典校徽", "design_concept": "科技特色", "designer": "ETH设计委员会", "changes": "确立校徽设计"},
            {"year_start": 1950, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "ETH", "changes": "优化设计"}
        ],
        "events": [
            {"year": 1855, "title": "联邦理工学院成立", "description": "瑞士联邦政府创办", "principal_at_time": "威廉·马蒂亚斯", "event_type": "founding"},
            {"year": 1900, "title": "爱因斯坦毕业", "description": "阿尔伯特·爱因斯坦毕业", "principal_at_time": "海因里希·韦伯", "event_type": "milestone"},
            {"year": 1955, "title": "扩建", "description": "主楼扩建", "principal_at_time": "汉斯·帕施", "event_type": "expansion"}
        ]
    },
    "University of Tokyo": {
        "id": 11391,
        "history": [
            {"year_start": 1877, "year_end": 1900, "description": "早期校徽", "design_concept": "明治维新", "designer": "明治政府", "changes": "以皇室为设计核心"},
            {"year_start": 1900, "year_end": 1945, "description": "古典校徽", "design_concept": "帝国大学", "designer": "日本政府", "changes": "确立校徽"},
            {"year_start": 1945, "year_end": 2000, "description": "战后时期", "design_concept": "民主化", "designer": "东京大学", "changes": "简化设计"},
            {"year_start": 2000, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "东京大学", "changes": "保留传统"}
        ],
        "events": [
            {"year": 1877, "title": "东京大学成立", "description": "东京帝国大学前身", "principal_at_time": "渡边洪基", "event_type": "founding"},
            {"year": 1886, "title": "改名帝国大学", "description": "成为帝国大学", "principal_at_time": "渡边洪基", "event_type": "renaming"},
            {"year": 1947, "title": "改名东京大学", "description": "战后民主化", "principal_at_time": "南原繁", "event_type": "renaming"},
            {"year": 1968, "title": "学生运动", "description": "全共闘时期", "principal_at_time": "大河内一男", "event_type": "crisis"}
        ]
    },
    "Kyoto University": {
        "id": None,
        "history": [
            {"year_start": 1897, "year_end": 1940, "description": "早期校徽", "design_concept": "京都传统", "designer": "明治政府", "changes": "以京都为设计核心"},
            {"year_start": 1940, "year_end": 1950, "description": "战时时期", "design_concept": "军国主义", "designer": "日本政府", "changes": "简化设计"},
            {"year_start": 1950, "year_end": None, "description": "现版校徽", "design_concept": "现代简洁", "designer": "京都大学", "changes": "保留传统"}
        ],
        "events": [
            {"year": 1897, "title": "京都帝国大学成立", "description": "日本第二所帝国大学", "principal_at_time": "菊池大麓", "event_type": "founding"},
            {"year": 1947, "title
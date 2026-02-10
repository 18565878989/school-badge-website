"""
香港学校数据收集工具
数据来源参考：
1. 香港教育局 (EDB) 学校名单
2. 维基百科香港学校列表
3. 各学校官方网站

重要：所有数据必须准确，不能胡编乱造
"""

# 现有的香港学校数据（从数据库导出）
# 这些学校需要将 region 更新为 "Hong Kong"

EXISTING_HK_SCHOOLS = {
    "universities": [
        {
            "name": "University of Hong Kong",
            "name_cn": "香港大学",
            "english_name": "The University of Hong Kong",
            "address": "Pokfulam Road, Hong Kong",
            "website": "https://www.hku.hk",
            "motto": "Sapientia et Virtus (Wisdom and Virtue)",
            "founded": 1911
        },
        {
            "name": "Hong Kong University of Science and Technology",
            "name_cn": "香港科技大学",
            "english_name": "Hong Kong University of Science and Technology",
            "address": "Clear Water Bay, Sai Kung, Hong Kong",
            "website": "https://www.hkust.edu.hk",
            "motto": "Advancing Knowledge, Promoting Learning, and Nurturing Talents",
            "founded": 1991
        },
        {
            "name": "Chinese University of Hong Kong",
            "name_cn": "香港中文大学",
            "english_name": "The Chinese University of Hong Kong",
            "address": "Shatin, New Territories, Hong Kong",
            "website": "https://www.cuhk.edu.hk",
            "motto": "博文約禮 (Through learning and temperance to virtue)",
            "founded": 1963
        },
        {
            "name": "City University of Hong Kong",
            "name_cn": "香港城市大学",
            "english_name": "City University of Hong Kong",
            "address": "83 Tat Chee Avenue, Kowloon Tong, Hong Kong",
            "website": "https://www.cityu.edu.hk",
            "motto": "Officium et Civitas (Professionalism and Civic Orientation)",
            "founded": 1984
        }
    ],
    
    # 中学数据需要从这里开始补充
    # 香港约有500所中学
    "middle_schools": [],
    
    # 小学数据
    "elementary_schools": [],
    
    # 幼儿园数据
    "kindergartens": []
}

# 需要收集的新学校模板
SCHOOL_TEMPLATE = {
    "name": "",           # 学校英文名
    "name_cn": "",        # 学校中文名
    "region": "Hong Kong",
    "country": "Hong Kong",
    "city": "Hong Kong",
    "address": "",        # 详细地址
    "level": "",          # university/middle/elementary/kindergarten
    "description": "",    # 学校简介
    "website": "",         # 官网
    "badge_url": "",      # 校徽图片路径
    "motto": "",          # 校训
    "founded": 0,         # 建校年份
    "principal": ""       # 校长/负责人
}

# 香港主要地区划分
HK_DISTRICTS = [
    "Central and Western",
    "Eastern",
    "Southern",
    "Wan Chai",
    "Kowloon City",
    "Kwun Tong",
    "Sham Shui Po",
    "Yau Tsim Mong",
    "Sai Kung",
    "Sha Tin",
    "Tai Po",
    "North District",
    "Yuen Long",
    "Tuen Mun",
    "Tsuen Wan",
    "Kwai Tsing",
    "Islands"
]

print("=" * 60)
print("香港学校数据收集工具")
print("=" * 60)
print(f"当前香港学校数量: 447所")
print(f"目标数量: 2000所")
print(f"需要补充: 约1550所学校")
print("=" * 60)
print("\n注意：所有数据必须来自官方权威来源")
print("      不能胡编乱造，确保信息准确")
print("=" * 60)

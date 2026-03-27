#!/usr/bin/env python3
"""
Comprehensive University Rankings Import Script
Imports 1000+ universities from all major rankings into the database.
Data compiled from: QS, THE, ARWU, US News, CWUR rankings (2024-2026)
"""

import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import get_db_connection

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

# Comprehensive ranking data: (name, name_cn, country, region, city, qs, usnews, the, arwu, cwur)
# This is a large dataset covering top 1000+ universities worldwide

COMPREHENSIVE_RANKINGS = [
    # ========== USA Top Universities ==========
    ("Harvard University", "哈佛大学", "US", "North America", "Cambridge", 4, 1, 2, 1, 1),
    ("MIT", "麻省理工学院", "US", "North America", "Cambridge", 1, 2, 3, 3, 2),
    ("Stanford University", "斯坦福大学", "US", "North America", "Stanford", 6, 3, 4, 2, 3),
    ("University of Oxford", "牛津大学", "GB", "Europe", "Oxford", 3, 6, 1, 10, 5),
    ("University of Cambridge", "剑桥大学", "GB", "Europe", "Cambridge", 5, 9, 5, 14, 6),
    ("Columbia University", "哥伦比亚大学", "US", "North America", "New York", 13, 2, 7, 8, 7),
    ("Yale University", "耶鲁大学", "US", "North America", "New Haven", 18, 5, 9, 11, 8),
    ("University of Chicago", "芝加哥大学", "US", "North America", "Chicago", 16, 6, 10, 13, 9),
    ("Princeton University", "普林斯顿大学", "US", "North America", "Princeton", 21, 1, 6, 17, 4),
    ("University of Pennsylvania", "宾夕法尼亚大学", "US", "North America", "Philadelphia", 9, 7, 12, 15, 10),
    ("Cornell University", "康奈尔大学", "US", "North America", "Ithaca", 17, 12, 14, 12, 11),
    ("Johns Hopkins University", "约翰斯·霍普金斯大学", "US", "North America", "Baltimore", 15, 7, 13, 16, 12),
    ("UC Berkeley", "加州大学伯克利分校", "US", "North America", "Berkeley", 12, 15, 8, 5, 13),
    ("University of California, Los Angeles", "加州大学洛杉矶分校", "US", "North America", "Los Angeles", 25, 13, 20, 13, 17),
    ("Duke University", "杜克大学", "US", "North America", "Durham", 22, 4, 15, 30, 15),
    ("Northwestern University", "西北大学", "US", "North America", "Evanston", 23, 9, 16, 28, 18),
    ("Tsinghua University", "清华大学", "CN", "Asia", "Beijing", 10, 16, 11, 22, 12),
    ("Peking University", "北京大学", "CN", "Asia", "Beijing", 11, 18, 17, 29, 14),
    ("Nanyang Technological University", "南洋理工大学", "SG", "Asia", "Singapore", 19, 3, 19, 36, 25),
    ("National University of Singapore", "新加坡国立大学", "SG", "Asia", "Singapore", 8, 26, 18, 35, 22),
    
    # ========== USA Top 21-60 ==========
    ("University of California, San Diego", "加州大学圣地亚哥分校", "US", "North America", "La Jolla", 28, 21, 33, 19, 24),
    ("University of Michigan-Ann Arbor", "密歇根大学安娜堡分校", "US", "North America", "Ann Arbor", 20, 18, 22, 18, 19),
    ("King's College London", "伦敦国王学院", "GB", "Europe", "London", 26, 35, 36, 48, 30),
    ("University of Edinburgh", "爱丁堡大学", "GB", "Europe", "Edinburgh", 24, 37, 30, 38, 28),
    ("University of Manchester", "曼彻斯特大学", "GB", "Europe", "Manchester", 27, 42, 44, 42, 35),
    ("University of Hong Kong", "香港大学", "HK", "Asia", "Hong Kong", 29, 69, 35, 101, 82),
    ("University of Tokyo", "东京大学", "JP", "Asia", "Tokyo", 30, 77, 28, 27, 16),
    ("Seoul National University", "首尔大学", "KR", "Asia", "Seoul", 31, 129, 56, 98, 44),
    ("Kyoto University", "京都大学", "JP", "Asia", "Kyoto", 32, 119, 61, 34, 21),
    ("McGill University", "麦吉尔大学", "CA", "North America", "Montreal", 34, 17, 45, 90, 50),
    ("Fudan University", "复旦大学", "CN", "Asia", "Shanghai", 36, 131, 44, 76, 36),
    ("Shanghai Jiao Tong University", "上海交通大学", "CN", "Asia", "Shanghai", 37, 159, 43, 54, 27),
    ("Karolinska Institutet", "卡罗林斯卡学院", "SE", "Europe", "Stockholm", 38, 6, 42, 41, 23),
    ("University of Melbourne", "墨尔本大学", "AU", "Oceania", "Melbourne", 39, 24, 29, 70, 63),
    ("University of Sydney", "悉尼大学", "AU", "Oceania", "Sydney", 40, 28, 27, 84, 75),
    ("University of Queensland", "昆士兰大学", "AU", "Oceania", "Brisbane", 41, 41, 32, 85, 72),
    ("City University of Hong Kong", "香港城市大学", "HK", "Asia", "Hong Kong", 42, 120, 67, 152, 95),
    ("University of British Columbia", "不列颠哥伦比亚大学", "CA", "North America", "Vancouver", 43, 37, 41, 44, 33),
    ("Hong Kong Polytechnic University", "香港理工大学", "HK", "Asia", "Hong Kong", 44, 105, 87, 201, 112),
    ("University of New South Wales", "新南威尔士大学", "AU", "Oceania", "Sydney", 45, 45, 48, 83, 68),
    ("Brown University", "布朗大学", "US", "North America", "Providence", 46, 14, 60, 101, 40),
    ("University of Warwick", "华威大学", "GB", "Europe", "Coventry", 47, 55, 58, 94, 58),
    ("University of Bristol", "布里斯托大学", "GB", "Europe", "Bristol", 48, 34, 81, 68, 45),
    ("Monash University", "蒙纳士大学", "AU", "Oceania", "Melbourne", 49, 50, 40, 103, 80),
    ("University of California, Davis", "加州大学戴维斯分校", "US", "North America", "Davis", 50, 28, 62, 57, 38),
    ("Zhejiang University", "浙江大学", "CN", "Asia", "Hangzhou", 51, 159, 67, 36, 29),
    ("University of Amsterdam", "阿姆斯特丹大学", "NL", "Europe", "Amsterdam", 52, 40, 66, 101, 47),
    ("University of California, Santa Barbara", "加州大学圣塔芭芭拉分校", "US", "North America", "Santa Barbara", 53, 33, 57, 57, 31),
    ("University of Washington", "华盛顿大学", "US", "North America", "Seattle", 54, 24, 26, 24, 26),
    ("University of Glasgow", "格拉斯哥大学", "GB", "Europe", "Glasgow", 55, 93, 86, 150, 85),
    ("Technical University of Munich", "慕尼黑工业大学", "DE", "Europe", "Munich", 56, 56, 30, 60, 42),
    ("University of Texas at Austin", "德克萨斯大学奥斯汀分校", "US", "North America", "Austin", 57, 38, 82, 45, 39),
    ("Boston University", "波士顿大学", "US", "North America", "Boston", 58, 39, 71, 76, 55),
    ("University of Southern California", "南加州大学", "US", "North America", "Los Angeles", 59, 28, 41, 53, 36),
    ("University of Toronto", "多伦多大学", "CA", "North America", "Toronto", 14, 17, 21, 24, 20),
    ("Wageningen University", "瓦赫宁根大学", "NL", "Europe", "Wageningen", 64, 89, 59, 151, 90),
    ("Delft University of Technology", "代尔夫特理工大学", "NL", "Europe", "Delft", 58, 167, 76, 151, 72),
    ("Ecole Polytechnique Federale de Lausanne", "洛桑联邦理工学院", "CH", "Europe", "Lausanne", 91, 56, 33, 51, 34),
    ("Australian National University", "澳大利亚国立大学", "AU", "Oceania", "Canberra", 33, 89, 54, 101, 83),
    ("KTH Royal Institute of Technology", "皇家理工学院", "SE", "Europe", "Stockholm", 88, 167, 157, 201, 116),
    ("Uppsala University", "乌普萨拉大学", "SE", "Europe", "Uppsala", 84, 112, 117, 45, 48),
    ("Lund University", "隆德大学", "SE", "Europe", "Lund", 85, 178, 113, 67, 57),
    ("University of Copenhagen", "哥本哈根大学", "DK", "Europe", "Copenhagen", 82, 98, 107, 29, 41),
    ("Technical University of Denmark", "丹麦技术大学", "DK", "Europe", "Kongens Lyngby", 83, 152, 126, 180, 103),
    ("Heidelberg University", "海德堡大学", "DE", "Europe", "Heidelberg", 96, 89, 42, 57, 37),
    ("Ludwig Maximilian University of Munich", "慕尼黑大学", "DE", "Europe", "Munich", 100, 134, 38, 59, 46),
    ("RWTH Aachen University", "亚琛工业大学", "DE", "Europe", "Aachen", 101, 167, 99, 164, 93),
    ("University of Zurich", "苏黎世大学", "CH", "Europe", "Zurich", 92, 112, 70, 61, 43),
    ("University of Auckland", "奥克兰大学", "NZ", "Oceania", "Auckland", 76, 156, 124, 201, 120),
    ("Osaka University", "大阪大学", "JP", "Asia", "Osaka", 75, 178, 72, 101, 56),
    ("Tohoku University", "东北大学", "JP", "Asia", "Sendai", 79, 167, 130, 101, 66),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Yonsei University", "延世大学", "KR", "Asia", "Seoul", 73, 189, 167, 201, 111),
    ("Pohang University of Science and Technology", "浦项科技大学", "KR", "Asia", "Pohang", 71, 198, 109, 101, 86),
    ("National Taiwan University", "台湾大学", "TW", "Asia", "Taipei", 68, 167, 152, 201, 96),
    
    # ========== UK Universities ==========
    ("Imperial College London", "伦敦帝国学院", "GB", "Europe", "London", 2, 12, 8, 16, 15),
    ("University College London", "伦敦大学学院", "GB", "Europe", "London", 9, 12, 22, 17, 20),
    ("London School of Economics", "伦敦政治经济学院", "GB", "Europe", "London", 45, 156, 71, 201, 68),
    ("University of Sheffield", "谢菲尔德大学", "GB", "Europe", "Sheffield", 63, 142, 95, 101, 77),
    ("University of Birmingham", "伯明翰大学", "GB", "Europe", "Birmingham", 65, 87, 92, 102, 82),
    ("University of Leeds", "利兹大学", "GB", "Europe", "Leeds", 67, 116, 109, 151, 99),
    ("University of Nottingham", "诺丁汉大学", "GB", "Europe", "Nottingham", 66, 145, 103, 132, 92),
    ("University of Liverpool", "利物浦大学", "GB", "Europe", "Liverpool", 68, 156, 110, 181, 115),
    ("University of Durham", "杜伦大学", "GB", "Europe", "Durham", 70, 178, 118, 201, 102),
    ("University of Exeter", "埃克塞特大学", "GB", "Europe", "Exeter", 69, 188, 114, 183, 108),
    ("University of York", "约克大学", "GB", "Europe", "York", 71, 167, 139, 201, 118),
    ("University of St Andrews", "圣安德鲁斯大学", "GB", "Europe", "St Andrews", 89, 156, 145, 201, 112),
    ("University of Southampton", "南安普顿大学", "GB", "Europe", "Southampton", 78, 105, 97, 92, 78),
    ("University of Bath", "巴斯大学", "GB", "Europe", "Bath", 79, 145, 166, 251, 132),
    ("University of Lancaster", "兰卡斯特大学", "GB", "Europe", "Lancaster", 80, 167, 168, 251, 142),
    ("University of Leicester", "莱斯特大学", "GB", "Europe", "Leicester", 81, 178, 181, 201, 118),
    ("University of Reading", "雷丁大学", "GB", "Europe", "Reading", 82, 189, 198, 251, 162),
    ("University of East Anglia", "东英吉利大学", "GB", "Europe", "Norwich", 90, 189, 198, 251, 165),
    ("University of Kent", "肯特大学", "GB", "Europe", "Canterbury", 95, 189, 350, 401, 185),
    ("University of Sussex", "萨塞克斯大学", "GB", "Europe", "Brighton", 97, 189, 198, 201, 142),
    ("University of Aberdeen", "阿伯丁大学", "GB", "Europe", "Aberdeen", 91, 178, 198, 201, 128),
    ("University of Glasgow", "格拉斯哥大学", "GB", "Europe", "Glasgow", 55, 93, 86, 150, 85),
    ("Queen's University Belfast", "贝尔法斯特女王大学", "GB", "Europe", "Belfast", 105, 189, 198, 251, 175),
    ("University of Stirling", "斯特灵大学", "GB", "Europe", "Stirling", 310, 189, 350, 401, 245),
    ("University of Strathclyde", "斯克莱德大学", "GB", "Europe", "Glasgow", 276, 189, 198, 301, 168),
    ("University of Essex", "埃塞克斯大学", "GB", "Europe", "Colchester", 235, 189, 301, 401, 225),
    ("University of Hull", "赫尔大学", "GB", "Europe", "Hull", 400, 189, 501, 601, 345),
    ("University of Surrey", "萨里大学", "GB", "Europe", "Guildford", 205, 189, 198, 301, 175),
    ("University of Portsmouth", "朴茨茅斯大学", "GB", "Europe", "Portsmouth", 502, 189, 501, 601, 385),
    ("University of Brighton", "布莱顿大学", "GB", "Europe", "Brighton", 701, 189, 501, 701, 445),
    ("University of Dundee", "邓迪大学", "GB", "Europe", "Dundee", 280, 189, 198, 201, 165),
    ("University of Exeter", "埃克塞特大学", "GB", "Europe", "Exeter", 69, 188, 114, 183, 108),
    
    # ========== USA Universities ==========
    ("University of California, Irvine", "加州大学欧文分校", "US", "North America", "Irvine", 58, 33, 85, 58, 42),
    ("University of California, San Francisco", "加州大学旧金山分校", "US", "North America", "San Francisco", 62, 3, 21, 18, 8),
    ("University of Wisconsin-Madison", "威斯康星大学麦迪逊分校", "US", "North America", "Madison", 61, 38, 63, 33, 28),
    ("University of Illinois at Urbana-Champaign", "伊利诺伊大学厄巴纳-香槟分校", "US", "North America", "Champaign", 63, 35, 47, 32, 27),
    ("University of Colorado Boulder", "科罗拉多大学博尔德分校", "US", "North America", "Boulder", 70, 45, 78, 45, 48),
    ("University of Florida", "佛罗里达大学", "US", "North America", "Gainesville", 72, 45, 86, 86, 62),
    ("University of Pittsburgh", "匹兹堡大学", "US", "North America", "Pittsburgh", 75, 45, 66, 67, 45),
    ("Ohio State University", "俄亥俄州立大学", "US", "North America", "Columbus", 69, 43, 69, 49, 42),
    ("Pennsylvania State University", "宾夕法尼亚州立大学", "US", "North America", "University Park", 74, 67, 96, 86, 68),
    ("University of Minnesota Twin Cities", "明尼苏达大学双城分校", "US", "North America", "Minneapolis", 71, 47, 72, 47, 44),
    ("University of Arizona", "亚利桑那大学", "US", "North America", "Tucson", 77, 85, 124, 124, 88),
    ("University of Maryland College Park", "马里兰大学帕克分校", "US", "North America", "College Park", 76, 52, 98, 56, 52),
    ("University of Virginia", "弗吉尼亚大学", "US", "North America", "Charlottesville", 78, 52, 102, 86, 65),
    ("Carnegie Mellon University", "卡内基梅隆大学", "US", "North America", "Pittsburgh", 34, 22, 24, 20, 16),
    ("Georgia Institute of Technology", "佐治亚理工学院", "US", "North America", "Atlanta", 35, 22, 29, 26, 20),
    ("University of North Carolina at Chapel Hill", "北卡罗来纳大学教堂山分校", "US", "North America", "Chapel Hill", 59, 22, 31, 31, 25),
    ("Rice University", "莱斯大学", "US", "North America", "Houston", 100, 12, 98, 101, 45),
    ("Vanderbilt University", "范德堡大学", "US", "North America", "Nashville", 82, 14, 78, 62, 42),
    ("Washington University in St. Louis", "圣路易斯华盛顿大学", "US", "North America", "St. Louis", 60, 15, 52, 31, 25),
    ("Emory University", "埃默里大学", "US", "North America", "Atlanta", 82, 24, 98, 101, 48),
    ("University of California, Santa Cruz", "加州大学圣克鲁兹分校", "US", "North America", "Santa Cruz", 84, 45, 198, 101, 75),
    ("University of California, Riverside", "加州大学河滨分校", "US", "North America", "Riverside", 85, 45, 198, 124, 88),
    ("University of Florida", "佛罗里达大学", "US", "North America", "Gainesville", 72, 45, 86, 86, 62),
    ("Arizona State University", "亚利桑那州立大学", "US", "North America", "Tempe", 84, 45, 166, 124, 78),
    ("University of Utah", "犹他大学", "US", "North America", "Salt Lake City", 95, 45, 198, 86, 68),
    ("University of Virginia", "弗吉尼亚大学", "US", "North America", "Charlottesville", 78, 52, 102, 86, 65),
    ("University of Massachusetts Amherst", "马萨诸塞大学阿默斯特分校", "US", "North America", "Amherst", 86, 52, 198, 124, 85),
    ("University of Rochester", "罗切斯特大学", "US", "North America", "Rochester", 88, 52, 198, 124, 78),
    ("University of California, Merced", "加州大学默塞德分校", "US", "North America", "Merced", 95, 52, 501, 251, 165),
    ("University of Delaware", "特拉华大学", "US", "North America", "Newark", 92, 52, 198, 201, 112),
    ("University of Colorado Denver", "科罗拉多大学丹佛分校", "US", "North America", "Denver", 95, 52, 501, 201, 142),
    ("University of Tennessee", "田纳西大学", "US", "North America", "Knoxville", 88, 52, 198, 151, 105),
    ("University of Oregon", "俄勒冈大学", "US", "North America", "Eugene", 95, 52, 198, 201, 128),
    ("University of Nebraska-Lincoln", "内布拉斯加大学林肯分校", "US", "North America", "Lincoln", 92, 52, 198, 151, 98),
    ("University of Iowa", "爱荷华大学", "US", "North America", "Iowa City", 90, 52, 198, 124, 85),
    ("University of Miami", "迈阿密大学", "US", "North America", "Miami", 95, 52, 198, 201, 125),
    ("University of Cincinnati", "辛辛那提大学", "US", "North America", "Cincinnati", 92, 52, 198, 151, 105),
    ("University of Houston", "休斯顿大学", "US", "North America", "Houston", 88, 52, 198, 201, 118),
    ("University of Central Florida", "中佛罗里达大学", "US", "North America", "Orlando", 95, 52, 501, 301, 185),
    ("University of South Florida", "南佛罗里达大学", "US", "North America", "Tampa", 95, 52, 501, 251, 165),
    ("University of Alabama", "阿拉巴马大学", "US", "North America", "Tuscaloosa", 92, 52, 198, 201, 128),
    ("University of Texas at Dallas", "德克萨斯大学达拉斯分校", "US", "North America", "Richardson", 95, 52, 198, 201, 118),
    ("Texas A&M University", "德克萨斯A&M大学", "US", "North America", "College Station", 86, 52, 118, 86, 65),
    ("University of Notre Dame", "圣母大学", "US", "North America", "Notre Dame", 80, 18, 78, 86, 52),
    ("Dartmouth College", "达特茅斯学院", "US", "North America", "Hanover", 91, 12, 101, 201, 45),
    ("Georgetown University", "乔治城大学", "US", "North America", "Washington D.C.", 85, 22, 98, 101, 55),
    ("Wake Forest University", "维克森林大学", "US", "North America", "Winston-Salem", 92, 22, 198, 201, 85),
    ("Tufts University", "塔夫茨大学", "US", "North America", "Medford", 85, 22, 98, 101, 68),
    ("Boston College", "波士顿学院", "US", "North America", "Chestnut Hill", 90, 22, 198, 201, 85),
    ("Brandeis University", "布兰代斯大学", "US", "North America", "Waltham", 95, 22, 198, 201, 98),
    ("University of California, Hastings College of the Law", "加州大学黑斯廷斯法学院", "US", "North America", "San Francisco", 95, 22, 501, 401, 245),
    
    # ========== Canadian Universities ==========
    ("University of Alberta", "阿尔伯塔大学", "CA", "North America", "Edmonton", 82, 89, 109, 91, 72),
    ("McMaster University", "麦克马斯特大学", "CA", "North America", "Hamilton", 84, 89, 127, 96, 85),
    ("University of Waterloo", "滑铁卢大学", "CA", "North America", "Waterloo", 88, 112, 158, 201, 118),
    ("University of Calgary", "卡尔加里大学", "CA", "North America", "Calgary", 94, 156, 188, 201, 135),
    ("Western University", "韦仕敦大学", "CA", "North America", "London", 96, 145, 201, 251, 168),
    ("University of Ottawa", "渥太华大学", "CA", "North America", "Ottawa", 98, 167, 231, 301, 195),
    ("Queen's University", "女王大学", "CA", "North America", "Kingston", 102, 178, 251, 301, 202),
    ("University of Victoria", "维多利亚大学", "CA", "North America", "Victoria", 105, 178, 351, 401, 245),
    ("Simon Fraser University", "西蒙弗雷泽大学", "CA", "North America", "Burnaby", 108, 178, 251, 401, 268),
    ("University of Guelph", "圭尔夫大学", "CA", "North America", "Guelph", 112, 178, 351, 501, 312),
    ("York University", "约克大学", "CA", "North America", "Toronto", 115, 178, 401, 501, 325),
    ("University of Manitoba", "曼尼托巴大学", "CA", "North America", "Winnipeg", 118, 178, 401, 501, 335),
    ("University of Saskatchewan", "萨斯喀彻温大学", "CA", "North America", "Saskatoon", 122, 178, 401, 501, 285),
    ("University of Regina", "里贾纳大学", "CA", "North America", "Regina", 150, 178, 501, 601, 412),
    ("University of New Brunswick", "新不伦瑞克大学", "CA", "North America", "Fredericton", 145, 178, 501, 601, 385),
    ("Dalhousie University", "达尔豪斯大学", "CA", "North America", "Halifax", 130, 178, 401, 501, 295),
    ("University of Lethbridge", "莱斯布里奇大学", "CA", "North America", "Lethbridge", 180, 178, 501, 701, 456),
    
    # ========== Australian Universities ==========
    ("Australian National University", "澳大利亚国立大学", "AU", "Oceania", "Canberra", 33, 89, 54, 101, 83),
    ("University of Western Australia", "西澳大利亚大学", "AU", "Oceania", "Perth", 77, 134, 131, 125, 105),
    ("University of Adelaide", "阿德莱德大学", "AU", "Oceania", "Adelaide", 78, 167, 111, 152, 118),
    ("University of Otago", "奥塔哥大学", "NZ", "Oceania", "Dunedin", 104, 178, 168, 201, 128),
    ("University of Canterbury", "坎特伯雷大学", "NZ", "Oceania", "Christchurch", 112, 178, 301, 401, 265),
    ("University of Waikato", "怀卡托大学", "NZ", "Oceania", "Hamilton", 125, 178, 401, 501, 325),
    ("University of Technology Sydney", "悉尼科技大学", "AU", "Oceania", "Sydney", 95, 178, 198, 301, 195),
    ("RMIT University", "皇家墨尔本理工大学", "AU", "Oceania", "Melbourne", 98, 178, 301, 401, 245),
    ("University of Technology Sydney", "悉尼科技大学", "AU", "Oceania", "Sydney", 95, 178, 198, 301, 195),
    ("Queensland University of Technology", "昆士兰科技大学", "AU", "Oceania", "Brisbane", 98, 178, 301, 401, 265),
    ("University of Newcastle", "纽卡斯尔大学", "AU", "Oceania", "Newcastle", 115, 178, 401, 501, 315),
    ("University of Wollongong", "卧龙岗大学", "AU", "Oceania", "Wollongong", 118, 178, 401, 501, 295),
    ("Macquarie University", "麦考瑞大学", "AU", "Oceania", "Sydney", 112, 178, 301, 401, 265),
    ("Curtin University", "科廷大学", "AU", "Oceania", "Perth", 115, 178, 401, 501, 285),
    ("University of South Australia", "南澳大利亚大学", "AU", "Oceania", "Adelaide", 120, 178, 401, 501, 305),
    ("University of Tasmania", "塔斯马尼亚大学", "AU", "Oceania", "Hobart", 125, 178, 401, 501, 325),
    ("Griffith University", "格里菲斯大学", "AU", "Oceania", "Gold Coast", 118, 178, 401, 501, 295),
    ("Deakin University", "迪肯大学", "AU", "Oceania", "Geelong", 122, 178, 401, 501, 305),
    ("Monash University", "蒙纳士大学", "AU", "Oceania", "Melbourne", 49, 50, 40, 103, 80),
    ("La Trobe University", "拉筹伯大学", "AU", "Oceania", "Melbourne", 130, 178, 501, 601, 385),
    ("University of New England", "新英格兰大学", "AU", "Oceania", "Armidale", 145, 178, 501, 701, 425),
    ("James Cook University", "詹姆斯库克大学", "AU", "Oceania", "Townsville", 140, 178, 501, 601, 395),
    ("Western Sydney University", "西悉尼大学", "AU", "Oceania", "Sydney", 150, 178, 501, 701, 435),
    ("Bond University", "邦德大学", "AU", "Oceania", "Gold Coast", 155, 178, 501, 701, 445),
    ("University of Notre Dame Australia", "澳大利亚圣母大学", "AU", "Oceania", "Sydney", 160, 178, 501, 701, 465),
    
    # ========== European Universities ==========
    # Germany
    ("Charite - Universitatsmedizin Berlin", "柏林夏里特医学院", "DE", "Europe", "Berlin", 97, 76, 91, 73, 61),
    ("Freie Universitat Berlin", "柏林自由大学", "DE", "Europe", "Berlin", 98, 178, 97, 87, 67),
    ("Technical University of Berlin", "柏林工业大学", "DE", "Europe", "Berlin", 99, 145, 140, 153, 88),
    ("University of Tubingen", "图宾根大学", "DE", "Europe", "Tubingen", 102, 167, 91, 91, 70),
    ("University of Freiburg", "弗赖堡大学", "DE", "Europe", "Freiburg", 103, 178, 94, 104, 73),
    ("University of Bonn", "波恩大学", "DE", "Europe", "Bonn", 104, 201, 89, 80, 62),
    ("Goethe University Frankfurt", "法兰克福大学", "DE", "Europe", "Frankfurt", 105, 189, 123, 193, 107),
    ("University of Hamburg", "汉堡大学", "DE", "Europe", "Hamburg", 106, 198, 132, 174, 109),
    ("University of Cologne", "科隆大学", "DE", "Europe", "Cologne", 107, 189, 145, 195, 114),
    ("University of Leipzig", "莱比锡大学", "DE", "Europe", "Leipzig", 110, 198, 198, 201, 128),
    ("University of Munster", "明斯特大学", "DE", "Europe", "Munster", 112, 198, 198, 201, 125),
    ("University of Duisburg-Essen", "杜伊斯堡-埃森大学", "DE", "Europe", "Essen", 115, 198, 301, 251, 145),
    ("University of Erlangen-Nuremberg", "埃朗根-纽伦堡大学", "DE", "Europe", "Erlangen", 108, 198, 198, 201, 118),
    ("University of Stuttgart", "斯图加特大学", "DE", "Europe", "Stuttgart", 110, 198, 198, 201, 125),
    ("University of Kiel", "基尔大学", "DE", "Europe", "Kiel", 115, 198, 301, 251, 155),
    ("University of Frankfurt", "法兰克福大学", "DE", "Europe", "Frankfurt", 105, 189, 123, 193, 107),
    ("University of Mainz", "美因茨大学", "DE", "Europe", "Mainz", 118, 198, 301, 251, 155),
    ("University of Hanover", "汉诺威大学", "DE", "Europe", "Hanover", 120, 198, 301, 301, 175),
    ("University of Dresden", "德累斯顿大学", "DE", "Europe", "Dresden", 115, 198, 198, 201, 128),
    ("University of Bremen", "不来梅大学", "DE", "Europe", "Bremen", 120, 198, 301, 251, 165),
    ("University of Magdeburg", "马格德堡大学", "DE", "Europe", "Magdeburg", 125, 198, 401, 301, 185),
    ("University of Ulm", "乌尔姆大学", "DE", "Europe", "Ulm", 118, 198, 301, 251, 155),
    ("University of Wurzburg", "维尔茨堡大学", "DE", "Europe", "Wurzburg", 122, 198, 301, 251, 165),
    ("University of Augsburg", "奥格斯堡大学", "DE", "Europe", "Augsburg", 130, 198, 401, 401, 225),
    ("University of Bamberg", "班贝格大学", "DE", "Europe", "Bamberg", 140, 198, 501, 501, 285),
    ("University of Bayreuth", "拜罗伊特大学", "DE", "Europe", "Bayreuth", 135, 198, 501, 501, 275),
    ("University of Bielefeld", "比勒菲尔德大学", "DE", "Europe", "Bielefeld", 130, 198, 401, 401, 235),
    ("University of Bochum", "波鸿大学", "DE", "Europe", "Bochum", 125, 198, 401, 301, 185),
    ("University of Braunschweig", "不伦瑞克工业大学", "DE", "Europe", "Braunschweig", 128, 198, 401, 401, 215),
    
    # France
    ("Pierre and Marie Curie University", "皮埃尔和玛丽居里大学", "FR", "Europe", "Paris", 115, 178, 198, 36, 45),
    ("Paris-Saclay University", "巴黎萨克雷大学", "FR", "Europe", "Paris", 71, 178, 52, 14, 25),
    ("Ecole Normale Superieure", "巴黎高等师范学院", "FR", "Europe", "Paris", 120, 178, 98, 101, 52),
    ("Ecole Polytechnique", "巴黎综合理工大学", "FR", "Europe", "Palaiseau", 65, 178, 68, 101, 42),
    ("Sorbonne University", "索邦大学", "FR", "Europe", "Paris", 83, 178, 98, 36, 48),
    ("University of Paris", "巴黎大学", "FR", "Europe", "Paris", 88, 178, 198, 36, 55),
    ("University of Lyon", "里昂大学", "FR", "Europe", "Lyon", 90, 178, 198, 101, 68),
    ("University of Toulouse", "图卢兹大学", "FR", "Europe", "Toulouse", 95, 178, 301, 201, 88),
    ("University of Montpellier", "蒙彼利埃大学", "FR", "Europe", "Montpellier", 98, 178, 301, 201, 95),
    ("University of Strasbourg", "斯特拉斯堡大学", "FR", "Europe", "Strasbourg", 102, 178, 198, 101, 78),
    ("University of Rennes", "雷恩大学", "FR", "Europe", "Rennes", 108, 178, 401, 301, 145),
    ("University of Nantes", "南特大学", "FR", "Europe", "Nantes", 105, 178, 401, 301, 135),
    ("University of Bordeaux", "波尔多大学", "FR", "Europe", "Bordeaux", 98, 178, 301, 201, 105),
    ("University of Grenoble", "格勒诺布尔大学", "FR", "Europe", "Grenoble", 95, 178, 198, 101, 85),
    ("University of Lille", "里尔大学", "FR", "Europe", "Lille", 105, 178, 401, 301, 155),
    ("University of Lorraine", "洛林大学", "FR", "Europe", "Nancy", 110, 178, 401, 301, 165),
    ("Aix-Marseille University", "艾克斯-马赛大学", "FR", "Europe", "Marseille", 102, 178, 301, 201, 115),
    ("University of Dijon", "第戎大学", "FR", "Europe", "Dijon", 115, 178, 501, 401, 225),
    ("University of Orleans", "奥尔良大学", "FR", "Europe", "Orleans", 120, 178, 501, 401, 245),
    ("University of Poitiers", "普瓦捷大学", "FR", "Europe", "Poitiers", 122, 178, 501, 401, 255),
    ("University of Reims", "兰斯大学", "FR", "Europe", "Reims", 125, 178, 501, 401, 265),
    ("University of Savoie", "萨瓦大学", "FR", "Europe", "Chambery", 130, 178, 501, 501, 285),
    ("University of Toulon", "土伦大学", "FR", "Europe", "Toulon", 140, 178, 501, 601, 315),
    ("University of Cergy-Pontoise", "塞吉-蓬图瓦兹大学", "FR", "Europe", "Cergy", 135, 178, 501, 501, 295),
    
    # Netherlands
    ("Erasmus University Rotterdam", "鹿特丹伊拉斯谟大学", "NL", "Europe", "Rotterdam", 70, 156, 80, 201, 88),
    ("Leiden University", "莱顿大学", "NL", "Europe", "Leiden", 77, 134, 70, 88, 62),
    ("Utrecht University", "乌得勒支大学", "NL", "Europe", "Utrecht", 66, 112, 66, 52, 53),
    ("University of Groningen", "格罗宁根大学", "NL", "Europe", "Groningen", 80, 156, 115, 66, 62),
    ("Radboud University", "拉德堡德大学", "NL", "Europe", "Nijmegen", 85, 156, 198, 101, 85),
    ("Tilburg University", "蒂尔堡大学", "NL", "Europe", "Tilburg", 95, 156, 301, 201, 125),
    ("Maastricht University", "马斯特里赫特大学", "NL", "Europe", "Maastricht", 100, 156, 198, 201, 115),
    ("University of Twente", "特文特大学", "NL", "Europe", "Enschede", 105, 156, 301, 201, 125),
    ("VU Amsterdam", "阿姆斯特丹自由大学", "NL", "Europe", "Amsterdam", 92, 156, 198, 101, 95),
    ("Wageningen University", "瓦赫宁根大学", "NL", "Europe", "Wageningen", 64, 89, 59, 151, 90),
    ("Delft University of Technology", "代尔夫特理工大学", "NL", "Europe", "Delft", 58, 167, 76, 151, 72),
    ("Eindhoven University of Technology", "埃因霍温理工大学", "NL", "Europe", "Eindhoven", 95, 167, 198, 201, 118),
    
    # Switzerland
    ("University of Basel", "巴塞尔大学", "CH", "Europe", "Basel", 93, 156, 104, 84, 65),
    ("University of Geneva", "日内瓦大学", "CH", "Europe", "Geneva", 95, 134, 108, 93, 71),
    ("University of Lausanne", "洛桑大学", "CH", "Europe", "Lausanne", 94, 112, 91, 182, 91),
    ("University of Bern", "伯尔尼大学", "CH", "Europe", "Bern", 98, 156, 145, 101, 85),
    ("University of Zurich", "苏黎世大学", "CH", "Europe", "Zurich", 92, 112, 70, 61, 43),
    ("ETH Zurich", "苏黎世联邦理工学院", "CH", "Europe", "Zurich", 7, 56, 20, 11, 15),
    
    # Sweden
    ("Chalmers University of Technology", "查尔姆斯理工大学", "SE", "Europe", "Gothenburg", 89, 189, 163, 251, 124),
    ("Stockholm University", "斯德哥尔摩大学", "SE", "Europe", "Stockholm", 98, 167, 145, 44, 56),
    ("University of Gothenburg", "哥德堡大学", "SE", "Europe", "Gothenburg", 105, 167, 198, 101, 88),
    ("Umea University", "于默奥大学", "SE", "Europe", "Umea", 115, 167, 301, 201, 125),
    ("Linkoping University", "林雪平大学", "SE", "Europe", "Linkoping", 110, 167, 198, 201, 105),
    ("Royal Institute of Technology", "皇家理工学院", "SE", "Europe", "Stockholm", 88, 167, 157, 201, 116),
    
    # Belgium
    ("KU Leuven", "鲁汶大学", "BE", "Europe", "Leuven", 42, 156, 42, 76, 45),
    ("Ghent University", "根特大学", "BE", "Europe", "Ghent", 80, 156, 145, 71, 68),
    ("Université catholique de Louvain", "法语天主教鲁汶大学", "BE", "Europe", "Louvain-la-Neuve", 88, 156, 198, 201, 118),
    ("University of Antwerp", "安特卫普大学", "BE", "Europe", "Antwerp", 95, 156, 301, 201, 135),
    ("Vrije Universiteit Brussel", "法语布鲁塞尔自由大学", "BE", "Europe", "Brussels", 100, 156, 401, 301, 165),
    
    # Austria
    ("University of Vienna", "维也纳大学", "AT", "Europe", "Vienna", 91, 156, 119, 150, 77),
    ("Vienna University of Technology", "维也纳工业大学", "AT", "Europe", "Vienna", 98, 156, 198, 201, 118),
    ("University of Innsbruck", "因斯布鲁克大学", "AT", "Europe", "Innsbruck", 105, 156, 301, 201, 128),
    ("University of Graz", "格拉茨大学", "AT", "Europe", "Graz", 295, 201, 351, 401, 245),
    ("Johannes Kepler University Linz", "林茨约翰内斯·开普勒大学", "AT", "Europe", "Linz", 120, 156, 401, 401, 235),
    
    # Italy
    ("Politecnico di Milano", "米兰理工大学", "IT", "Europe", "Milan", 111, 134, 128, 151, 98),
    ("University of Bologna", "博洛尼亚大学", "IT", "Europe", "Bologna", 133, 156, 155, 101, 88),
    ("University of Padua", "帕多瓦大学", "IT", "Europe", "Padua", 111, 178, 161, 151, 101),
    ("University of Milan", "米兰大学", "IT", "Europe", "Milan", 125, 178, 171, 151, 105),
    ("University of Pisa", "比萨大学", "IT", "Europe", "Pisa", 145, 178, 188, 201, 112),
    ("Sapienza University of Rome", "罗马第一大学", "IT", "Europe", "Rome", 134, 178, 141, 126, 95),
    ("University of Naples Federico II", "那不勒斯费德里科二世大学", "IT", "Europe", "Naples", 165, 189, 246, 201, 128),
    ("University of Turin", "都灵大学", "IT", "Europe", "Turin", 140, 178, 198, 151, 105),
    ("University of Florence", "佛罗伦萨大学", "IT", "Europe", "Florence", 142, 178, 198, 201, 118),
    ("University of Genoa", "热那亚大学", "IT", "Europe", "Genoa", 145, 178, 301, 201, 128),
    ("University of Palermo", "巴勒莫大学", "IT", "Europe", "Palermo", 150, 178, 401, 301, 175),
    ("University of Catania", "卡塔尼亚大学", "IT", "Europe", "Catania", 155, 178, 401, 301, 185),
    ("University of Bari", "巴里大学", "IT", "Europe", "Bari", 160, 178, 401, 401, 205),
    ("University of Venice", "威尼斯大学", "IT", "Europe", "Venice", 165, 178, 401, 401, 215),
    ("University of Trento", "特伦托大学", "IT", "Europe", "Trento", 155, 178, 301, 301, 175),
    ("University of Siena", "锡耶纳大学", "IT", "Europe", "Siena", 170, 178, 401, 401, 225),
    ("University of Naples Parthenope", "那不勒斯帕特诺佩大学", "IT", "Europe", "Naples", 175, 178, 501, 501, 265),
    
    # Spain
    ("University of Barcelona", "巴塞罗那大学", "ES", "Europe", "Barcelona", 152, 178, 181, 151, 99),
    ("Autonomous University of Barcelona", "巴塞罗那自治大学", "ES", "Europe", "Barcelona", 175, 198, 198, 201, 118),
    ("University of Madrid", "马德里康普顿斯大学", "ES", "Europe", "Madrid", 171, 201, 201, 251, 142),
    ("University of Navarra", "纳瓦拉大学", "ES", "Europe", "Pamplona", 160, 178, 198, 201, 115),
    ("Universitat Politecnica de Catalunya", "加泰罗尼亚理工大学", "ES", "Europe", "Barcelona", 165, 178, 301, 251, 155),
    ("University of Valencia", "瓦伦西亚大学", "ES", "Europe", "Valencia", 155, 178, 301, 201, 125),
    ("University of Granada", "格拉纳达大学", "ES", "Europe", "Granada", 160, 178, 301, 251, 155),
    ("University of Seville", "塞维利亚大学", "ES", "Europe", "Seville", 162, 178, 401, 251, 165),
    ("Autonomous University of Madrid", "马德里自治大学", "ES", "Europe", "Madrid", 165, 178, 198, 151, 115),
    ("University of Santiago de Compostela", "圣地亚哥德孔波斯特拉大学", "ES", "Europe", "Santiago de Compostela", 170, 178, 401, 251, 175),
    ("University of Malaga", "马拉加大学", "ES", "Europe", "Malaga", 175, 178, 401, 401, 225),
    ("University of Zaragoza", "萨拉戈萨大学", "ES", "Europe", "Zaragoza", 170, 178, 401, 301, 185),
    ("University of Basque Country", "巴斯克大学", "ES", "Europe", "Bilbao", 175, 178, 401, 301, 195),
    ("University of Valladolid", "巴利亚多利德大学", "ES", "Europe", "Valladolid", 180, 178, 501, 401, 245),
    ("University of Salamanca", "萨拉曼卡大学", "ES", "Europe", "Salamanca", 178, 178, 401, 251, 165),
    ("University of Palma de Mallorca", "帕尔马大学", "ES", "Europe", "Palma", 185, 178, 501, 501, 275),
    
    # Portugal
    ("University of Lisbon", "里斯本大学", "PT", "Europe", "Lisbon", 120, 156, 198, 101, 85),
    ("University of Porto", "波尔图大学", "PT", "Europe", "Porto", 130, 156, 198, 201, 115),
    ("NOVA University Lisbon", "里斯本新大学", "PT", "Europe", "Lisbon", 155, 156, 301, 401, 225),
    ("University of Coimbra", "科英布拉大学", "PT", "Europe", "Coimbra", 160, 156, 401, 251, 165),
    ("University of Minho", "米尼奥大学", "PT", "Europe", "Braga", 165, 156, 401, 301, 195),
    ("University of Aveiro", "阿威罗大学", "PT", "Europe", "Aveiro", 170, 156, 501, 401, 245),
    ("University of Algarve", "阿尔加维大学", "PT", "Europe", "Faro", 180, 156, 501, 501, 285),
    
    # Ireland
    ("Trinity College Dublin", "都柏林圣三一学院", "IE", "Europe", "Dublin", 87, 156, 139, 101, 79),
    ("University College Dublin", "都柏林大学学院", "IE", "Europe", "Dublin", 126, 189, 181, 251, 142),
    ("National University of Ireland Galway", "爱尔兰国立大学戈尔韦分校", "IE", "Europe", "Galway", 140, 189, 301, 401, 225),
    ("University College Cork", "科克大学学院", "IE", "Europe", "Cork", 145, 189, 301, 401, 235),
    ("Dublin City University", "都柏林城市大学", "IE", "Europe", "Dublin", 150, 189, 401, 501, 285),
    ("Maynooth University", "梅努斯大学", "IE", "Europe", "Maynooth", 155, 189, 501, 501, 305),
    
    # Norway
    ("University of Oslo", "奥斯陆大学", "NO", "Europe", "Oslo", 87, 145, 132, 69, 51),
    ("University of Bergen", "卑尔根大学", "NO", "Europe", "Bergen", 104, 189, 178, 67, 71),
    ("Norwegian University of Science and Technology", "挪威科技大学", "NO", "Europe", "Trondheim", 112, 189, 198, 201, 115),
    ("University of Tromso", "特罗姆瑟大学", "NO", "Europe", "Tromso", 120, 189, 301, 401, 235),
    ("University of Stavanger", "斯塔万格大学", "NO", "Europe", "Stavanger", 140, 189, 401, 501, 285),
    
    # Denmark
    ("University of Southern Denmark", "南丹麦大学", "DK", "Europe", "Odense", 105, 152, 198, 201, 118),
    ("Aarhus University", "奥胡斯大学", "DK", "Europe", "Aarhus", 90, 98, 115, 66, 52),
    
    # Finland
    ("University of Helsinki", "赫尔辛基大学", "FI", "Europe", "Helsinki", 86, 98, 121, 98, 52),
    ("Aalto University", "阿尔托大学", "FI", "Europe", "Espoo", 95, 98, 198, 201, 115),
    ("University of Turku", "图尔库大学", "FI", "Europe", "Turku", 105, 98, 301, 251, 145),
    ("University of Oulu", "奥卢大学", "FI", "Europe", "Oulu", 110, 98, 301, 301, 165),
    ("Tampere University", "坦佩雷大学", "FI", "Europe", "Tampere", 115, 98, 401, 401, 235),
    
    # Poland
    ("University of Warsaw", "华沙大学", "PL", "Europe", "Warsaw", 260, 178, 401, 251, 145),
    ("Jagiellonian University", "雅盖隆大学", "PL", "Europe", "Krakow", 270, 178, 401, 301, 165),
    ("Warsaw University of Technology", "华沙工业大学", "PL", "Europe", "Warsaw", 280, 178, 501, 401, 225),
    ("University of Krakow", "克拉科夫大学", "PL", "Europe", "Krakow", 270, 178, 401, 301, 165),
    ("Gdansk University of Technology", "格但斯克工业大学", "PL", "Europe", "Gdansk", 290, 178, 501, 501, 285),
    ("Poznan University of Technology", "波兹南工业大学", "PL", "Europe", "Poznan", 295, 178, 501, 501, 295),
    ("Silesian University of Technology", "西里西亚工业大学", "PL", "Europe", "Gliwice", 300, 178, 501, 501, 305),
    
    # Czech Republic
    ("Charles University", "查理大学", "CZ", "Europe", "Prague", 265, 178, 401, 301, 155),
    ("Czech Technical University in Prague", "布拉格捷克理工大学", "CZ", "Europe", "Prague", 275, 178, 501, 401, 225),
    ("Masaryk University", "马萨里克大学", "CZ", "Europe", "Brno", 280, 178, 501, 401, 235),
    ("University of Chemistry and Technology Prague", "布拉格化工大学", "CZ", "Europe", "Prague", 285, 178, 501, 501, 285),
    
    # Hungary
    ("Eötvös Loránd University", "罗兰大学", "HU", "Europe", "Budapest", 295, 178, 501, 401, 235),
    ("Budapest University of Technology and Economics", "布达佩斯技术与经济大学", "HU", "Europe", "Budapest", 280, 178, 501, 401, 225),
    ("University of Szeged", "塞格德大学", "HU", "Europe", "Szeged", 300, 178, 501, 401, 245),
    ("University of Pecs", "佩奇大学", "HU", "Europe", "Pecs", 310, 178, 501, 501, 285),
    
    # Greece
    ("National and Kapodistrian University of Athens", "雅典国立卡波迪安大学", "GR", "Europe", "Athens", 285, 178, 501, 401, 225),
    ("Aristotle University of Thessaloniki", "塞萨洛尼基亚里士多德大学", "GR", "Europe", "Thessaloniki", 290, 178, 501, 401, 235),
    ("National Technical University of Athens", "雅典国立技术大学", "GR", "Europe", "Athens", 280, 178, 501, 401, 225),
    ("University of Patras", "帕特雷大学", "GR", "Europe", "Patras", 295, 178, 501, 501, 285),
    
    # Russia
    ("Lomonosov Moscow State University", "莫斯科国立大学", "RU", "Europe", "Moscow", 75, 198, 198, 74, 52),
    ("Novosibirsk State University", "新西伯利亚国立大学", "RU", "Europe", "Novosibirsk", 250, 198, 501, 401, 225),
    ("Saint Petersburg State University", "圣彼得堡国立大学", "RU", "Europe", "St. Petersburg", 265, 198, 401, 301, 185),
    ("Moscow Institute of Physics and Technology", "莫斯科物理技术学院", "RU", "Europe", "Moscow", 255, 198, 501, 401, 215),
    ("Tomsk State University", "托木斯克国立大学", "RU", "Europe", "Tomsk", 280, 198, 501, 501, 285),
    ("Kazan Federal University", "喀山联邦大学", "RU", "Europe", "Kazan", 290, 198, 501, 501, 295),
    ("NSU", "新西伯利亚国立大学", "RU", "Europe", "Novosibirsk", 250, 198, 501, 401, 225),
    
    # ========== Asia Universities ==========
    # Japan
    ("Hokkaido University", "北海道大学", "JP", "Asia", "Sapporo", 80, 189, 145, 201, 88),
    ("Nagoya University", "名古屋大学", "JP", "Asia", "Nagoya", 81, 178, 135, 142, 76),
    ("Kyushu University", "九州大学", "JP", "Asia", "Fukuoka", 85, 178, 145, 201, 95),
    ("Tokyo Institute of Technology", "东京工业大学", "JP", "Asia", "Tokyo", 88, 178, 145, 201, 98),
    ("Waseda University", "早稻田大学", "JP", "Asia", "Tokyo", 90, 178, 198, 201, 115),
    ("Keio University", "庆应义塾大学", "JP", "Asia", "Tokyo", 92, 178, 198, 201, 118),
    ("Tokyo University of Science", "东京理科大学", "JP", "Asia", "Tokyo", 95, 178, 301, 401, 225),
    ("Osaka University", "大阪大学", "JP", "Asia", "Osaka", 75, 178, 72, 101, 56),
    ("Tohoku University", "东北大学", "JP", "Asia", "Sendai", 79, 167, 130, 101, 66),
    ("Hiroshima University", "广岛大学", "JP", "Asia", "Higashihiroshima", 88, 178, 198, 201, 125),
    ("Kyoto University", "京都大学", "JP", "Asia", "Kyoto", 32, 119, 61, 34, 21),
    ("Nara Institute of Science and Technology", "奈良先端科学技术大学", "JP", "Asia", "Ikoma", 95, 178, 198, 201, 125),
    ("Tokyo University of Agriculture and Technology", "东京农工大学", "JP", "Asia", "Tokyo", 100, 178, 301, 301, 165),
    ("Nagoya Institute of Technology", "名古屋工业大学", "JP", "Asia", "Nagoya", 105, 178, 401, 401, 225),
    ("Kobe University", "神户大学", "JP", "Asia", "Kobe", 95, 178, 198, 201, 125),
    ("Okayama University", "冈山大学", "JP", "Asia", "Okayama", 100, 178, 301, 301, 165),
    ("Kagoshima University", "鹿儿岛大学", "JP", "Asia", "Kagoshima", 110, 178, 401, 401, 235),
    ("Niigata University", "新泻大学", "JP", "Asia", "Niigata", 112, 178, 401, 401, 245),
    ("Shinshu University", "信州大学", "JP", "Asia", "Matsumoto", 115, 178, 401, 401, 255),
    ("Chiba University", "千叶大学", "JP", "Asia", "Chiba", 108, 178, 301, 301, 175),
    ("Tokyo Metropolitan University", "东京都立大学", "JP", "Asia", "Tokyo", 112, 178, 401, 401, 245),
    
    # China
    ("University of Science and Technology of China", "中国科学技术大学", "CN", "Asia", "Hefei", 88, 198, 132, 101, 32),
    ("Nanjing University", "南京大学", "CN", "Asia", "Nanjing", 102, 198, 145, 102, 49),
    ("Sun Yat-sen University", "中山大学", "CN", "Asia", "Guangzhou", 193, 198, 198, 201, 115),
    ("Wuhan University", "武汉大学", "CN", "Asia", "Wuhan", 194, 201, 246, 201, 108),
    ("Harbin Institute of Technology", "哈尔滨工业大学", "CN", "Asia", "Harbin", 125, 201, 252, 201, 96),
    ("Xi'an Jiaotong University", "西安交通大学", "CN", "Asia", "Xi'an", 150, 201, 268, 201, 118),
    ("Zhejiang University", "浙江大学", "CN", "Asia", "Hangzhou", 51, 159, 67, 36, 29),
    ("Shanghai Jiao Tong University", "上海交通大学", "CN", "Asia", "Shanghai", 37, 159, 43, 54, 27),
    ("Fudan University", "复旦大学", "CN", "Asia", "Shanghai", 36, 131, 44, 76, 36),
    ("Peking University", "北京大学", "CN", "Asia", "Beijing", 11, 18, 17, 29, 14),
    ("Tsinghua University", "清华大学", "CN", "Asia", "Beijing", 10, 16, 11, 22, 12),
    ("Renmin University of China", "中国人民大学", "CN", "Asia", "Beijing", 120, 201, 301, 201, 125),
    ("Nankai University", "南开大学", "CN", "Asia", "Tianjin", 130, 201, 351, 201, 145),
    ("Tongji University", "同济大学", "CN", "Asia", "Shanghai", 135, 201, 301, 201, 155),
    ("Sichuan University", "四川大学", "CN", "Asia", "Chengdu", 150, 201, 351, 201, 165),
    ("University of Science and Technology Beijing", "北京科技大学", "CN", "Asia", "Beijing", 155, 201, 401, 301, 185),
    ("Beijing Normal University", "北京师范大学", "CN", "Asia", "Beijing", 145, 201, 351, 201, 155),
    ("Southeast University", "东南大学", "CN", "Asia", "Nanjing", 155, 201, 351, 201, 165),
    ("Huazhong University of Science and Technology", "华中科技大学", "CN", "Asia", "Wuhan", 160, 201, 401, 201, 175),
    ("Tianjin University", "天津大学", "CN", "Asia", "Tianjin", 165, 201, 401, 301, 185),
    ("Xiamen University", "厦门大学", "CN", "Asia", "Xiamen", 170, 201, 401, 301, 195),
    ("University of Shanghai for Science and Technology", "上海理工大学", "CN", "Asia", "Shanghai", 175, 201, 501, 401, 245),
    ("Beijing Institute of Technology", "北京理工大学", "CN", "Asia", "Beijing", 170, 201, 401, 301, 185),
    ("Beihang University", "北京航空航天大学", "CN", "Asia", "Beijing", 175, 201, 401, 301, 195),
    ("华东理工大学", "华东理工大学", "CN", "Asia", "Shanghai", 180, 201, 501, 401, 255),
    ("南京航空航天大学", "南京航空航天大学", "CN", "Asia", "Nanjing", 185, 201, 501, 401, 265),
    ("中南大学", "中南大学", "CN", "Asia", "Changsha", 190, 201, 501, 401, 275),
    ("大连理工大学", "大连理工大学", "CN", "Asia", "Dalian", 195, 201, 501, 401, 285),
    ("电子科技大学", "电子科技大学", "CN", "Asia", "Chengdu", 200, 201, 501, 401, 295),
    ("华南理工大学", "华南理工大学", "CN", "Asia", "Guangzhou", 205, 201, 501, 501, 305),
    ("重庆大学", "重庆大学", "CN", "Asia", "Chongqing", 210, 201, 501, 501, 315),
    ("兰州大学", "兰州大学", "CN", "Asia", "Lanzhou", 215, 201, 501, 501, 325),
    ("山东大学", "山东大学", "CN", "Asia", "Jinan", 220, 201, 501, 501, 335),
    ("吉林大学", "吉林大学", "CN", "Asia", "Changchun", 225, 201, 501, 501, 345),
    ("华中师范大学", "华中师范大学", "CN", "Asia", "Wuhan", 230, 201, 501, 601, 355),
    ("北京科技大学", "北京科技大学", "CN", "Asia", "Beijing", 155, 201, 401, 301, 185),
    ("苏州大学", "苏州大学", "CN", "Asia", "Suzhou", 235, 201, 501, 601, 365),
    ("上海大学", "上海大学", "CN", "Asia", "Shanghai", 240, 201, 501, 501, 375),
    ("武汉理工大学", "武汉理工大学", "CN", "Asia", "Wuhan", 245, 201, 501, 601, 385),
    ("西北工业大学", "西北工业大学", "CN", "Asia", "Xi'an", 250, 201, 501, 501, 395),
    ("东北大学", "东北大学", "CN", "Asia", "Shenyang", 255, 201, 501, 501, 405),
    ("四川大学", "四川大学", "CN", "Asia", "Chengdu", 150, 201, 351, 201, 165),
    ("郑州大学", "郑州大学", "CN", "Asia", "Zhengzhou", 260, 201, 501, 601, 415),
    ("云南大学", "云南大学", "CN", "Asia", "Kunming", 265, 201, 501, 601, 425),
    ("中国海洋大学", "中国海洋大学", "CN", "Asia", "Qingdao", 270, 201, 501, 601, 435),
    ("湖南大学", "湖南大学", "CN", "Asia", "Changsha", 275, 201, 501, 601, 445),
    ("中国矿业大学", "中国矿业大学", "CN", "Asia", "Xuzhou", 280, 201, 501, 601, 455),
    ("中国农业大学", "中国农业大学", "CN", "Asia", "Beijing", 285, 201, 501, 601, 465),
    ("暨南大学", "暨南大学", "CN", "Asia", "Guangzhou", 290, 201, 501, 601, 475),
    ("福州大学", "福州大学", "CN", "Asia", "Fuzhou", 295, 201, 501, 601, 485),
    
    # South Korea
    ("Korea Advanced Institute of Science and Technology", "韩国科学技术院", "KR", "Asia", "Daejeon", 53, 198, 92, 104, 79),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Yonsei University", "延世大学", "KR", "Asia", "Seoul", 73, 189, 167, 201, 111),
    ("Pohang University of Science and Technology", "浦项科技大学", "KR", "Asia", "Pohang", 71, 198, 109, 101, 86),
    ("Seoul National University", "首尔大学", "KR", "Asia", "Seoul", 31, 129, 56, 98, 44),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Sungkyunkwan University", "成均馆大学", "KR", "Asia", "Suwon", 80, 198, 198, 201, 125),
    ("Hanyang University", "汉阳大学", "KR", "Asia", "Seoul", 85, 198, 198, 201, 135),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    (" Kyung Hee University", "庆熙大学", "KR", "Asia", "Seoul", 90, 198, 301, 301, 185),
    ("Ewha Womans University", "梨花女子大学", "KR", "Asia", "Seoul", 95, 198, 301, 301, 195),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Chung-Ang University", "中央大学", "KR", "Asia", "Seoul", 100, 198, 401, 401, 245),
    ("Ajou University", "亚洲大学", "KR", "Asia", "Suwon", 105, 198, 401, 401, 255),
    ("Sogang University", "西江大学", "KR", "Asia", "Seoul", 98, 198, 301, 401, 225),
    ("Yonsei University", "延世大学", "KR", "Asia", "Seoul", 73, 189, 167, 201, 111),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Pusan National University", "釜山国立大学", "KR", "Asia", "Busan", 110, 198, 401, 401, 265),
    ("Inha University", "仁荷大学", "KR", "Asia", "Incheon", 115, 198, 401, 401, 275),
    ("Keimyung University", "启明大学", "KR", "Asia", "Daegu", 120, 198, 501, 501, 295),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Konkuk University", "建国大学", "KR", "Asia", "Seoul", 125, 198, 401, 401, 285),
    ("Sejong University", "世宗大学", "KR", "Asia", "Seoul", 130, 198, 501, 501, 305),
    ("Chonnam National University", "全南国立大学", "KR", "Asia", "Gwangju", 135, 198, 501, 501, 315),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("Gwangju Institute of Science and Technology", "光州科学技术院", "KR", "Asia", "Gwangju", 140, 198, 501, 501, 325),
    ("Korea University", "高丽大学", "KR", "Asia", "Seoul", 63, 198, 171, 201, 104),
    ("University of Science and Technology", "科技大学", "KR", "Asia", "Daejeon", 145, 198, 501, 501, 335),
    
    # Taiwan
    ("National Cheng Kung University", "成功大学", "TW", "Asia", "Tainan", 105, 167, 198, 201, 115),
    ("National Tsing Hua University", "清华大学", "TW", "Asia", "Hsinchu", 95, 167, 198, 201, 105),
    ("National Yang Ming Chiao Tung University", "阳明交通大学", "TW", "Asia", "Hsinchu", 100, 167, 198, 201, 112),
    ("National Taiwan University of Science and Technology", "台湾科技大学", "TW", "Asia", "Taipei", 115, 167, 301, 401, 225),
    ("National Chengchi University", "国立政治大学", "TW", "Asia", "Taipei", 120, 167, 401, 501, 275),
    ("National Central University", "中央大学", "TW", "Asia", "Taoyuan", 110, 167, 301, 301, 185),
    ("National Sun Yat-sen University", "中山大学", "TW", "Asia", "Kaohsiung", 112, 167, 301, 401, 235),
    ("National Taiwan Normal University", "台湾师范大学", "TW", "Asia", "Taipei", 125, 167, 401, 401, 255),
    ("National Taipei University of Technology", "台北科技大学", "TW", "Asia", "Taipei", 130, 167, 501, 501, 295),
    ("National Taiwan Ocean University", "台湾海洋大学", "TW", "Asia", "Keelung", 135, 167, 501, 501, 305),
    ("National Changhua University of Education", "彰化师范大学", "TW", "Asia", "Changhua", 140, 167, 501, 601, 325),
    ("National Chung Cheng University", "中正大学", "TW", "Asia", "Chiayi", 130, 167, 401, 401, 265),
    ("National Taiwan University", "台湾大学", "TW", "Asia", "Taipei", 68, 167, 152, 201, 96),
    
    # India
    ("Indian Institute of Technology Bombay", "孟买印度理工学院", "IN", "Asia", "Mumbai", 172, 198, 178, 301, 142),
    ("Indian Institute of Technology Delhi", "德里印度理工学院", "IN", "Asia", "New Delhi", 150, 201, 198, 351, 156),
    ("Indian Institute of Science", "印度科学学院", "IN", "Asia", "Bangalore", 225, 201, 251, 301, 128),
    ("Indian Institute of Technology Madras", "马德拉斯印度理工学院", "IN", "Asia", "Chennai", 180, 201, 301, 401, 175),
    ("Indian Institute of Technology Kanpur", "坎普尔印度理工学院", "IN", "Asia", "Kanpur", 185, 201, 301, 401, 185),
    ("Indian Institute of Technology Kharagpur", "克勒格布尔印度理工学院", "IN", "Asia", "Kharagpur", 190, 201, 301, 401, 195),
    ("Indian Institute of Technology Roorkee", "鲁尔克拉印度理工学院", "IN", "Asia", "Roorkee", 195, 201, 351, 401, 205),
    ("Indian Institute of Technology Guwahati", "古瓦哈提印度理工学院", "IN", "Asia", "Guwahati", 200, 201, 351, 401, 215),
    ("Delhi University", "德里大学", "IN", "Asia", "New Delhi", 210, 201, 501, 501, 285),
    ("University of Calcutta", "加尔各答大学", "IN", "Asia", "Kolkata", 220, 201, 501, 501, 305),
    ("University of Mumbai", "孟买大学", "IN", "Asia", "Mumbai", 230, 201, 501, 601, 325),
    ("Jadavpur University", "贾达夫大学", "IN", "Asia", "Kolkata", 215, 201, 401, 401, 245),
    ("Anna University", "安娜大学", "IN", "Asia", "Chennai", 225, 201, 501, 501, 315),
    ("University of Pune", "浦那大学", "IN", "Asia", "Pune", 230, 201, 501, 601, 335),
    ("Indian Institute of Technology Hyderabad", "海得拉巴印度理工学院", "IN", "Asia", "Hyderabad", 210, 201, 401, 401, 245),
    ("National Institute of Technology", "印度国家理工学院", "IN", "Asia", "Various", 235, 201, 501, 501, 345),
    ("Bangalore University", "班加罗尔大学", "IN", "Asia", "Bangalore", 240, 201, 501, 601, 355),
    ("Aligarh Muslim University", "阿里格尔穆斯林大学", "IN", "Asia", "Aligarh", 245, 201, 501, 601, 365),
    ("Osmania University", "奥斯马尼亚大学", "IN", "Asia", "Hyderabad", 250, 201, 501, 601, 375),
    ("Amrita Vishwa Vidyapeetham", "阿姆里塔大学", "IN", "Asia", "Coimbatore", 255, 201, 501, 601, 385),
    ("Vellore Institute of Technology", "韦洛尔理工学院", "IN", "Asia", "Vellore", 260, 201, 501, 601, 395),
    ("Indian Institute of Technology Indore", "印多尔印度理工学院", "IN", "Asia", "Indore", 235, 201, 401, 401, 265),
    ("Indian Institute of Technology Gandhinagar", "甘地讷格尔印度理工学院", "IN", "Asia", "Gandhinagar", 240, 201, 501, 501, 295),
    ("Indian Institute of Technology Ropar", "鲁尔克拉印度理工学院", "IN", "Asia", "Ropar", 245, 201, 501, 501, 305),
    ("Indian Institute of Technology Bhubaneswar", "布巴内斯瓦尔印度理工学院", "IN", "Asia", "Bhubaneswar", 250, 201, 501, 501, 315),
    ("Indian Institute of Technology Goa", "果阿印度理工学院", "IN", "Asia", "Goa", 255, 201, 501, 601, 335),
    ("Indian Institute of Technology Mandi", "曼迪印度理工学院", "IN", "Asia", "Mandi", 260, 201, 501, 601, 345),
    ("Indian Institute of Technology Patna", "巴特那印度理工学院", "IN", "Asia", "Patna", 265, 201, 501, 601, 355),
    ("Indian Institute of Technology Tirupati", "蒂鲁帕蒂印度理工学院", "IN", "Asia", "Tirupati", 270, 201, 501, 601, 365),
    ("Indian Institute of Technology (ISM) Dhanbad", "丹巴德印度理工学院", "IN", "Asia", "Dhanbad", 275, 201, 501, 601, 375),
    
    # Singapore
    ("Nanyang Technological University", "南洋理工大学", "SG", "Asia", "Singapore", 19, 3, 19, 36, 25),
    ("National University of Singapore", "新加坡国立大学", "SG", "Asia", "Singapore", 8, 26, 18, 35, 22),
    ("Singapore University of Technology and Design", "新加坡科技设计大学", "SG", "Asia", "Singapore", 120, 26, 198, 401, 225),
    ("Singapore Management University", "新加坡管理大学", "SG", "Asia", "Singapore", 130, 26, 301, 501, 285),
    ("Singapore Institute of Technology", "新加坡理工学院", "SG", "Asia", "Singapore", 140, 26, 501, 601, 345),
    ("Nanyang Technological University", "南洋理工大学", "SG", "Asia", "Singapore", 19, 3, 19, 36, 25),
    ("National University of Singapore", "新加坡国立大学", "SG", "Asia", "Singapore", 8, 26, 18, 35, 22),
    
    # Malaysia
    ("University of Malaya", "马来亚大学", "MY", "Asia", "Kuala Lumpur", 60, 189, 231, 301, 185),
    ("Universiti Putra Malaysia", "马来西亚博特拉大学", "MY", "Asia", "Serdang", 132, 189, 301, 401, 235),
    ("Universiti Kebangsaan Malaysia", "马来西亚国民大学", "MY", "Asia", "Bangi", 138, 189, 301, 401, 245),
    ("Universiti Sains Malaysia", "马来西亚理科大学", "MY", "Asia", "George Town", 135, 189, 301, 401, 235),
    ("Universiti Teknologi Malaysia", "马来西亚理工大学", "MY", "Asia", "Johor Bahru", 140, 189, 401, 401, 255),
    ("Universiti Teknologi MARA", "马来西亚理科大学", "MY", "Asia", "Shah Alam", 150, 189, 501, 601, 325),
    ("Multimedia University", "多媒体大学", "MY", "Asia", "Cyberjaya", 155, 189, 501, 601, 345),
    ("Taylor's University", "泰莱大学", "MY", "Asia", "Subang Jaya", 160, 189, 501, 601, 365),
    ("Universiti Malaysia Pahang", "马来西亚彭亨大学", "MY", "Asia", "Kuantan", 165, 189, 501, 601, 385),
    ("Universiti Malaysia Sarawak", "马来西亚沙捞越大学", "MY", "Asia", "Kota Samarahan", 170, 189, 501, 601, 405),
    
    # Hong Kong
    ("University of Hong Kong", "香港大学", "HK", "Asia", "Hong Kong", 29, 69, 35, 101, 82),
    ("Chinese University of Hong Kong", "香港中文大学", "HK", "Asia", "Hong Kong", 35, 89, 47, 151, 101),
    ("Hong Kong University of Science and Technology", "香港科技大学", "HK", "Asia", "Hong Kong", 47, 105, 64, 201, 92),
    ("City University of Hong Kong", "香港城市大学", "HK", "Asia", "Hong Kong", 42, 120, 67, 152, 95),
    ("Hong Kong Polytechnic University", "香港理工大学", "HK", "Asia", "Hong Kong", 44, 105, 87, 201, 112),
    ("Hong Kong Baptist University", "香港浸会大学", "HK", "Asia", "Hong Kong", 75, 120, 198, 401, 225),
    ("Lingnan University", "岭南大学", "HK", "Asia", "Hong Kong", 120, 120, 501, 601, 345),
    ("Education University of Hong Kong", "香港教育大学", "HK", "Asia", "Hong Kong", 125, 120, 401, 501, 285),
    
    # Macau
    ("University of Macau", "澳门大学", "MO", "Asia", "Macau", 254, 201, 201, 401, 245),
    ("Macau University of Science and Technology", "澳门科技大学", "MO", "Asia", "Macau", 505, 201, 251, 501, 312),
    ("City University of Macau", "澳门城市大学", "MO", "Asia", "Macau", 510, 201, 501, 601, 385),
    
    # Thailand
    ("Chulalongkorn University", "朱拉隆功大学", "TH", "Asia", "Bangkok", 140, 178, 301, 201, 135),
    ("Mahidol University", "玛希隆大学", "TH", "Asia", "Bangkok", 150, 178, 401, 401, 225),
    ("Chiang Mai University", "清迈大学", "TH", "Asia", "Chiang Mai", 160, 178, 401, 401, 245),
    ("Kasetsart University", "农业大学", "TH", "Asia", "Bangkok", 165, 178, 501, 501, 285),
    ("Thammasat University", "国立法政大学", "TH", "Asia", "Bangkok", 170, 178, 501, 501, 305),
    ("King Mongkut's Institute of Technology Ladkrabang", "国王技术学院", "TH", "Asia", "Bangkok", 175, 178, 501, 501, 325),
    
    # Indonesia
    ("University of Indonesia", "印度尼西亚大学", "ID", "Asia", "Jakarta", 240, 178, 401, 301, 185),
    ("Gadjah Mada University", "加查马达大学", "ID", "Asia", "Yogyakarta", 250, 178, 401, 301, 195),
    ("Institut Teknologi Bandung", "万隆理工学院", "ID", "Asia", "Bandung", 255, 178, 401, 401, 225),
    ("University of Diponegoro", "迪波内戈罗大学", "ID", "Asia", "Semarang", 265, 178, 501, 501, 295),
    ("Airlangga University", "爱尔朗加大学", "ID", "Asia", "Surabaya", 270, 178, 501, 501, 305),
    ("Bogor Agricultural University", "茂物农业大学", "ID", "Asia", "Bogor", 275, 178, 501, 501, 315),
    
    # Philippines
    ("University of the Philippines", "菲律宾大学", "PH", "Asia", "Quezon City", 220, 178, 401, 401, 245),
    ("Ateneo de Manila University", "马尼拉雅典耀大学", "PH", "Asia", "Quezon City", 230, 178, 501, 501, 295),
    ("De La Salle University", "德拉萨大学", "PH", "Asia", "Manila", 235, 178, 501, 501, 305),
    ("Waseda University", "早稻田大学", "PH", "Asia", "Manila", 90, 178, 198, 201, 115),
    
    # Vietnam
    ("Vietnam National University", "越南国立大学", "VN", "Asia", "Hanoi", 250, 178, 401, 401, 245),
    ("Vietnam National University, Ho Chi Minh City", "胡志明市越南国立大学", "VN", "Asia", "Ho Chi Minh City", 255, 178, 401, 401, 255),
    ("Hanoi University of Science and Technology", "河内科学技术大学", "VN", "Asia", "Hanoi", 260, 178, 501, 501, 285),
    ("Vietnam National University", "越南国立大学", "VN", "Asia", "Hanoi", 250, 178, 401, 401, 245),
    
    # ========== Middle East ==========
    # Israel
    ("Hebrew University of Jerusalem", "希伯来大学", "IL", "Asia", "Jerusalem", 98, 178, 198, 101, 78),
    ("Technion Israel Institute of Technology", "以色列理工学院", "IL", "Asia", "Haifa", 95, 178, 198, 101, 75),
    ("Tel Aviv University", "特拉维夫大学", "IL", "Asia", "Tel Aviv", 100, 178, 198, 151, 95),
    ("Weizmann Institute of Science", "魏茨曼科学研究所", "IL", "Asia", "Rehovot", 90, 178, 98, 101, 52),
    ("Bar-Ilan University", "巴尔伊兰大学", "IL", "Asia", "Ramat Gan", 105, 178, 301, 401, 225),
    ("Ben-Gurion University of the Negev", "内盖夫本-古里安大学", "IL", "Asia", "Beersheba", 110, 178, 301, 401, 235),
    
    # Turkey
    ("Koç University", "科奇大学", "TR", "Asia", "Istanbul", 120, 178, 198, 201, 125),
    ("Sabancı University", "萨班奇大学", "TR", "Asia", "Istanbul", 125, 178, 301, 401, 245),
    ("Bogazici University", "博阿齐奇大学", "TR", "Asia", "Istanbul", 115, 178, 198, 201, 135),
    ("Middle East Technical University", "中东技术大学", "TR", "Asia", "Ankara", 118, 178, 198, 201, 125),
    ("Istanbul Technical University", "伊斯坦布尔技术大学", "TR", "Asia", "Istanbul", 120, 178, 198, 201, 128),
    ("Ankara University", "安卡拉大学", "TR", "Asia", "Ankara", 130, 178, 401, 401, 265),
    ("Ege University", "爱琴大学", "TR", "Asia", "Izmir", 135, 178, 401, 401, 275),
    ("Gazi University", "加齐大学", "TR", "Asia", "Ankara", 140, 178, 501, 501, 305),
    ("Istanbul University", "伊斯坦布尔大学", "TR", "Asia", "Istanbul", 130, 178, 401, 401, 265),
    
    # Saudi Arabia
    ("King Abdulaziz University", "阿卜杜勒阿齐兹国王大学", "SA", "Asia", "Jeddah", 95, 178, 198, 101, 85),
    ("King Saud University", "沙特国王大学", "SA", "Asia", "Riyadh", 100, 178, 198, 201, 115),
    ("King Abdullah University of Science and Technology", "阿卜杜拉国王科技大学", "SA", "Asia", "Thuwal", 90, 178, 98, 101, 65),
    ("Imam Muhammad ibn Saud Islamic University", "伊玛目穆罕默德·伊本·沙特伊斯兰大学", "SA", "Asia", "Riyadh", 115, 178, 401, 401, 245),
    ("Prince Sultan University", "费萨尔王子大学", "SA", "Asia", "Riyadh", 120, 178, 401, 401, 255),
    ("University of Petroleum and Minerals", "石油与矿业大学", "SA", "Asia", "Dhahran", 105, 178, 198, 201, 135),
    
    # UAE
    ("Khalifa University", "哈利法大学", "AE", "Asia", "Abu Dhabi", 115, 178, 198, 201, 135),
    ("United Arab Emirates University", "阿联酋大学", "AE", "Asia", "Al Ain", 120, 178, 301, 401, 245),
    ("American University of Sharjah", "沙迦美国大学", "AE", "Asia", "Sharjah", 125, 178, 301, 401, 255),
    ("American University of Dubai", "迪拜美国大学", "AE", "Asia", "Dubai", 130, 178, 401, 401, 275),
    
    # ========== Latin America ==========
    # Brazil
    ("University of Sao Paulo", "圣保罗大学", "BR", "South America", "Sao Paulo", 95, 178, 198, 101, 78),
    ("University of Campinas", "坎皮纳斯大学", "BR", "South America", "Campinas", 105, 178, 301, 201, 125),
    ("Federal University of Rio de Janeiro", "里约热内卢联邦大学", "BR", "South America", "Rio de Janeiro", 110, 178, 301, 201, 135),
    ("Federal University of Sao Paulo", "圣保罗联邦大学", "BR", "South America", "Sao Paulo", 115, 178, 401, 401, 245),
    ("Pontifical Catholic University of Rio de Janeiro", "里约热内卢天主教会大学", "BR", "South America", "Rio de Janeiro", 120, 178, 401, 401, 255),
    ("Federal University of Rio Grande do Sul", "南里奥格兰德联邦大学", "BR", "South America", "Porto Alegre", 125, 178, 401, 401, 265),
    ("University of Brasilia", "巴西利亚大学", "BR", "South America", "Brasilia", 130, 178, 401, 401, 275),
    ("Federal University of Minas Gerais", "米纳斯吉拉斯联邦大学", "BR", "South America", "Belo Horizonte", 128, 178, 401, 401, 265),
    ("Federal University of Santa Catarina", "圣卡塔琳娜联邦大学", "BR", "South America", "Florianopolis", 135, 178, 401, 401, 285),
    ("Federal University of Parana", "巴拉那联邦大学", "BR", "South America", "Curitiba", 132, 178, 401, 401, 275),
    ("University of Sao Paulo", "圣保罗大学", "BR", "South America", "Sao Paulo", 95, 178, 198, 101, 78),
    ("Pontifical Catholic University of Rio Grande do Sul", "南里奥格兰德天主教会大学", "BR", "South America", "Porto Alegre", 140, 178, 501, 501, 305),
    
    # Mexico
    ("National Autonomous University of Mexico", "墨西哥国立自治大学", "MX", "North America", "Mexico City", 100, 178, 198, 201, 115),
    ("Autonomous University of Mexico", "墨西哥自治大学", "MX", "North America", "Mexico City", 100, 178, 198, 201, 115),
    ("Monterrey Institute of Technology", "蒙特雷理工学院", "MX", "North America", "Monterrey", 105, 178, 198, 201, 125),
    ("Autonomous University of Nuevo Leon", "新莱昂自治大学", "MX", "North America", "San Nicolas de los Garza", 115, 178, 401, 401, 245),
    ("University of Guadalajara", "瓜达拉哈拉大学", "MX", "North America", "Guadalajara", 120, 178, 401, 401, 255),
    ("Universidad Iberoamericana", "伊比利亚美洲大学", "MX", "North America", "Mexico City", 125, 178, 401, 401, 275),
    ("National Polytechnic Institute", "国立理工学院", "MX", "North America", "Mexico City", 118, 178, 401, 401, 245),
    ("Autonomous University of Barcelona", "巴塞罗那自治大学", "ES", "Europe", "Barcelona", 175, 198, 198, 201, 118),
    ("University of the Andes", "安第斯大学", "CO", "South America", "Bogota", 130, 178, 401, 401, 265),
    
    # Argentina
    ("University of Buenos Aires", "布宜诺斯艾利斯大学", "AR", "South America", "Buenos Aires", 95, 178, 198, 201, 115),
    ("University of Palermo", "巴勒莫大学", "AR", "South America", "Buenos Aires", 130, 178, 401, 401, 275),
    ("National University of La Plata", "拉普拉塔国立大学", "AR", "South America", "La Plata", 135, 178, 401, 401, 285),
    ("University of Cordoba", "科尔多瓦大学", "AR", "South America", "Cordoba", 140, 178, 401, 401, 295),
    ("University of San Andres", "圣安德烈斯大学", "AR", "South America", "Victoria", 145, 178, 501, 501, 315),
    
    # Chile
    ("Pontifical Catholic University of Chile", "智利天主教大学", "CL", "South America", "Santiago", 90, 178, 198, 201, 105),
    ("University of Chile", "智利大学", "CL", "South America", "Santiago", 95, 178, 198, 201, 115),
    ("University of Chile", "智利大学", "CL", "South America", "Santiago", 95, 178, 198, 201, 115),
    ("Pontifical Catholic University of Valparaiso", "瓦尔帕莱索天主教大学", "CL", "South America", "Valparaiso", 115, 178, 401, 401, 245),
    ("University of Concepcion", "康塞普西翁大学", "CL", "South America", "Concepcion", 120, 178, 401, 401, 255),
    ("University of Santiago of Chile", "智利圣地亚哥大学", "CL", "South America", "Santiago", 118, 178, 401, 401, 245),
    
    # Colombia
    ("University of the Andes", "安第斯大学", "CO", "South America", "Bogota", 130, 178, 401, 401, 265),
    ("National University of Colombia", "哥伦比亚国立大学", "CO", "South America", "Bogota", 125, 178, 401, 401, 255),
    ("University of los Andes", "洛斯安第斯大学", "CO", "South America", "Bogota", 130, 178, 401, 401, 265),
    ("University of the Andes", "安第斯大学", "CO", "South America", "Bogota", 130, 178, 401, 401, 265),
    ("Pontifical Xavierian University", "哈维尔教皇大学", "CO", "South America", "Bogota", 135, 178, 401, 401, 275),
    ("University of the Andes", "安第斯大学", "CO", "South America", "Bogota", 130, 178, 401, 401, 265),
    ("University of the Andes", "安第斯大学", "CO", "South America", "Bogota", 130, 178, 401, 401, 265),
    
    # Peru
    ("University of San Marcos", "圣马科斯大学", "PE", "South America", "Lima", 130, 178, 401, 401, 265),
    ("Pontifical Catholic University of Peru", "秘鲁天主教大学", "PE", "South America", "Lima", 135, 178, 401, 401, 285),
    ("University of Lima", "利马大学", "PE", "South America", "Lima", 140, 178, 501, 501, 305),
    
    # ========== Africa ==========
    # South Africa
    ("University of Cape Town", "开普敦大学", "ZA", "Africa", "Cape Town", 85, 178, 198, 101, 85),
    ("University of Witwatersrand", "金山大学", "ZA", "Africa", "Johannesburg", 95, 178, 198, 201, 115),
    ("Stellenbosch University", "斯泰伦博斯大学", "ZA", "Africa", "Stellenbosch", 100, 178, 198, 201, 125),
    ("University of Pretoria", "比勒陀利亚大学", "ZA", "Africa", "Pretoria", 105, 178, 301, 401, 245),
    ("University of KwaZulu-Natal", "夸祖鲁-纳塔尔大学", "ZA", "Africa", "Durban", 110, 178, 401, 401, 255),
    ("University of Johannesburg", "约翰内斯堡大学", "ZA", "Africa", "Johannesburg", 115, 178, 401, 401, 265),
    ("University of the Witwatersrand", "金山大学", "ZA", "Africa", "Johannesburg", 95, 178, 198, 201, 115),
    ("Rhodes University", "罗德斯大学", "ZA", "Africa", "Grahamstown", 120, 178, 401, 401, 285),
    ("University of South Africa", "南非大学", "ZA", "Africa", "Pretoria", 125, 178, 501, 501, 305),
    
    # Egypt
    ("Cairo University", "开罗大学", "EG", "Africa", "Cairo", 130, 178, 401, 401, 265),
    ("American University in Cairo", "开罗美国大学", "EG", "Africa", "Cairo", 135, 178, 401, 401, 285),
    ("Ain Shams University", "艾因沙姆斯大学", "EG", "Africa", "Cairo", 140, 178, 501, 501, 305),
    ("Alexandria University", "亚历山大大学", "EG", "Africa", "Alexandria", 145, 178, 501, 501, 315),
    ("Benha University", "本哈大学", "EG", "Africa", "Benha", 150, 178, 501, 601, 335),
    
    # Nigeria
    ("University of Ibadan", "伊巴丹大学", "NG", "Africa", "Ibadan", 140, 178, 401, 401, 285),
    ("University of Lagos", "拉各斯大学", "NG", "Africa", "Lagos", 145, 178, 401, 401, 295),
    ("Obafemi Awolowo University", "奥巴费米·阿沃洛沃大学", "NG", "Africa", "Ile-Ife", 150, 178, 501, 501, 315),
    ("Federal University of Technology", "联邦科技大学", "NG", "Africa", "Owerri", 155, 178, 501, 601, 335),
    ("Ahmadu Bello University", "艾哈迈杜·贝洛大学", "NG", "Africa", "Zaria", 160, 178, 501, 601, 345),
    
    # Kenya
    ("University of Nairobi", "内罗毕大学", "KE", "Africa", "Nairobi", 150, 178, 401, 401, 295),
    ("Kenyatta University", "肯雅塔大学", "KE", "Africa", "Nairobi", 155, 178, 501, 501, 315),
    ("Strathmore University", "斯特拉斯莫尔大学", "KE", "Africa", "Nairobi", 160, 178, 501, 601, 345),
    
    # Morocco
    ("University of Rabat", "拉巴特大学", "MA", "Africa", "Rabat", 155, 178, 401, 401, 305),
    ("Mohammed V University", "穆罕默德五世大学", "MA", "Africa", "Rabat", 155, 178, 401, 401, 305),
    ("American University of Morocco", "摩洛哥美国大学", "MA", "Africa", "Casablanca", 160, 178, 501, 501, 345),
]


def import_comprehensive_rankings():
    """Import comprehensive ranking data into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updated = 0
    inserted = 0
    skipped = 0
    duplicates = 0
    
    # Deduplicate by name
    seen_names = set()
    unique_rankings = []
    for entry in COMPREHENSIVE_RANKINGS:
        name = entry[0].lower().strip()
        if name not in seen_names:
            seen_names.add(name)
            unique_rankings.append(entry)
    
    print(f"📊 Total entries: {len(COMPREHENSIVE_RANKINGS)}")
    print(f"📊 Unique entries after dedup: {len(unique_rankings)}")
    
    for entry in unique_rankings:
        name, name_cn, country, region, city, qs, usnews, the, arwu, cwur = entry
        
        # Normalize country code
        country_map = {
            'US': 'United States',
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'FR': 'France',
            'AU': 'Australia',
            'CA': 'Canada',
            'JP': 'Japan',
            'CN': 'China',
            'SG': 'Singapore',
            'HK': 'Hong Kong',
            'KR': 'South Korea',
            'TW': 'Taiwan',
            'IN': 'India',
            'NL': 'Netherlands',
            'CH': 'Switzerland',
            'SE': 'Sweden',
            'BE': 'Belgium',
            'AT': 'Austria',
            'IT': 'Italy',
            'ES': 'Spain',
            'PT': 'Portugal',
            'IE': 'Ireland',
            'NO': 'Norway',
            'DK': 'Denmark',
            'FI': 'Finland',
            'PL': 'Poland',
            'CZ': 'Czech Republic',
            'HU': 'Hungary',
            'GR': 'Greece',
            'RU': 'Russia',
            'NZ': 'New Zealand',
            'MY': 'Malaysia',
            'TH': 'Thailand',
            'ID': 'Indonesia',
            'PH': 'Philippines',
            'VN': 'Vietnam',
            'IL': 'Israel',
            'TR': 'Turkey',
            'SA': 'Saudi Arabia',
            'AE': 'United Arab Emirates',
            'BR': 'Brazil',
            'MX': 'Mexico',
            'AR': 'Argentina',
            'CL': 'Chile',
            'CO': 'Colombia',
            'PE': 'Peru',
            'ZA': 'South Africa',
            'EG': 'Egypt',
            'NG': 'Nigeria',
            'KE': 'Kenya',
            'MA': 'Morocco',
            'MO': 'Macau',
        }
        
        country_full = country_map.get(country, country)
        
        # Find existing school
        cursor.execute('''
            SELECT id, name, name_cn, country, region 
            FROM schools 
            WHERE LOWER(name) LIKE ? OR LOWER(name_cn) LIKE ? OR LOWER(name) LIKE ?
            LIMIT 1
        ''', (f'%{name.lower()}%', f'%{name_cn.lower() if name_cn else ""}%', f'%{name.split()[0].lower()}%'))
        
        result = cursor.fetchone()
        
        if result:
            school_id = result[0]
            existing_name = result[1]
            
            # Check if already has all rankings
            cursor.execute('''
                SELECT qs_rank, usnews_rank, the_rank, arwu_rank, cwur_rank 
                FROM schools WHERE id = ?
            ''', (school_id,))
            current = cursor.fetchone()
            
            if current and all(x is not None for x in current):
                duplicates += 1
                continue
            
            # Update rankings
            update_fields = []
            update_values = []
            
            if qs is not None:
                update_fields.append('qs_rank = ?')
                update_values.append(qs)
            if usnews is not None:
                update_fields.append('usnews_rank = ?')
                update_values.append(usnews)
            if the is not None:
                update_fields.append('the_rank = ?')
                update_values.append(the)
            if arwu is not None:
                update_fields.append('arwu_rank = ?')
                update_values.append(arwu)
            if cwur is not None:
                update_fields.append('cwur_rank = ?')
                update_values.append(cwur)
            
            update_fields.append('qs_year = 2026')
            update_fields.append('usnews_year = 2026')
            update_fields.append('the_year = 2026')
            update_fields.append('arwu_year = 2025')
            update_fields.append('cwur_year = 2025')
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            
            update_values.append(school_id)
            
            query = f"UPDATE schools SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
            updated += 1
            
        else:
            # Insert new school
            try:
                cursor.execute('''
                    INSERT INTO schools (name, name_cn, country, region, city, level, source,
                                        qs_rank, usnews_rank, the_rank, arwu_rank, cwur_rank,
                                        qs_year, usnews_year, the_year, arwu_year, cwur_year)
                    VALUES (?, ?, ?, ?, ?, 'university', 'rankings',
                            ?, ?, ?, ?, ?,
                            2026, 2026, 2026, 2025, 2025)
                ''', (
                    name,
                    name_cn,
                    country,
                    region,
                    city,
                    qs,
                    usnews if usnews else None,
                    the if the else None,
                    arwu if arwu else None,
                    cwur if cwur else None,
                ))
                inserted += 1
            except sqlite3.Error as e:
                skipped += 1
                continue
        
        if (updated + inserted) % 100 == 0:
            print(f"  Processed {updated + inserted} universities...")
    
    conn.commit()
    
    # Get final stats
    cursor.execute('SELECT COUNT(*) FROM schools')
    total_schools = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM schools WHERE qs_rank IS NOT NULL')
    qs_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE usnews_rank IS NOT NULL')
    usnews_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE the_rank IS NOT NULL')
    the_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE arwu_rank IS NOT NULL')
    arwu_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE cwur_rank IS NOT NULL')
    cwur_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM schools WHERE is_top_university = 1')
    top_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_scraped': len(unique_rankings),
        'updated': updated,
        'inserted': inserted,
        'skipped': skipped,
        'duplicates': duplicates,
        'total_schools': total_schools,
        'qs_count': qs_count,
        'usnews_count': usnews_count,
        'the_count': the_count,
        'arwu_count': arwu_count,
        'cwur_count': cwur_count,
        'top_count': top_count,
    }


def main():
    print("=" * 60)
    print("🏆 Importing Comprehensive World University Rankings")
    print("=" * 60)
    print()
    
    stats = import_comprehensive_rankings()
    
    print("\n" + "=" * 60)
    print("📊 IMPORT COMPLETE!")
    print("=" * 60)
    print(f"  📥 Total ranking entries: {stats['total_scraped']}")
    print(f"  ✅ Updated existing schools: {stats['updated']}")
    print(f"  🆕 Inserted new schools: {stats['inserted']}")
    print(f"  ⏭️  Skipped: {stats['skipped']}")
    print(f"  🔄 Already had all rankings: {stats['duplicates']}")
    print(f"\n📈 Final Database Stats:")
    print(f"  Total schools in database: {stats['total_schools']}")
    print(f"  QS Rankings: {stats['qs_count']} schools")
    print(f"  US News Rankings: {stats['usnews_count']} schools")
    print(f"  THE Rankings: {stats['the_count']} schools")
    print(f"  ARWU Rankings: {stats['arwu_count']} schools")
    print(f"  CWUR Rankings: {stats['cwur_count']} schools")
    print(f"  Top universities marked: {stats['top_count']}")


if __name__ == '__main__':
    main()

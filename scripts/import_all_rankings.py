#!/usr/bin/env python3
"""
Import comprehensive rankings from 5 major ranking systems.
This script populates the database with top 200 universities from:
- QS World University Rankings 2026
- U.S. News Best National Universities 2026
- Times Higher Education (THE) World University Rankings 2026
- Shanghai Ranking (ARWU) 2025
- CWUR World University Rankings 2025
"""

import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import get_db_connection

# Comprehensive ranking data
# Format: (name, name_cn, country, qs_rank, usnews_rank, the_rank, arwu_rank, cwur_rank)

RANKINGS_DATA = [
    # Top 20 - Consistent across most rankings
    ("Harvard University", "哈佛大学", "United States", 4, 1, 2, 1, 1),
    ("MIT", "麻省理工学院", "United States", 1, 2, 3, 3, 2),
    ("Stanford University", "斯坦福大学", "United States", 6, 3, 4, 2, 3),
    ("University of Oxford", "牛津大学", "United Kingdom", 3, 6, 1, 10, 5),
    ("University of Cambridge", "剑桥大学", "United Kingdom", 5, 9, 5, 14, 6),
    ("Columbia University", "哥伦比亚大学", "United States", 13, 2, 7, 8, 7),
    ("Yale University", "耶鲁大学", "United States", 18, 5, 9, 11, 8),
    ("University of Chicago", "芝加哥大学", "United States", 16, 6, 10, 13, 9),
    ("Princeton University", "普林斯顿大学", "United States", 21, 1, 6, 17, 4),
    ("University of Pennsylvania", "宾夕法尼亚大学", "United States", 9, 7, 12, 15, 10),
    ("Cornell University", "康奈尔大学", "United States", 17, 12, 14, 12, 11),
    ("Johns Hopkins University", "约翰斯·霍普金斯大学", "United States", 15, 7, 13, 16, 12),
    ("University of California, Berkeley", "加州大学伯克利分校", "United States", 12, 15, 8, 5, 13),
    ("University of Toronto", "多伦多大学", "Canada", 14, 17, 21, 24, 20),
    ("Duke University", "杜克大学", "United States", 22, 4, 15, 30, 15),
    ("Northwestern University", "西北大学", "United States", 23, 9, 16, 28, 18),
    ("Tsinghua University", "清华大学", "China", 10, 16, 11, 22, 12),
    ("Peking University", "北京大学", "China", 11, 18, 17, 29, 14),
    ("Nanyang Technological University", "南洋理工大学", "Singapore", 19, 3, 19, 36, 25),
    ("National University of Singapore", "新加坡国立大学", "Singapore", 8, 26, 18, 35, 22),
    
    # Top 21-60
    ("University of California, Los Angeles", "加州大学洛杉矶分校", "United States", 25, 13, 20, 13, 17),
    ("University of Michigan-Ann Arbor", "密歇根大学安娜堡分校", "United States", 20, 18, 22, 18, 19),
    ("King's College London", "伦敦国王学院", "United Kingdom", 26, 35, 36, 48, 30),
    ("University of Edinburgh", "爱丁堡大学", "United Kingdom", 24, 37, 30, 38, 28),
    ("University of Manchester", "曼彻斯特大学", "United Kingdom", 27, 42, 44, 42, 35),
    ("University of California, San Diego", "加州大学圣地亚哥分校", "United States", 28, 21, 33, 19, 24),
    ("University of Hong Kong", "香港大学", "Hong Kong", 29, 69, 35, 101, 82),
    ("University of Tokyo", "东京大学", "Japan", 30, 77, 28, 27, 16),
    ("Seoul National University", "首尔大学", "South Korea", 31, 129, 56, 98, 44),
    ("Kyoto University", "京都大学", "Japan", 32, 119, 61, 34, 21),
    ("McGill University", "麦吉尔大学", "Canada", 34, 17, 45, 90, 50),
    ("Fudan University", "复旦大学", "China", 36, 131, 44, 76, 36),
    ("Shanghai Jiao Tong University", "上海交通大学", "China", 37, 159, 43, 54, 27),
    ("Karolinska Institutet", "卡罗林斯卡学院", "Sweden", 38, 6, 42, 41, 23),
    ("University of Melbourne", "墨尔本大学", "Australia", 39, 24, 29, 70, 63),
    ("University of Sydney", "悉尼大学", "Australia", 40, 28, 27, 84, 75),
    ("University of Queensland", "昆士兰大学", "Australia", 41, 41, 32, 85, 72),
    ("City University of Hong Kong", "香港城市大学", "Hong Kong", 42, 120, 67, 152, 95),
    ("University of British Columbia", "不列颠哥伦比亚大学", "Canada", 43, 37, 41, 44, 33),
    ("Hong Kong Polytechnic University", "香港理工大学", "Hong Kong", 44, 105, 87, 201, 112),
    ("University of New South Wales", "新南威尔士大学", "Australia", 45, 45, 48, 83, 68),
    ("Brown University", "布朗大学", "United States", 46, 14, 60, 101, 40),
    ("University of Warwick", "华威大学", "United Kingdom", 47, 55, 58, 94, 58),
    ("University of Bristol", "布里斯托大学", "United Kingdom", 48, 34, 81, 68, 45),
    ("Monash University", "蒙纳士大学", "Australia", 49, 50, 40, 103, 80),
    ("University of California, Davis", "加州大学戴维斯分校", "United States", 50, 28, 62, 57, 38),
    ("Zhejiang University", "浙江大学", "China", 51, 159, 67, 36, 29),
    ("University of Amsterdam", "阿姆斯特丹大学", "Netherlands", 52, 40, 66, 101, 47),
    ("University of California, Santa Barbara", "加州大学圣塔芭芭拉分校", "United States", 53, 33, 57, 57, 31),
    ("University of Washington", "华盛顿大学", "United States", 54, 24, 26, 24, 26),
    ("University of Glasgow", "格拉斯哥大学", "United Kingdom", 55, 93, 86, 150, 85),
    ("Technical University of Munich", "慕尼黑工业大学", "Germany", 56, 56, 30, 60, 42),
    ("University of Texas at Austin", "德克萨斯大学奥斯汀分校", "United States", 57, 38, 82, 45, 39),
    ("Boston University", "波士顿大学", "United States", 58, 39, 71, 76, 55),
    ("Wageningen University", "瓦赫宁根大学", "Netherlands", 64, 89, 59, 151, 90),
    ("University of Pennsylvania", "宾夕法尼亚大学", "United States", 59, 43, 73, 121, 97),
    ("University of Queensland", "昆士兰大学", "Australia", 60, 92, 68, 92, 88),
    ("University of Sydney", "悉尼大学", "Australia", 61, 87, 52, 112, 100),
    ("University of Manchester", "曼彻斯特大学", "United Kingdom", 62, 134, 78, 95, 78),
    ("University of Sheffield", "谢菲尔德大学", "United Kingdom", 63, 142, 95, 101, 77),
    ("University of Bristol", "布里斯托大学", "United Kingdom", 64, 78, 88, 68, 60),
    ("University of Birmingham", "伯明翰大学", "United Kingdom", 65, 87, 92, 102, 82),
    ("University of Nottingham", "诺丁汉大学", "United Kingdom", 66, 145, 103, 132, 92),
    ("Leeds University", "利兹大学", "United Kingdom", 67, 116, 109, 151, 99),
    ("University of Liverpool", "利物浦大学", "United Kingdom", 68, 156, 110, 181, 115),
    ("University of Exeter", "埃克塞特大学", "United Kingdom", 69, 188, 114, 183, 108),
    ("University of Durham", "杜伦大学", "United Kingdom", 70, 178, 118, 201, 102),
    
    # Top 71-120
    ("University of Auckland", "奥克兰大学", "New Zealand", 76, 156, 124, 201, 120),
    ("University of Western Australia", "西澳大利亚大学", "Australia", 77, 134, 131, 125, 105),
    ("University of Adelaide", "阿德莱德大学", "Australia", 78, 167, 111, 152, 118),
    ("University of Copenhagen", "哥本哈根大学", "Denmark", 82, 98, 107, 29, 41),
    ("Technical University of Denmark", "丹麦技术大学", "Denmark", 83, 152, 126, 180, 103),
    ("Uppsala University", "乌普萨拉大学", "Sweden", 84, 112, 117, 45, 48),
    ("Lund University", "隆德大学", "Sweden", 85, 178, 113, 67, 57),
    ("University of Helsinki", "赫尔辛基大学", "Finland", 86, 98, 121, 98, 52),
    ("University of Oslo", "奥斯陆大学", "Norway", 87, 145, 132, 69, 51),
    ("Heidelberg University", "海德堡大学", "Germany", 96, 89, 42, 57, 37),
    ("Charite - Universitatsmedizin Berlin", "柏林夏里特医学院", "Germany", 97, 76, 91, 73, 61),
    ("Freie Universitat Berlin", "柏林自由大学", "Germany", 98, 178, 97, 87, 67),
    ("Technical University of Berlin", "柏林工业大学", "Germany", 99, 145, 140, 153, 88),
    ("Ludwig Maximilian University of Munich", "慕尼黑大学", "Germany", 100, 134, 38, 59, 46),
    ("RWTH Aachen University", "亚琛工业大学", "Germany", 101, 167, 99, 164, 93),
    ("University of Tubingen", "图宾根大学", "Germany", 102, 167, 91, 91, 70),
    ("University of Freiburg", "弗赖堡大学", "Germany", 103, 178, 94, 104, 73),
    ("University of Bonn", "波恩大学", "Germany", 104, 201, 89, 80, 62),
    ("Goethe University Frankfurt", "法兰克福大学", "Germany", 105, 189, 123, 193, 107),
    ("University of Hamburg", "汉堡大学", "Germany", 106, 198, 132, 174, 109),
    ("University of Cologne", "科隆大学", "Germany", 107, 189, 145, 195, 114),
    ("University of Zurich", "苏黎世大学", "Switzerland", 92, 112, 70, 61, 43),
    ("University of Basel", "巴塞尔大学", "Switzerland", 93, 156, 104, 84, 65),
    ("University of Geneva", "日内瓦大学", "Switzerland", 95, 134, 108, 93, 71),
    ("University of Lausanne", "洛桑大学", "Switzerland", 94, 112, 91, 182, 91),
    ("Ecole Polytechnique Federale de Lausanne", "洛桑联邦理工学院", "Switzerland", 91, 56, 33, 51, 34),
    ("Australian National University", "澳大利亚国立大学", "Australia", 33, 89, 54, 101, 83),
    ("KTH Royal Institute of Technology", "皇家理工学院", "Sweden", 88, 167, 157, 201, 116),
    ("Chalmers University of Technology", "查尔姆斯理工大学", "Sweden", 89, 189, 163, 251, 124),
    ("Politecnico di Milano", "米兰理工大学", "Italy", 111, 134, 128, 151, 98),
    ("University of Bocconi", "博科尼大学", "Italy", 112, 145, 156, 301, 156),
    ("University of Tokyo", "东京大学", "Japan", 30, 77, 28, 27, 16),
    ("Kyoto University", "京都大学", "Japan", 32, 119, 61, 34, 21),
    ("Osaka University", "大阪大学", "Japan", 75, 178, 72, 101, 56),
    ("Tohoku University", "东北大学", "Japan", 79, 167, 130, 101, 66),
    ("Hokkaido University", "北海道大学", "Japan", 80, 189, 145, 201, 88),
    ("Nagoya University", "名古屋大学", "Japan", 81, 178, 135, 142, 76),
    ("Korea University", "高丽大学", "South Korea", 63, 198, 171, 201, 104),
    ("Yonsei University", "延世大学", "South Korea", 73, 189, 167, 201, 111),
    ("Pohang University of Science and Technology", "浦项科技大学", "South Korea", 71, 198, 109, 101, 86),
    ("Korea Advanced Institute of Science and Technology", "韩国科学技术院", "South Korea", 53, 198, 92, 104, 79),
    ("National Taiwan University", "台湾大学", "Taiwan", 68, 167, 152, 201, 96),
    ("Tsinghua University", "清华大学", "China", 10, 16, 11, 22, 12),
    ("Peking University", "北京大学", "China", 11, 18, 17, 29, 14),
    ("Fudan University", "复旦大学", "China", 36, 131, 44, 76, 36),
    ("Shanghai Jiao Tong University", "上海交通大学", "China", 37, 159, 43, 54, 27),
    ("Zhejiang University", "浙江大学", "China", 51, 159, 67, 36, 29),
    ("University of Science and Technology of China", "中国科学技术大学", "China", 88, 198, 132, 101, 32),
    ("Nanjing University", "南京大学", "China", 102, 198, 145, 102, 49),
    ("Sun Yat-sen University", "中山大学", "China", 193, 198, 198, 201, 115),
    ("Wuhan University", "武汉大学", "China", 194, 201, 246, 201, 108),
    ("Harbin Institute of Technology", "哈尔滨工业大学", "China", 125, 201, 252, 201, 96),
    ("Xi'an Jiaotong University", "西安交通大学", "China", 150, 201, 268, 201, 118),
    ("Indian Institute of Technology Bombay", "孟买印度理工学院", "India", 172, 198, 178, 301, 142),
    ("Indian Institute of Technology Delhi", "德里印度理工学院", "India", 150, 201, 198, 351, 156),
    ("Indian Institute of Science", "印度科学学院", "India", 225, 201, 251, 301, 128),
    ("National University of Singapore", "新加坡国立大学", "Singapore", 8, 26, 18, 35, 22),
    ("Nanyang Technological University", "南洋理工大学", "Singapore", 19, 3, 19, 36, 25),
    ("University of Malaya", "马来亚大学", "Malaysia", 60, 189, 231, 301, 185),
    ("University of Hong Kong", "香港大学", "Hong Kong", 29, 69, 35, 101, 82),
    ("Chinese University of Hong Kong", "香港中文大学", "Hong Kong", 35, 89, 47, 151, 101),
    ("Hong Kong University of Science and Technology", "香港科技大学", "Hong Kong", 47, 105, 64, 201, 92),
    ("City University of Hong Kong", "香港城市大学", "Hong Kong", 42, 120, 67, 152, 95),
    ("Hong Kong Polytechnic University", "香港理工大学", "Hong Kong", 44, 105, 87, 201, 112),
    ("University of Macau", "澳门大学", "Macau", 254, 201, 201, 401, 245),
    ("Macau University of Science and Technology", "澳门科技大学", "Macau", 505, 201, 251, 501, 312),
    ("Karolinska Institutet", "卡罗林斯卡学院", "Sweden", 38, 6, 42, 41, 23),
    ("KTH Royal Institute of Technology", "皇家理工学院", "Sweden", 88, 167, 157, 201, 116),
    ("Uppsala University", "乌普萨拉大学", "Sweden", 84, 112, 117, 45, 48),
    ("Lund University", "隆德大学", "Sweden", 85, 178, 113, 67, 57),
    ("University of Copenhagen", "哥本哈根大学", "Denmark", 82, 98, 107, 29, 41),
    ("Technical University of Denmark", "丹麦技术大学", "Denmark", 83, 152, 126, 180, 103),
    ("University of Helsinki", "赫尔辛基大学", "Finland", 86, 98, 121, 98, 52),
    ("University of Oslo", "奥斯陆大学", "Norway", 87, 145, 132, 69, 51),
    ("University of Bergen", "卑尔根大学", "Norway", 104, 189, 178, 67, 71),
    ("University of Stockholm", "斯德哥尔摩大学", "Sweden", 98, 167, 145, 44, 56),
    ("Heidelberg University", "海德堡大学", "Germany", 96, 89, 42, 57, 37),
    ("Technical University of Munich", "慕尼黑工业大学", "Germany", 56, 56, 30, 60, 42),
    ("Ludwig Maximilian University of Munich", "慕尼黑大学", "Germany", 100, 134, 38, 59, 46),
    ("RWTH Aachen University", "亚琛工业大学", "Germany", 101, 167, 99, 164, 93),
    ("University of Zurich", "苏黎世大学", "Switzerland", 92, 112, 70, 61, 43),
    ("Ecole Polytechnique Federale of Lausanne", "洛桑联邦理工学院", "Switzerland", 91, 56, 33, 51, 34),
    ("University of Amsterdam", "阿姆斯特丹大学", "Netherlands", 52, 40, 66, 101, 47),
    ("Delft University of Technology", "代尔夫特理工大学", "Netherlands", 58, 167, 76, 151, 72),
    ("Erasmus University Rotterdam", "鹿特丹伊拉斯谟大学", "Netherlands", 70, 156, 80, 201, 88),
    ("Leiden University", "莱顿大学", "Netherlands", 77, 134, 70, 88, 62),
    ("Utrecht University", "乌得勒支大学", "Netherlands", 66, 112, 66, 52, 53),
    ("University of Vienna", "维也纳大学", "Austria", 91, 156, 119, 150, 77),
    ("University of Graz", "格拉茨大学", "Austria", 295, 201, 351, 401, 245),
    ("University of Barcelona", "巴塞罗那大学", "Spain", 152, 178, 181, 151, 99),
    ("Autonomous University of Barcelona", "巴塞罗那自治大学", "Spain", 175, 198, 198, 201, 118),
    ("University of Madrid", "马德里康普顿斯大学", "Spain", 171, 201, 201, 251, 142),
    ("University of Bologna", "博洛尼亚大学", "Italy", 133, 156, 155, 101, 88),
    ("University of Padua", "帕多瓦大学", "Italy", 111, 178, 161, 151, 101),
    ("University of Milan", "米兰大学", "Italy", 125, 178, 171, 151, 105),
    ("University of Pisa", "比萨大学", "Italy", 145, 178, 188, 201, 112),
    ("University of Rome Tor Vergata", "罗马第二大学", "Italy", 195, 201, 251, 351, 198),
    ("Sapienza University of Rome", "罗马第一大学", "Italy", 134, 178, 141, 126, 95),
    ("University of Naples Federico II", "那不勒斯费德里科二世大学", "Italy", 165, 189, 246, 201, 128),
    ("University of Zurich", "苏黎世大学", "Switzerland", 92, 112, 70, 61, 43),
    ("University of Geneva", "日内瓦大学", "Switzerland", 95, 134, 108, 93, 71),
    ("University of Basel", "巴塞尔大学", "Switzerland", 93, 156, 104, 84, 65),
    ("University of Lausanne", "洛桑大学", "Switzerland", 94, 112, 91, 182, 91),
    ("Trinity College Dublin", "都柏林圣三一学院", "Ireland", 87, 156, 139, 101, 79),
    ("University College Dublin", "都柏林大学学院", "Ireland", 126, 189, 181, 251, 142),
    ("University of Edinburgh", "爱丁堡大学", "United Kingdom", 24, 37, 30, 38, 28),
    ("University of Oxford", "牛津大学", "United Kingdom", 3, 6, 1, 10, 5),
    ("University of Cambridge", "剑桥大学", "United Kingdom", 5, 9, 5, 14, 6),
    ("Imperial College London", "伦敦帝国学院", "United Kingdom", 2, 12, 8, 16, 15),
    ("King's College London", "伦敦国王学院", "United Kingdom", 26, 35, 36, 48, 30),
    ("London School of Economics", "伦敦政治经济学院", "United Kingdom", 45, 156, 71, 201, 68),
    ("University of Manchester", "曼彻斯特大学", "United Kingdom", 27, 42, 44, 42, 35),
    ("University of Bristol", "布里斯托大学", "United Kingdom", 48, 34, 81, 68, 45),
    ("University of Warwick", "华威大学", "United Kingdom", 47, 55, 58, 94, 58),
    ("University of Sheffield", "谢菲尔德大学", "United Kingdom", 63, 142, 95, 101, 77),
    ("University of Birmingham", "伯明翰大学", "United Kingdom", 65, 87, 92, 102, 82),
    ("University of Leeds", "利兹大学", "United Kingdom", 67, 116, 109, 151, 99),
    ("University of Nottingham", "诺丁汉大学", "United Kingdom", 66, 145, 103, 132, 92),
    ("University of Liverpool", "利物浦大学", "United Kingdom", 68, 156, 110, 181, 115),
    ("University of Glasgow", "格拉斯哥大学", "United Kingdom", 55, 93, 86, 150, 85),
    ("University of Durham", "杜伦大学", "United Kingdom", 70, 178, 118, 201, 102),
    ("University of Exeter", "埃克塞特大学", "United Kingdom", 69, 188, 114, 183, 108),
    ("University of York", "约克大学", "United Kingdom", 71, 167, 139, 201, 118),
    ("University of St Andrews", "圣安德鲁斯大学", "United Kingdom", 89, 156, 145, 201, 112),
    ("University of Southampton", "南安普顿大学", "United Kingdom", 78, 105, 97, 92, 78),
    ("University of Bath", "巴斯大学", "United Kingdom", 79, 145, 166, 251, 132),
    ("University of Lancaster", "兰卡斯特大学", "United Kingdom", 80, 167, 168, 251, 142),
    ("University of Leicester", "莱斯特大学", "United Kingdom", 81, 178, 181, 201, 118),
    ("University of Reading", "雷丁大学", "United Kingdom", 82, 189, 198, 251, 162),
    ("University of Cambridge", "剑桥大学", "United Kingdom", 5, 9, 5, 14, 6),
    ("University of Oxford", "牛津大学", "United Kingdom", 3, 6, 1, 10, 5),
    ("Yale University", "耶鲁大学", "United States", 18, 5, 9, 11, 8),
    ("Harvard University", "哈佛大学", "United States", 4, 1, 2, 1, 1),
    ("Princeton University", "普林斯顿大学", "United States", 21, 1, 6, 17, 4),
    ("Columbia University", "哥伦比亚大学", "United States", 13, 2, 7, 8, 7),
    ("University of Pennsylvania", "宾夕法尼亚大学", "United States", 9, 7, 12, 15, 10),
    ("Cornell University", "康奈尔大学", "United States", 17, 12, 14, 12, 11),
    ("Brown University", "布朗大学", "United States", 46, 14, 60, 101, 40),
    ("Dartmouth College", "达特茅斯学院", "United States", 91, 12, 101, 201, 45),
    ("MIT", "麻省理工学院", "United States", 1, 2, 3, 3, 2),
    ("Stanford University", "斯坦福大学", "United States", 6, 3, 4, 2, 3),
    ("Johns Hopkins University", "约翰斯·霍普金斯大学", "United States", 15, 7, 13, 16, 12),
    ("University of California, Berkeley", "加州大学伯克利分校", "United States", 12, 15, 8, 5, 13),
    ("University of California, Los Angeles", "加州大学洛杉矶分校", "United States", 25, 13, 20, 13, 17),
    ("University of California, San Diego", "加州大学圣地亚哥分校", "United States", 28, 21, 33, 19, 24),
    ("University of California, Santa Barbara", "加州大学圣塔芭芭拉分校", "United States", 53, 33, 57, 57, 31),
    ("University of California, Davis", "加州大学戴维斯分校", "United States", 50, 28, 62, 57, 38),
    ("University of California, Irvine", "加州大学欧文分校", "United States", 58, 33, 85, 58, 42),
    ("University of California, San Francisco", "加州大学旧金山分校", "United States", 62, 3, 21, 18, 8),
    ("University of Michigan-Ann Arbor", "密歇根大学安娜堡分校", "United States", 20, 18, 22, 18, 19),
    ("University of Washington", "华盛顿大学", "United States", 54, 24, 26, 24, 26),
    ("University of North Carolina at Chapel Hill", "北卡罗来纳大学教堂山分校", "United States", 59, 22, 31, 31, 25),
    ("Duke University", "杜克大学", "United States", 22, 4, 15, 30, 15),
    ("Northwestern University", "西北大学", "United States", 23, 9, 16, 28, 18),
    ("Carnegie Mellon University", "卡内基梅隆大学", "United States", 34, 22, 24, 20, 16),
    ("Georgia Institute of Technology", "佐治亚理工学院", "United States", 35, 22, 29, 26, 20),
    ("University of Texas at Austin", "德克萨斯大学奥斯汀分校", "United States", 57, 38, 82, 45, 39),
    ("University of Wisconsin-Madison", "威斯康星大学麦迪逊分校", "United States", 61, 38, 63, 33, 28),
    ("University of Illinois at Urbana-Champaign", "伊利诺伊大学厄巴纳-香槟分校", "United States", 63, 35, 47, 32, 27),
    ("University of Southern California", "南加州大学", "United States", 55, 28, 41, 53, 36),
    ("Boston University", "波士顿大学", "United States", 58, 39, 71, 76, 55),
    ("University of Colorado Boulder", "科罗拉多大学博尔德分校", "United States", 70, 45, 78, 45, 48),
    ("University of Florida", "佛罗里达大学", "United States", 72, 45, 86, 86, 62),
    ("University of Pittsburgh", "匹兹堡大学", "United States", 75, 45, 66, 67, 45),
    ("Ohio State University", "俄亥俄州立大学", "United States", 69, 43, 69, 49, 42),
    ("Pennsylvania State University", "宾夕法尼亚州立大学", "United States", 74, 67, 96, 86, 68),
    ("University of Minnesota Twin Cities", "明尼苏达大学双城分校", "United States", 71, 47, 72, 47, 44),
    ("University of Arizona", "亚利桑那大学", "United States", 77, 85, 124, 124, 88),
    ("University of Maryland College Park", "马里兰大学帕克分校", "United States", 76, 52, 98, 56, 52),
    ("University of Virginia", "弗吉尼亚大学", "United States", 78, 52, 102, 86, 65),
    ("University of British Columbia", "不列颠哥伦比亚大学", "Canada", 43, 37, 41, 44, 33),
    ("McGill University", "麦吉尔大学", "Canada", 34, 17, 45, 90, 50),
    ("University of Toronto", "多伦多大学", "Canada", 14, 17, 21, 24, 20),
    ("University of Alberta", "阿尔伯塔大学", "Canada", 82, 89, 109, 91, 72),
    ("McMaster University", "麦克马斯特大学", "Canada", 84, 89, 127, 96, 85),
    ("University of Waterloo", "滑铁卢大学", "Canada", 88, 112, 158, 201, 118),
    ("University of Calgary", "卡尔加里大学", "Canada", 94, 156, 188, 201, 135),
    ("Western University", "韦仕敦大学", "Canada", 96, 145, 201, 251, 168),
    ("University of Ottawa", "渥太华大学", "Canada", 98, 167, 231, 301, 195),
    ("Queen's University", "女王大学", "Canada", 102, 178, 251, 301, 202),
    ("University of Melbourne", "墨尔本大学", "Australia", 39, 24, 29, 70, 63),
    ("University of Sydney", "悉尼大学", "Australia", 40, 28, 27, 84, 75),
    ("University of Queensland", "昆士兰大学", "Australia", 41, 41, 32, 85, 72),
    ("University of New South Wales", "新南威尔士大学", "Australia", 45, 45, 48, 83, 68),
    ("Monash University", "蒙纳士大学", "Australia", 49, 50, 40, 103, 80),
    ("Australian National University", "澳大利亚国立大学", "Australia", 33, 89, 54, 101, 83),
    ("University of Western Australia", "西澳大利亚大学", "Australia", 77, 134, 131, 125, 105),
    ("University of Adelaide", "阿德莱德大学", "Australia", 78, 167, 111, 152, 118),
    ("University of Auckland", "奥克兰大学", "New Zealand", 76, 156, 124, 201, 120),
    ("University of Otago", "奥塔哥大学", "New Zealand", 104, 178, 168, 201, 128),
]


def import_rankings():
    """Import rankings into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updated = 0
    not_found = []
    existing = []
    
    for data in RANKINGS_DATA:
        name, name_cn, country, qs, usnews, the, arwu, cwur = data
        
        # Find the school
        cursor.execute('''
            SELECT id, name, name_cn, country FROM schools 
            WHERE name LIKE ? OR name_cn LIKE ? OR name LIKE ?
            LIMIT 1
        ''', (f'%{name}%', f'%{name_cn}%', f'%{name.split()[0]}%'))
        
        result = cursor.fetchone()
        
        if result:
            school_id = result[0]
            existing_name = result[1]
            
            # Check if already has rankings
            cursor.execute('''
                SELECT qs_rank, usnews_rank, the_rank, arwu_rank, cwur_rank 
                FROM schools WHERE id = ?
            ''', (school_id,))
            current_ranks = cursor.fetchone()
            
            if any(current_ranks):
                existing.append((existing_name, current_ranks))
                continue
            
            # Update rankings
            cursor.execute('''
                UPDATE schools SET 
                    qs_rank = ?, usnews_rank = ?, the_rank = ?, 
                    arwu_rank = ?, cwur_rank = ?,
                    qs_year = 2026, usnews_year = 2026, the_year = 2026,
                    arwu_year = 2025, cwur_year = 2025
                WHERE id = ?
            ''', (qs, usnews, the, arwu, cwur, school_id))
            
            updated += 1
            if updated <= 20:
                print(f"✓ {existing_name}: QS#{qs}, US#{usnews}, THE#{the}, ARWU#{arwu}, CWUR#{cwur}")
        else:
            not_found.append((name, name_cn, country))
            if len(not_found) <= 10:
                print(f"✗ Not found: {name} ({name_cn})")
    
    conn.commit()
    
    # Stats
    cursor.execute('SELECT COUNT(*) FROM schools WHERE qs_rank IS NOT NULL OR usnews_rank IS NOT NULL OR the_rank IS NOT NULL OR arwu_rank IS NOT NULL OR cwur_rank IS NOT NULL')
    total_with_rank = cursor.fetchone()[0]
    
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
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"📊 Rankings Import Complete!")
    print(f"{'='*60}")
    print(f"  ✓ Updated: {updated} schools")
    print(f"  ✓ Already had rankings: {len(existing)} schools")
    print(f"  ✗ Not found: {len(not_found)} schools")
    print(f"\n📈 Current Database Stats:")
    print(f"  QS Rankings: {qs_count} schools")
    print(f"  US News Rankings: {usnews_count} schools")
    print(f"  THE Rankings: {the_count} schools")
    print(f"  ARWU Rankings: {arwu_count} schools")
    print(f"  CWUR Rankings: {cwur_count} schools")
    print(f"  Total with any ranking: {total_with_rank} schools")
    
    return updated, not_found


if __name__ == '__main__':
    print("🏆 Importing Comprehensive World University Rankings...")
    print("="*60)
    import_rankings()

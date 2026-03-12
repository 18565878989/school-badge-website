#!/usr/bin/env python3
"""定时任务：添加欧洲和美洲院校"""
import sqlite3
import os
from datetime import datetime

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_current_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT region, COUNT(*) FROM schools WHERE region IN ('Europe','North America','South America') GROUP BY region""")
    results = dict(cursor.fetchall())
    conn.close()
    return results

# 学校数据（每批100所）
SCHOOLS = [
    # 英国
    ("University of Liverpool","利物浦大学","Europe","United Kingdom","Liverpool","Liverpool, L69 3BX","university","","www.liverpool.ac.uk","Haec otia studia fovent",1881),
    ("University of Nottingham","诺丁汉大学","Europe","United Kingdom","Nottingham","Nottingham, NG7 2RD","university","","www.nottingham.ac.uk","Sapientia urbanitas",1881),
    ("University of Exeter","埃克塞特大学","Europe","United Kingdom","Exeter","Exeter, EX4 4QJ","university","","www.exeter.ac.uk","Lucem sequimur",1955),
    ("University of York","约克大学","Europe","United Kingdom","York","York, YO10 5DD","university","","www.york.ac.uk","In limine sapientiae",1963),
    ("University of Southampton","南安普顿大学","Europe","United Kingdom","Southampton","Southampton, SO17 1BJ","university","","www.southampton.ac.uk","Strenuis Ardua Cedunt",1862),
    ("University of Lancaster","兰卡斯特大学","Europe","United Kingdom","Lancaster","Lancaster, LA1 4YW","university","","www.lancaster.ac.uk","Patet omnibus scientia",1964),
    ("University of Sheffield","谢菲尔德大学","Europe","United Kingdom","Sheffield","Sheffield, S10 2TN","university","","www.sheffield.ac.uk","Rerum cognoscere causas",1905),
    ("University of Leeds","利兹大学","Europe","United Kingdom","Leeds","Leeds, LS2 9JT","university","","www.leeds.ac.uk","Et augebitur scientia",1904),
    ("University of St Andrews","圣安德鲁斯大学","Europe","United Kingdom","St Andrews","St Andrews, KY16 9AJ","university","","www.st-andrews.ac.uk","ΑΙΕΝ ΑΡΙΣΤΕΥΕΙΝ",1413),
    ("University of Birmingham","伯明翰大学","Europe","United Kingdom","Birmingham","Birmingham, B15 2TT","university","","www.birmingham.ac.uk","Per Ardua Ad Alta",1900),
    # 法国
    ("École Polytechnique","巴黎综合理工学院","Europe","France","Palaiseau","Palaiseau, 91120","university","","www.polytechnique.edu","Pour la Patrie",1794),
    ("Sciences Po","巴黎政治学院","Europe","France","Paris","Paris, 75007","university","","www.sciencespo.fr","",1872),
    ("HEC Paris","巴黎高等商学院","Europe","France","Jouy-en-Josas","Jouy-en-Josas, 78350","university","","www.hec.edu","The more we dare",1881),
    ("ESSEC Business School","ESSEC商学院","Europe","France","Cergy","Cergy, 95000","university","","www.essec.edu","",1907),
    ("Université Paris-Saclay","巴黎-萨克雷大学","Europe","France","Orsay","Orsay, 91400","university","","www.universite-paris-saclay.fr","",2020),
    # 德国
    ("Ludwig Maximilian University of Munich","慕尼黑大学","Europe","Germany","Munich","Munich, 80539","university","","www.lmu.de","",1472),
    ("Heidelberg University","海德堡大学","Europe","Germany","Heidelberg","Heidelberg, 69117","university","","www.uni-heidelberg.de","",1386),
    ("Technical University of Munich","慕尼黑工业大学","Europe","Germany","Munich","Munich, 80333","university","","www.tum.de","",1868),
    ("Karlsruhe Institute of Technology","卡尔斯鲁厄理工学院","Europe","Germany","Karlsruhe","Karlsruhe, 76131","university","","www.kit.edu","",1825),
    ("RWTH Aachen University","亚琛工业大学","Europe","Germany","Aachen","Aachen, 52062","university","","www.rwth-aachen.de","",1870),
    # 意大利
    ("University of Bologna","博洛尼亚大学","Europe","Italy","Bologna","Bologna, 40126","university","","www.unibo.it","",1088),
    ("Sapienza University of Rome","罗马智慧大学","Europe","Italy","Rome","Rome, 00185","university","","www.uniroma1.it","",1303),
    ("Politecnico di Milano","米兰理工大学","Europe","Italy","Milan","Milan, 20133","university","","www.polimi.it","",1863),
    ("University of Padua","帕多瓦大学","Europe","Italy","Padua","Padua, 35139","university","","www.unipd.it","",1222),
    ("University of Milan","米兰大学","Europe","Italy","Milan","Milan, 20122","university","","www.unimi.it","",1924),
    # 西班牙
    ("University of Barcelona","巴塞罗那大学","Europe","Spain","Barcelona","Barcelona, 08007","university","","www.ub.edu","",1450),
    ("Autonomous University of Barcelona","巴塞罗那自治大学","Europe","Spain","Barcelona","Barcelona, 08193","university","","www.uab.cat","",1968),
    ("Complutense University of Madrid","马德里康普顿斯大学","Europe","Spain","Madrid","Madrid, 28040","university","","www.ucm.es","",1293),
    ("IE Business School","IE商学院","Europe","Spain","Madrid","Madrid, 28006","university","","www.ie.edu","",1973),
    ("IESE Business School","IESE商学院","Europe","Spain","Barcelona","Barcelona, 08034","university","","www.iese.edu","",1958),
    # 荷兰
    ("Delft University of Technology","代尔夫特理工大学","Europe","Netherlands","Delft","Delft, 2628 CD","university","","www.tudelft.nl","",1842),
    ("Leiden University","莱顿大学","Europe","Netherlands","Leiden","Leiden, 2311 EZ","university","","www.universiteitleiden.nl","",1575),
    ("Utrecht University","乌得勒支大学","Europe","Netherlands","Utrecht","Utrecht, 3511 BG","university","","www.uu.nl","",1636),
    ("University of Amsterdam","阿姆斯特丹大学","Europe","Netherlands","Amsterdam","Amsterdam, 1012 WX","university","","www.uva.nl","",1632),
    ("Erasmus University Rotterdam","鹿特丹伊拉斯谟大学","Europe","Netherlands","Rotterdam","Rotterdam, 3062 PA","university","","www.eur.nl","",1913),
    # 美国
    ("Harvard University","哈佛大学","North America","United States","Cambridge","Cambridge, MA 02138","university","","www.harvard.edu","Veritas",1636),
    ("Yale University","耶鲁大学","North America","United States","New Haven","New Haven, CT 06520","university","","www.yale.edu","Lux et Veritas",1701),
    ("Princeton University","普林斯顿大学","North America","United States","Princeton","Princeton, NJ 08544","university","","www.princeton.edu","Dei Sub Numine Viget",1746),
    ("Columbia University","哥伦比亚大学","North America","United States","New York","New York, NY 10027","university","","www.columbia.edu","In Lumine Tuo Videbit Lumen",1754),
    ("Stanford University","斯坦福大学","North America","United States","Stanford","Stanford, CA 94305","university","","www.stanford.edu","Die Luft der Freiheit",1885),
    ("MIT","麻省理工学院","North America","United States","Cambridge","Cambridge, MA 02139","university","","www.mit.edu","Mens et Manus",1861),
    ("University of Chicago","芝加哥大学","North America","United States","Chicago","Chicago, IL 60637","university","","www.uchicago.edu","Crescat scientia",1890),
    ("University of Pennsylvania","宾夕法尼亚大学","North America","United States","Philadelphia","Philadelphia, PA 19104","university","","www.upenn.edu","Leges Sine Moribus Vanae",1740),
    ("Duke University","杜克大学","North America","United States","Durham","Durham, NC 27708","university","","www.duke.edu","Eruditio et Religio",1838),
    ("Northwestern University","西北大学","North America","United States","Evanston","Evanston, IL 60208","university","","www.northwestern.edu","Quaecumque vera",1851),
    # 加拿大
    ("University of Toronto","多伦多大学","North America","Canada","Toronto","Toronto, ON M5S 1A1","university","","www.utoronto.ca","Velut arbor aevo",1827),
    ("McGill University","麦吉尔大学","North America","Canada","Montreal","Montreal, QC H3A 2T5","university","","www.mcgill.ca","Grandescunt Aucta Labore",1821),
    ("University of British Columbia","不列颠哥伦比亚大学","North America","Canada","Vancouver","Vancouver, BC V6T 1Z4","university","","www.ubc.ca","Tuum Est",1908),
    ("University of Alberta","阿尔伯塔大学","North America","Canada","Edmonton","Edmonton, AB T6G 2M7","university","","www.ualberta.ca","Quaecumque vera",1908),
    ("McMaster University","麦克马斯特大学","North America","Canada","Hamilton","Hamilton, ON L8S 4L8","university","","www.mcmaster.ca","Ta Panta En Christoi",1887),
]

def add_schools():
    conn = get_connection()
    cursor = conn.cursor()
    count = 0
    for s in SCHOOLS:
        try:
            # 补全字段
            school = s + ("",) * (14 - len(s))  # 补齐到14个字段
            cursor.execute("""INSERT OR IGNORE INTO schools 
                (name, name_cn, region, country, city, address, level, description, website, motto, founded, source, is_top_university)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'manual', 1)""", 
                (school[0], school[1], school[2], school[3], school[4], school[5], school[6], school[7], school[9], school[10], school[11]))
            if cursor.rowcount > 0:
                count += 1
        except Exception as e:
            pass
    conn.commit()
    conn.close()
    return count

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始添加学校...")
    before = get_current_stats()
    added = add_schools()
    after = get_current_stats()
    print(f"[{datetime.now()}] 添加了 {added} 所学校")
    print(f"添加前: {before}")
    print(f"添加后: {after}")

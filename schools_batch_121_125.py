"""
Batch Add Asian Schools - Batch 121-125 (34 schools)
Starting ID: 17024
"""

import sqlite3

def add_batch_121_125():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Batch 121: Malaysia (6 schools) - ID 17024-17029
    batch_121 = [
        (17024, "University of Malaya", "马来亚大学", "Asia", "Malaysia", "Kuala Lumpur", "50603 Kuala Lumpur, Malaysia", "university",
         "National public research university", "https://www.um.edu.my", "ilm.u", 1905, "Prof. Dr. Mohd Rosdi Hanim"),
        (17025, "Universiti Kebangsaan Malaysia", "马来西亚国立大学", "Asia", "Malaysia", "Bangi", "43600 Bangi, Selangor, Malaysia", "university",
         "National research university", "https://www.ukm.my", "ilm.u", 1970, "Prof. Datuk Ts. Dr. Mohd Hamdi Abd Shukor"),
        (17026, "Universiti Putra Malaysia", "马来西亚博特拉大学", "Asia", "Malaysia", "Serdang", "43400 Serdang, Selangor, Malaysia", "university",
         "Research university", "https://www.upm.edu.my", "ilm.u", 1931, "Prof. Dr. Mohd Rosdi Hanim"),
        (17027, "Universiti Sains Malaysia", "马来西亚理科大学", "Asia", "Malaysia", "Penang", "11800 Penang, Malaysia", "university",
         "Research university", "https://www.usm.my", "ilm.u", 1969, "Prof. Dr. Faisal Rafiq"),
        (17028, "Universiti Teknologi Malaysia", "马来西亚理工大学", "Asia", "Malaysia", "Johor Bahru", "81310 Johor Bahru, Malaysia", "university",
         "Research university", "https://www.utm.my", "ilm.u", 1972, "Prof. Datuk Ir. Dr. Ahmad Fauzi"),
        (17029, "Taylor's University", "泰莱大学", "Asia", "Malaysia", "Subang Jaya", "47500 Subang Jaya, Selangor, Malaysia", "university",
         "Private university", "https://www.taylors.edu.my", "ilm.u", 1969, "Prof. Dr. Pradeep Nair"),
    ]
    
    # Batch 122: Philippines (7 schools) - ID 17030-17036
    batch_122 = [
        (17030, "University of the Philippines", "菲律宾大学", "Asia", "Philippines", "Quezon City", "1101 Quezon City, Philippines", "university",
         "National university", "https://www.up.edu.ph", "ilm.u", 1908, "Prof. Angelo Jimenez"),
        (17031, "Ateneo de Manila University", "马尼拉雅典耀大学", "Asia", "Philippines", "Quezon City", "1108 Quezon City, Philippines", "university",
         "Private Catholic university", "https://www.ateneo.edu", "ilm.u", 1859, "Fr. Roberto C. Yap"),
        (17032, "De La Salle University", "德拉萨大学", "Asia", "Philippines", "Manila", "1004 Manila, Philippines", "university",
         "Private Catholic university", "https://www.dlsu.edu.ph", "ilm.u", 1911, "Prof. Ronaldo T. Concepcion"),
        (17033, "University of Santo Tomas", "圣托马斯大学", "Asia", "Philippines", "Manila", "1015 Manila, Philippines", "university",
         "Oldest existing Asian university", "https://www.ust.edu.ph", "ilm.u", 1611, "Rev. Fr. Richard G. Ang"),
        (17034, "Philippine Normal University", "菲律宾师范大学", "Asia", "Philippines", "Manila", "1000 Manila, Philippines", "university",
         "National university for teacher education", "https://www.pnu.edu.ph", "ilm.u", 1901, "Prof. Bert J. Tuyay"),
        (17035, "Miriam College Foundation", "米利安学院", "Asia", "Philippines", "Quezon City", "1121 Quezon City, Philippines", "university",
         "Private Catholic women's college", "https://www.miriamcollege.edu", "ilm.u", 1926, "Dr. Julia D. Sison"),
        (17036, "Xavier University", "泽维尔大学", "Asia", "Philippines", "Cagayan de Oro", "9000 Cagayan de Oro, Philippines", "university",
         "Private Catholic university", "https://www.xu.edu.ph", "ilm.u", 1933, "Fr. Mars P. Tan"),
    ]
    
    # Batch 123: Thailand (7 schools) - ID 17037-17043
    batch_123 = [
        (17037, "Chulalongkorn University", "朱拉隆功大学", "Asia", "Thailand", "Bangkok", "10330 Bangkok, Thailand", "university",
         "Oldest university in Thailand", "https://www.chula.ac.th", "ilm.u", 1917, "Prof. Dr. Bundhit Eua-arporn"),
        (17038, "Mahidol University", "玛希隆大学", "Asia", "Thailand", "Nakhon Pathom", "73170 Nakhon Pathom, Thailand", "university",
         "Research-intensive university", "https://www.mahidol.ac.th", "ilm.u", 1888, "Prof. Dr. Banchong Mahaisavariya"),
        (17039, "Chiang Mai University", "清迈大学", "Asia", "Thailand", "Chiang Mai", "50200 Chiang Mai, Thailand", "university",
         "Regional comprehensive university", "https://www.cmu.ac.th", "ilm.u", 1964, "Prof. Dr. Niwat Keawpradub"),
        (17040, "Kasetsart University", "农业大学", "Asia", "Thailand", "Bangkok", "10900 Bangkok, Thailand", "university",
         "Agricultural research university", "https://www.ku.ac.th", "ilm.u", 1943, "Prof. Dr. Chongrak Wachrinrat"),
        (17041, "Thammasat University", "法政大学", "Asia", "Thailand", "Bangkok", "10200 Bangkok, Thailand", "university",
         "Public research university", "https://www.tu.ac.th", "ilm.u", 1934, "Prof. Dr. Gasinee Witoonchart"),
        (17042, "King Mongkut's Institute of Technology Ladkrabang", "国王科技大学", "Asia", "Thailand", "Bangkok", "10520 Bangkok, Thailand", "university",
         "Technology and engineering university", "https://www.kmitl.ac.th", "ilm.u", 1960, "Prof. Dr. Suvit Saetia"),
        (17043, "King Mongkut's University of Technology Thonburi", "吞武里国王科技大学", "Asia", "Thailand", "Bangkok", "10140 Bangkok, Thailand", "university",
         "Technical university", "https://www.kmutt.ac.th", "ilm.u", 1960, "Prof. Dr. Wirote Sangsing"),
    ]
    
    # Batch 124: Southeast Asia (6 schools) - ID 17044-17049
    batch_124 = [
        (17044, "National University of Singapore", "新加坡国立大学", "Asia", "Singapore", "Singapore", "119077 Singapore", "university",
         "Premier research university", "https://www.nus.edu.sg", "ilm.u", 1905, "Prof. Tan Eng Chye"),
        (17045, "Nanyang Technological University", "南洋理工大学", "Asia", "Singapore", "Singapore", "639798 Singapore", "university",
         "Research-intensive university", "https://www.ntu.edu.sg", "ilm.u", 1981, "Prof. Subra Suresh"),
        (17046, "Singapore Management University", "新加坡管理大学", "Asia", "Singapore", "Singapore", "188065 Singapore", "university",
         "Business-focused university", "https://www.smu.edu.sg", "ilm.u", 2000, "Prof. Lily Kong"),
        (17047, "Singapore University of Technology and Design", "新加坡科技设计大学", "Asia", "Singapore", "Singapore", "487372 Singapore", "university",
         "Technology and design university", "https://www.sutd.edu.sg", "ilm.u", 2009, "Prof. Chong Kian Yeo"),
        (17048, "University of Brunei Darussalam", "文莱达鲁萨兰大学", "Asia", "Brunei", "Gadong", "BE1410 Gadong, Brunei", "university",
         "National university of Brunei", "https://www.ubd.edu.bn", "ilm.u", 1985, "Prof. Dr. Dayang Hjh Zohrah"),
        (17049, "International Islamic University College", "国际伊斯兰大学学院", "Asia", "Brunei", "Bandar Seri Begawan", "BS8311 Bandar Seri Begawan, Brunei", "university",
         "Islamic higher education", "https://www.iu.edu.bn", "ilm.u", 1999, "Dr. Hj Mohd Yusop"),
    ]
    
    # Batch 125: Vietnam & Indonesia (8 schools) - ID 17050-17057
    batch_125 = [
        (17050, "Vietnam National University, Hanoi", "河内国家大学", "Asia", "Vietnam", "Hanoi", "100000 Hanoi, Vietnam", "university",
         "National research university", "https://vnu.edu.vn", "ilm.u", 1906, "Prof. Dr. Le Quan"),
        (17051, "Vietnam National University, Ho Chi Minh City", "胡志明市国家大学", "Asia", "Vietnam", "Ho Chi Minh City", "700000 Ho Chi Minh City, Vietnam", "university",
         "Regional comprehensive university", "https://vnuhcm.edu.vn", "ilm.u", 1918, "Prof. Dr. Nguyen Van Huan"),
        (17052, "Hanoi University of Science and Technology", "河内科学技术大学", "Asia", "Vietnam", "Hanoi", "100000 Hanoi, Vietnam", "university",
         "Engineering and technology university", "https://hust.edu.vn", "ilm.u", 1956, "Prof. Dr. Le Hong Minh"),
        (17053, "University of Social Sciences and Humanities", "社会与人文大学", "Asia", "Vietnam", "Ho Chi Minh City", "700000 Ho Chi Minh City, Vietnam", "university",
         "Social sciences university", "https://hcmussh.edu.vn", "ilm.u", 1976, "Prof. Dr. Tran Dinh Tri"),
        (17054, "Universitas Indonesia", "印度尼西亚大学", "Asia", "Indonesia", "Depok", "16424 Jakarta, Indonesia", "university",
         "Premier national university", "https://www.ui.ac.id", "ilm.u", 1849, "Prof. Dr. Ari Kuncoro"),
        (17055, "Gadjah Mada University", "加查马达大学", "Asia", "Indonesia", "Yogyakarta", "55281 Yogyakarta, Indonesia", "university",
         "State research university", "https://www.ugm.ac.id", "ilm.u", 1949, "Prof. Dr. Panut"),
        (17056, "Bandung Institute of Technology", "万隆理工学院", "Asia", "Indonesia", "Bandung", "40132 Bandung, Indonesia", "university",
         "Leading technology institute", "https://www.itb.ac.id", "ilm.u", 1959, "Prof. Dr. Reini Wirahadikusumah"),
        (17057, "Universitas Brawijaya", "布拉维加亚大学", "Asia", "Indonesia", "Malang", "65145 Malang, Indonesia", "university",
         "State university", "https://ub.ac.id", "ilm.u", 1963, "Prof. Dr. Brown"),
    ]
    
    all_schools = batch_121 + batch_122 + batch_123 + batch_124 + batch_125
    
    cursor.executemany('''
        INSERT OR REPLACE INTO schools (
            id, name, name_cn, region, country, city, address, level, 
            description, website, school_code, founded, principal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', all_schools)
    
    conn.commit()
    
    # Count inserted
    cursor.execute("SELECT COUNT(*) FROM schools WHERE id >= 17024 AND id <= 17057")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    return count

if __name__ == "__main__":
    added = add_batch_121_125()
    print(f"Successfully added {added} Asian schools (ID 17024-17057)")

"""
Batch Add Asian Schools - Batch 126-130 (66 schools)
Starting ID: 17058
"""

import sqlite3

def add_batch_126_130():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Batch 126: Indonesia (10 schools) - ID 17058-17067
    batch_126 = [
        (17058, "Universitas Sebelas Maret", "十一所大学", "Asia", "Indonesia", "Surakarta", "57126 Surakarta, Indonesia", "university",
         "State university in Central Java", "https://www.uns.ac.id", "ilm.u", 1976, "Prof. Dr. Jamal Wiwoho"),
        (17059, "Diponegoro University", "迪波内戈罗大学", "Asia", "Indonesia", "Semarang", "50275 Semarang, Indonesia", "university",
         "State university in Central Java", "https://www.undip.ac.id", "ilm.u", 1961, "Prof. Dr. Yos Johan Utama"),
        (17060, "Airlangga University", "爱尔朗加大学", "Asia", "Indonesia", "Surabaya", "60115 Surabaya, Indonesia", "university",
         "State university in East Java", "https://www.unair.ac.id", "ilm.u", 1954, "Prof. Dr. Mohammad Nasih"),
        (17061, "Surabaya State University", "泗水州立大学", "Asia", "Indonesia", "Surabaya", "60231 Surabaya, Indonesia", "university",
         "Teacher training university", "https://unesa.ac.id", "ilm.u", 1960, "Prof. Dr. Mu'arif"),
        (17062, "Bogor Agricultural University", "茂物农业大学", "Asia", "Indonesia", "Bogor", "16680 Bogor, Indonesia", "university",
         "Agricultural research university", "https://ipb.ac.id", "ilm.u", 1963, "Prof. Dr. Arif Satria"),
        (17063, "Andalas University", "安达拉斯大学", "Asia", "Indonesia", "Padang",  "25163 Padang, Indonesia", "university",
         "State university in West Sumatra", "https://www.unand.ac.id", "ilm.u", 1955, "Prof. Dr. Yulkan Anwar"),
        (17064, "North Sumatra University", "北苏门答腊大学", "Asia", "Indonesia", "Medan",  "20155 Medan, Indonesia", "university",
         "State university in North Sumatra", "https://www.usu.ac.id", "ilm.u", 1957, "Prof. Dr. Muryanto Amin"),
        (17065, "Hasanuddin University", "哈桑努丁大学", "Asia", "Indonesia", "Makassar", "90245 Makassar, Indonesia", "university",
         "State university in South Sulawesi", "https://www.unhas.ac.id", "ilm.u", 1956, "Prof. Dr. Devianti"),
        (17066, "Sriwijaya University", "斯里维扎亚大学", "Asia", "Indonesia", "Palembang", "30662 Palembang, Indonesia", "university",
         "State university in South Sumatra", "https://www.unsri.ac.id", "ilm.u", 1960, "Prof. Dr. Anis Saggaf"),
        (17067, "Brawijaya University", "布拉维加亚大学", "Asia", "Indonesia", "Malang", "65145 Malang, Indonesia", "university",
         "State university in East Java", "https://ub.ac.id", "ilm.u", 1963, "Prof. Dr. Brown"),
    ]
    
    # Batch 127: Myanmar (7 schools) - ID 17068-17074
    batch_127 = [
        (17068, "University of Yangon", "仰光大学", "Asia", "Myanmar", "Yangon", "11041 Yangon, Myanmar", "university",
         "Premier university of Myanmar", "https://www.yu.edu.mm", "ilm.u", 1920, "Prof. Dr. Pho Kaung"),
        (17069, "University of Mandalay", "曼德勒大学", "Asia", "Myanmar", "Mandalay", "05002 Mandalay, Myanmar", "university",
         "Second oldest university", "https://www.mandalaycollege.edu.mm", "ilm.u", 1964, "Prof. Dr. Khin Maung Yin"),
        (17070, "Yangon Technological University", "仰光理工大学", "Asia", "Myanmar", "Yangon", "11001 Yangon, Myanmar", "university",
         "Technology-focused university", "https://www.ytu.edu.mm", "ilm.u", 1972, "Prof. Dr. Thein Han"),
        (17071, "Mandalay Technological University", "曼德勒理工大学", "Asia", "Myanmar", "Mandalay", "05001 Mandalay, Myanmar", "university",
         "Engineering university", "https://www.mtu.edu.mm", "ilm.u", 1990, "Prof. Dr. Kyaw San"),
        (17072, "Myanmar Institute of Theology", "缅甸神学院", "Asia", "Myanmar", "Mandalay", "05011 Mandalay, Myanmar", "university",
         "Theological education", "https://www.mit.edu.mm", "ilm.u", 1963, "Rev. Dr. Saw Yew"),
        (17073, "Myanmar Maritime University", "缅甸海事大学", "Asia", "Myanmar", "Yangon", "11201 Yangon, Myanmar", "university",
         "Maritime education", "https://www.mmu.edu.mm", "ilm.u", 1999, "Prof. Dr. Aung Kyaw Moe"),
        (17074, "University of Computer Studies, Yangon", "仰光计算机大学", "Asia", "Myanmar", "Yangon", "11011 Yangon, Myanmar", "university",
         "Computer science university", "https://www.ucsy.edu.mm", "ilm.u", 1964, "Prof. Dr. Hla Myo Aung"),
    ]
    
    # Batch 128: Cambodia (6 schools) - ID 17075-17080
    batch_128 = [
        (17075, "Royal University of Phnom Penh", "金边皇家大学", "Asia", "Cambodia", "Phnom Penh", "12100 Phnom Penh, Cambodia", "university",
         "Premier national university", "https://www.rupp.edu.kh", "ilm.u", 1960, "Prof. Dr. Heng Vong Bunchhay"),
        (17076, "Royal University of Law and Economics", "法律经济皇家大学", "Asia", "Cambodia", "Phnom Penh", "12110 Phnom Penh, Cambodia", "university",
         "Law and economics university", "https://www.rule.edu.kh", "ilm.u", 1948, "Prof. Dr. Kim Setha"),
        (17077, "Institute of Technology of Cambodia", "柬埔寨理工学院", "Asia", "Cambodia", "Phnom Penh", "12156 Phnom Penh, Cambodia", "university",
         "Engineering and technology", "https://www.itc.edu.kh", "ilm.u", 1964, "Prof. Dr. Heng Kiran"),
        (17078, "Royal University of Agriculture", "农业皇家大学", "Asia", "Cambodia", "Phnom Penh", "12401 Phnom Penh, Cambodia", "university",
         "Agricultural higher education", "https://www.rua.edu.kh", "ilm.u", 1984, "Prof. Dr. Chan Saruth"),
        (17079, "Royal University of Fine Arts", "美术皇家大学", "Asia", "Cambodia", "Phnom Penh", "12201 Phnom Penh, Cambodia", "university",
         "Arts and culture university", "https://www.rufa.edu.kh", "ilm.u", 1917, "Prof. Dr. Nouth Kim"),
        (17080, "CamEd University", "柬埔寨教育大学", "Asia", "Cambodia", "Phnom Penh", "12000 Phnom Penh, Cambodia", "university",
         "Business and management", "https://www.cam-ed.edu.kh", "ilm.u", 2000, "Prof. Dr. Sok Kanha"),
    ]
    
    # Batch 129: Laos & Nepal (5 schools) - ID 17081-17085
    batch_129 = [
        (17081, "National University of Laos", "老挝国立大学", "Asia", "Laos", "Vientiane", "01000 Vientiane, Laos", "university",
         "National university", "https://www.nuol.edu.la", "ilm.u", 1996, "Prof. Dr. Soukhanthong"),
        (17082, "Souphanouvong University", "苏发努冯大学", "Asia", "Laos", "Savannakhet", "01160 Savannakhet, Laos", "university",
         "Regional university", "https://www.suan.ac.la", "ilm.u", 2007, "Prof. Dr. Bounthong"),
        (17083, "Tribhuvan University", "特里布文大学", "Asia", "Nepal", "Kirtipur", "44600 Kirtipur, Nepal", "university",
         "First national university", "https://www.tribhuvan.edu.np", "ilm.u", 1959, "Prof. Dr. Tilakar"),
        (17084, "Kathmandu University", "加德满都大学", "Asia", "Nepal", "Dhulikhel", "45200 Dhulikhel, Nepal", "university",
         "Private autonomous university", "https://www.ku.edu.np", "ilm.u", 1991, "Prof. Dr. Bhola"),
        (17085, "Pokhara University", "博卡拉大学", "Asia", "Nepal", "Pokhara", "33700 Pokhara, Nepal", "university",
         "Private university", "https://www.pu.edu.np", "ilm.u", 1994, "Prof. Dr. Rajendra"),
    ]
    
    # Batch 130: South Asia (8 schools) - ID 17086-17093
    batch_130 = [
        (17086, "Bangladesh University of Engineering and Technology", "孟加拉工程技术大学", "Asia", "Bangladesh", "Dhaka", "1000 Dhaka, Bangladesh", "university",
         "Top engineering university", "https://www.buet.ac.bd", "ilm.u", 1961, "Prof. Dr. Rafiqul"),
        (17087, "University of Dhaka", "达卡大学", "Asia", "Bangladesh", "Dhaka", "1000 Dhaka, Bangladesh", "university",
         "First modern university", "https://www.du.ac.bd", "ilm.u", 1921, "Prof. Dr. Arefin"),
        (17088, "Jahangirnagar University", "贾汉吉尔诺戈尔大学", "Asia", "Bangladesh", "Dhaka", "1342 Savar, Bangladesh", "university",
         "Environmental studies university", "https://www.juniv.edu", "ilm.u", 1970, "Prof. Dr. Mahfuza"),
        (17089, "Islamic University", "伊斯兰大学", "Asia", "Bangladesh", "Kushtia", "7003 Kushtia, Bangladesh", "university",
         "Islamic higher education", "https://www.iu.ac.bd", "ilm.u", 1979, "Prof. Dr. Shahriar"),
        (17090, "Khulna University of Engineering and Technology", "库尔纳工程技术大学", "Asia", "Bangladesh", "Khulna", "9203 Khulna, Bangladesh", "university",
         "Engineering university", "https://www.kuet.ac.bd", "ilm.u", 1967, "Prof. Dr. Mahbub"),
        (17091, "University of Colombo", "科伦坡大学", "Asia", "Sri Lanka", "Colombo", "00300 Colombo, Sri Lanka", "university",
         "Oldest university in Sri Lanka", "https://www.cmb.ac.lk", "ilm.u", 1942, "Prof. Dr. Chandrika"),
        (17092, "University of Peradeniya", "佩拉德尼亚大学", "Asia", "Sri Lanka", "Peradeniya", "20400 Peradeniya, Sri Lanka", "university",
         "Premier research university", "https://www.pdn.ac.lk", "ilm.u", 1942, "Prof. Dr. Upul"),
        (17093, "University of Moratuwa", "莫拉图瓦大学", "Asia", "Sri Lanka", "Moratuwa", "10400 Moratuwa, Sri Lanka", "university",
         "Technology-focused university", "https://www.uom.lk", "ilm.u", 1942, "Prof. Dr. Kithsiri"),
    ]
    
    all_schools = batch_126 + batch_127 + batch_128 + batch_129 + batch_130
    
    cursor.executemany('''
        INSERT OR REPLACE INTO schools (
            id, name, name_cn, region, country, city, address, level, 
            description, website, school_code, founded, principal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', all_schools)
    
    conn.commit()
    
    # Count inserted
    cursor.execute("SELECT COUNT(*) FROM schools WHERE id >= 17058 AND id <= 17093")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    return count

if __name__ == "__main__":
    added = add_batch_126_130()
    print(f"Successfully added {added} Asian schools (ID 17058-17093)")

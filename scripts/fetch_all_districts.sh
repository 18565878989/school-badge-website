#!/bin/bash
#
# 使用curl抓取香港教育局学校数据并导入数据库
#

cd /Users/wangfeng/.openclaw/workspace/school-badge-website

echo "============================================================"
echo "开始批量抓取香港教育局学校数据"
echo "============================================================"

# 区域列表
for file in school-list-cw.html school-list-hke.html school-list-i.html \
            school-list-kc.html school-list-kt.html school-list-kwt.html \
            school-list-n.html school-list-sk.html school-list-sou.html \
            school-list-ssp.html school-list-st.html school-list-tm.html \
            school-list-tp.html school-list-tw.html school-list-wch.html \
            school-list-wts.html school-list-yl.html school-list-ytm.html; do
    
    echo ""
    echo "============================================================"
    echo "正在抓取: $file"
    echo "============================================================"
    
    url="http://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/$file"
    
    # 获取页面内容
    content=$(curl -sL "$url" -A "Mozilla/5.0" 2>/dev/null)
    
    if [ -z "$content" ]; then
        echo "  抓取失败"
        continue
    fi
    
    # 提取学校数量
    school_count=$(echo "$content" | grep -o '<td align="center" class="bodytxt" rowspan=2>' | wc -l)
    echo "  找到约 $school_count 所学校"
    
    # 保存原始HTML
    temp_file="/tmp/edb_${file}"
    echo "$content" > "$temp_file"
    echo "  已保存到 $temp_file"
    
    # 礼貌性延迟
    sleep 3

done

echo ""
echo "============================================================"
echo "所有区域抓取完成!"
echo "============================================================"

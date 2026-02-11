#!/bin/bash
#
# 重新下载所有EDB HTML文件
#

echo "重新下载所有18个区域的学校数据..."

for file in school-list-cw.html school-list-hke.html school-list-i.html \
            school-list-kc.html school-list-kt.html school-list-kwt.html \
            school-list-n.html school-list-sk.html school-list-sou.html \
            school-list-ssp.html school-list-st.html school-list-tm.html \
            school-list-tp.html school-list-tw.html school-list-wch.html \
            school-list-wts.html school-list-yl.html school-list-ytm.html; do
    
    url="http://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/$file"
    echo "下载: $file"
    curl -sL "$url" -A "Mozilla/5.0" -o "/tmp/edb_$file"
    sleep 1
    
done

echo ""
echo "所有文件下载完成!"
ls -lh /tmp/edb_*.html | wc -l

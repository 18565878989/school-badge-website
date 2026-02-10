#!/usr/bin/env python3
"""
验证学校网址有效性
批量检查香港学校官网是否可访问
"""

import sqlite3
import urllib.request
import urllib.error
import ssl
import json
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 配置
CHECK_TIMEOUT = 10
MAX_WORKERS = 10
BATCH_SIZE = 50

def check_url(url):
    """检查单个URL的有效性"""
    result = {
        'url': url,
        'status': 'unknown',
        'http_code': None,
        'final_url': None,
        'error': None
    }
    
    if not url or not url.startswith('http'):
        result['status'] = 'invalid_format'
        return result
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
            }
        )
        
        with urllib.request.urlopen(req, timeout=CHECK_TIMEOUT, context=ctx) as response:
            result['http_code'] = response.status
            result['final_url'] = response.geturl()
            
            if response.status == 200:
                if response.geturl() != url:
                    result['status'] = 'redirect'
                else:
                    result['status'] = 'valid'
            elif 300 <= response.status < 400:
                result['status'] = 'redirect'
            else:
                result['status'] = 'http_error'
    
    except urllib.error.HTTPError as e:
        result['http_code'] = e.code
        if e.code == 404:
            result['status'] = 'not_found'
        elif e.code == 403:
            result['status'] = 'forbidden'
        elif e.code == 500:
            result['status'] = 'server_error'
        else:
            result['status'] = 'http_error'
        result['error'] = str(e)[:100]
    
    except urllib.error.URLError as e:
        result['error'] = str(e.reason)[:100]
        if 'nodename' in str(e.reason).lower() or 'servname' in str(e.reason).lower():
            result['status'] = 'dns_error'
        elif 'connection' in str(e.reason).lower():
            result['status'] = 'connection_error'
        elif 'timeout' in str(e.reason).lower():
            result['status'] = 'timeout'
        elif 'ssl' in str(e.reason).lower():
            result['status'] = 'ssl_error'
        else:
            result['status'] = 'unreachable'
    
    except ssl.SSLCertVerificationError as e:
        result['status'] = 'ssl_error'
        result['error'] = '证书验证失败'
    
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)[:100]
    
    return result

def get_db_schools(limit=None):
    """从数据库获取学校列表"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if limit:
        c.execute(f"""
            SELECT id, name, name_cn, website
            FROM schools 
            WHERE region = 'Hong Kong' 
            AND website IS NOT NULL 
            AND website != ''
            AND website LIKE 'http%'
            ORDER BY name_cn
            LIMIT {limit}
        """)
    else:
        c.execute("""
            SELECT id, name, name_cn, website
            FROM schools 
            WHERE region = 'Hong Kong' 
            AND website IS NOT NULL 
            AND website != ''
            AND website LIKE 'http%'
            ORDER BY name_cn
        """)
    
    schools = [{'id': r[0], 'name': r[1], 'name_cn': r[2], 'website': r[3]} for r in c.fetchall()]
    conn.close()
    return schools

def verify_all_schools(limit=None):
    """验证所有学校网址"""
    schools = get_db_schools(limit)
    total = len(schools)
    
    print("=" * 80)
    print("学校网址验证")
    print("=" * 80)
    print(f"待检查学校: {total}")
    print(f"并行数: {MAX_WORKERS}")
    print(f"超时: {CHECK_TIMEOUT}秒")
    print()
    
    results = []
    stats = {
        'valid': 0,
        'redirect': 0,
        'invalid_format': 0,
        'not_found': 0,
        'dns_error': 0,
        'connection_error': 0,
        'timeout': 0,
        'ssl_error': 0,
        'http_error': 0,
        'unreachable': 0,
        'error': 0
    }
    
    start_time = time.time()
    
    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch = schools[batch_start:batch_end]
        
        print(f"检查中 [{batch_start+1}-{batch_end}/{total}]...", end=" ")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_url, s['website']): s for s in batch}
            
            for future in as_completed(futures):
                school = futures[future]
                url_result = future.result()
                
                results.append({
                    **school,
                    **url_result
                })
                
                status = url_result['status']
                if status in stats:
                    stats[status] += 1
        
        print(f"完成 {batch_end}/{total}")
        
        if batch_end < total:
            time.sleep(0.5)
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("验证结果统计")
    print("=" * 80)
    print(f"总耗时: {elapsed:.1f}秒")
    print(f"平均: {total/elapsed:.1f}个/秒")
    print()
    
    print("状态统计:")
    status_names = {
        'valid': '有效',
        'redirect': '重定向',
        'invalid_format': '格式错误',
        'not_found': '404未找到',
        'dns_error': 'DNS错误',
        'connection_error': '连接错误',
        'timeout': '超时',
        'ssl_error': 'SSL错误',
        'http_error': 'HTTP错误',
        'unreachable': '无法访问',
        'error': '其他错误'
    }
    
    for status, count in sorted(stats.items(), key=lambda x: -x[1]):
        if count > 0:
            name = status_names.get(status, status)
            print(f"  {name}: {count} ({count*100/total:.1f}%)")
    
    return results, stats

def export_results(results, filename=None):
    """导出验证结果"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'scripts/supplement/url_verification_{timestamp}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'name', 'name_cn', 'website', 'status', 'http_code', 'final_url', 'error'
        ])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n结果已导出到: {filename}")
    return filename

def generate_report(results, stats):
    """生成详细报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    total = len(results)
    valid = stats['valid'] + stats['redirect']
    
    report = []
    report.append(f"# 学校网址验证报告 - {timestamp}")
    report.append("")
    report.append("## 统计摘要")
    report.append("")
    report.append(f"- 总学校数: {total}")
    report.append(f"- 有效网址: {valid} ({valid*100/total:.1f}%)")
    report.append(f"- 无效网址: {total - valid} ({(total - valid)*100/total:.1f}%)")
    report.append("")
    report.append("## 无效网址列表")
    report.append("")
    
    invalid = [r for r in results if r['status'] not in ['valid', 'redirect']]
    for r in invalid[:50]:
        report.append(f"- [{r['name_cn'] or r['name']}]({r['website']}) - {r['status']}")
    
    report_text = '\n'.join(report)
    
    with open('scripts/supplement/verification_report.md', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"\n报告已保存到: scripts/supplement/verification_report.md")
    return report_text

def main():
    """主函数"""
    import sys
    
    limit = None
    export_file = None
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
        elif arg.startswith('--export='):
            export_file = arg[8:]
    
    print(f"检查限制: {'全部' if not limit else limit}所学校")
    
    results, stats = verify_all_schools(limit)
    csv_file = export_results(results, export_file)
    generate_report(results, stats)
    
    print("\n" + "=" * 80)
    print("建议: 查看生成的CSV文件，手动更正无效网址")

if __name__ == '__main__':
    main()

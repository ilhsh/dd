#!/usr/bin/env python3
"""
모든 형식의 파일을 생성하는 스크립트
JSON 파일을 기반으로 markdown, html, csv 파일을 생성합니다.
"""

import json
import csv
from pathlib import Path

def generate_all_formats():
    # Load JSON
    with open('cs_infosec_terms.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Generate Markdown
    md_content = f"# {data['title']}\n\n"
    md_content += f"## {data['description']}\n\n"
    md_content += f"## 발견된 용어 (총 {len(data['terms'])}개)\n\n"
    
    for term in data['terms']:
        md_content += f"### {term['name']}\n"
        md_content += f"**빈도**: {term['frequency']}회\n"
        md_content += f"**설명**: {term['description']}\n\n"
    
    with open('cs_infosec_terms.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("✓ Markdown 파일 재생성")

    # Generate CSV
    with open('cs_infosec_terms.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['용어', '빈도', '설명', '카테고리'])
        writer.writeheader()
        for term in data['terms']:
            writer.writerow({
                '용어': term['name'],
                '빈도': term['frequency'],
                '설명': term['description'],
                '카테고리': term['category']
            })
    print("✓ CSV 파일 재생성")

    # Generate HTML
    html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>"""
    html += data['title'] + """</title>
    <style>
        body { font-family: system-ui, sans-serif; line-height: 1.6; color: #333; padding: 40px; max-width: 900px; margin: 0 auto; }
        h1 { font-size: 32px; font-weight: 700; }
        .term-card { border: 1px solid #ddd; border-radius: 6px; padding: 16px; margin-bottom: 16px; background: #f9f9f9; }
        .term-name { font-size: 18px; font-weight: 600; color: #2c5aa0; }
        .term-frequency { background: #e7f3ff; color: #0066cc; padding: 4px 12px; border-radius: 4px; font-size: 12px; margin: 8px 0; display: inline-block; }
        .term-description { color: #555; font-size: 14px; }
        .category { color: #888; font-size: 12px; margin-top: 8px; }
    </style>
</head>
<body>
    <h1>"""
    html += data['title'] + """</h1>
    <p>"""
    html += data['description'] + """</p>
    <p><strong>총 """ + str(len(data['terms'])) + """개의 용어</strong></p>
"""
    
    for term in data['terms']:
        html += f"""    <div class="term-card">
        <div class="term-name">{term['name']}</div>
        <div class="term-frequency">빈도: {term['frequency']}회</div>
        <div class="term-description">{term['description']}</div>
        <div class="category">{term['category']}</div>
    </div>
"""
    
    html += """</body>
</html>
"""
    
    with open('cs_infosec_terms.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ HTML 파일 재생성")

    print("\n모든 형식의 파일이 재생성되었습니다!")

if __name__ == "__main__":
    generate_all_formats()

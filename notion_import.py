#!/usr/bin/env python3
"""
Notion에 컴퓨터공학 및 정보보안 용어를 가져오는 스크립트
Notion API를 사용하려면 NOTION_API_KEY 환경변수를 설정해야 합니다.

설치:
    pip install notion-client

사용법:
    export NOTION_API_KEY="your_api_key_here"
    export NOTION_DATABASE_ID="your_database_id_here"
    python notion_import.py
"""

import json
import os
from datetime import datetime

def import_to_notion():
    try:
        from notion_client import Client
    except ImportError:
        print("Error: notion-client 패키지가 설치되지 않았습니다.")
        print("설치: pip install notion-client")
        return False

    api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')

    if not api_key or not database_id:
        print("Error: NOTION_API_KEY와 NOTION_DATABASE_ID 환경변수가 필요합니다.")
        return False

    # Load the terms data
    with open('cs_infosec_terms.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize Notion client
    notion = Client(auth=api_key)

    print(f"Notion에 {len(data['terms'])}개의 용어를 추가합니다...")

    for term in data['terms']:
        try:
            # Create a page in the database
            response = notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Term": {
                        "title": [
                            {
                                "text": {
                                    "content": term['name'],
                                }
                            }
                        ]
                    },
                    "Description": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": term['description'],
                                }
                            }
                        ]
                    },
                    "Frequency": {
                        "number": term['frequency']
                    },
                    "Category": {
                        "select": {
                            "name": term['category']
                        }
                    },
                    "Source": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": "포트폴리오 PDF 자동 추출"
                                }
                            }
                        ]
                    },
                    "Imported": {
                        "date": {
                            "start": datetime.now().isoformat()
                        }
                    }
                }
            )
            print(f"✓ '{term['name']}' 추가됨")
        except Exception as e:
            print(f"✗ '{term['name']}' 추가 실패: {str(e)}")

    print("완료!")
    return True

if __name__ == "__main__":
    import_to_notion()

import json
import requests
from typing import List
from app.database import SessionLocal
from app.crud import create_or_update_place
from app.schemas.place import PlaceBase
from bs4 import BeautifulSoup

# Load configuration
with open('secrets.json', 'r') as file:
    config = json.load(file)

TOURAPI_KEY = config.get("TOURAPI_KEY")

def fetch_content_ids() -> List[dict]:
    print("Fetching content IDs...")
    url = "https://api.visitkorea.or.kr/openapi/service/rest/KorService/areaBasedList"
    params = {
        "ServiceKey": TOURAPI_KEY,
        "contentTypeId": "",
        "areaCode": 34,
        "MobileOS": "ETC",
        "MobileApp": "TourAPI3.0_Guide",
        "numOfRows": 500,
        "arrange": "B",
        "pageNo": 1,
        "_type": "json"
    }

    response = requests.get(url, params=params)
    print(f"Response status code: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=4))

    if 'response' not in data or 'body' not in data['response'] or 'items' not in data['response']['body']:
        print(f"Unexpected data format: {data}")
        return []

    items = data['response']['body']['items']['item']
    print(f"Number of items fetched: {len(items)}")

    content_ids = [{'contentid': item['contentid'],'sigunguCode': item.get('sigungucode')} for item in items]
    return content_ids

def fetch_tour_data(content_ids: List[dict]):
    print("Fetching detailed tour data...")
    url = "https://api.visitkorea.or.kr/openapi/service/rest/KorService/detailCommon"
    db = SessionLocal()

    for content_id in content_ids:
        content_num = content_id['contentid']
        sigungu_code = content_id.get('sigunguCode')
        params = {
            "ServiceKey": TOURAPI_KEY,
            "contentId": content_num,
            "MobileOS": "ETC",
            "MobileApp": "TourAPI3.0_Guide",
            "defaultYN": "Y",
            "firstImageYN": "Y",
            "areacodeYN": "Y",
            "catcodeYN": "Y",
            "addrinfoYN": "Y",
            "mapinfoYN": "Y",
            "overviewYN": "Y", 
            "_type": "json"
        }

        response = requests.get(url, params=params)
        print(f"Response status code: {response.status_code}")
        data = response.json()

        if 'response' not in data or 'body' not in data['response'] or 'items' not in data['response']['body']:
            print(f"Unexpected data format: {data}")
            continue

        items = data['response']['body']['items']['item']

        for item in items:
            if not item.get('firstimage'):  # firstimage가 없으면 이 항목을 건너뜀
                continue
            # hmpg 필드에서 URL 추출
            hmpg_html = item.get('hmpg', '')
            hmpg_url = ''
            if hmpg_html:
                soup = BeautifulSoup(hmpg_html, 'html.parser')
                hmpg_tag = soup.find('a')
                if hmpg_tag and 'href' in hmpg_tag.attrs:
                    hmpg_url = hmpg_tag['href']

            place = PlaceBase(
                title=item.get('title', ''),
                addr1=item.get('addr1', ''),
                addr2=item.get('addr2', ''),
                firstimage=item.get('firstimage', ''),
                tel=item.get('tel', ''),
                contentId=item.get('contentid', None),
                hmpg=hmpg_url,
                overview=item.get('overview', ''),  # 추가된 부분
                sigunguCode=sigungu_code
            )
            create_or_update_place(db, place)
            print(f"Saved place: {place.title}")

    db.close()

if __name__ == "__main__":
    content_ids = fetch_content_ids()
    fetch_tour_data(content_ids)
    print("Tour data fetching completed.")

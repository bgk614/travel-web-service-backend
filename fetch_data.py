import json
import requests
from typing import List
from app.database import SessionLocal
from app.crud import create_or_update_place
from app.schemas.place import PlaceBase

# Load configuration
with open('secrets.json', 'r') as file:
    config = json.load(file)

TOURAPI_KEY = config.get("TOURAPI_KEY")

def fetch_content_ids() -> List[int]:
    print("Fetching content IDs...")
    url = "https://api.visitkorea.or.kr/openapi/service/rest/KorService/areaBasedList"
    params = {
        "ServiceKey": TOURAPI_KEY,
        "contentTypeId": "",
        "areaCode": 34,
        "MobileOS": "ETC",
        "MobileApp": "TourAPI3.0_Guide",
        "numOfRows": 100,
        "arrange": "B",
        "pageNo": 1,
        "_type": "json"
    }

    response = requests.get(url, params=params)
    print(f"Response status code: {response.status_code}")
    data = response.json()

    if 'response' not in data or 'body' not in data['response'] or 'items' not in data['response']['body']:
        print(f"Unexpected data format: {data}")
        return []

    items = data['response']['body']['items']['item']
    print(f"Number of items fetched: {len(items)}")

    content_ids = [item['contentid'] for item in items]
    return content_ids

def fetch_tour_data(content_ids: List[int]):
    print("Fetching detailed tour data...")
    url = "https://api.visitkorea.or.kr/openapi/service/rest/KorService/detailCommon"
    db = SessionLocal()

    for content_id in content_ids:
        params = {
            "ServiceKey": TOURAPI_KEY,
            "contentId": content_id,
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
            place = PlaceBase(
                title=item.get('title', ''),
                addr1=item.get('addr1', ''),
                addr2=item.get('addr2', ''),
                firstimage=item.get('firstimage', ''),
                tel=item.get('tel', ''),
                contentId=item.get('contentid', None),
                hmpg=item.get('hmpg', ''),
                overview=item.get('overview', '')  # 추가된 부분
            )
            create_or_update_place(db, place)
            print(f"Saved place: {place.title}")

    db.close()

if __name__ == "__main__":
    content_ids = fetch_content_ids()
    fetch_tour_data(content_ids)
    print("Tour data fetching completed.")

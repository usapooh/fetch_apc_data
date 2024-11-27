import requests
import datetime
import time
import zoneinfo
import tqdm
from pprint import pprint

BASE_URL = "https://openapi.safie.link"
API_KEY = "YOUR API KEY HERE"
TIMEDELTA_DAYS = -1 # -1なら昨日, -2なら一昨日, -3なら三日前

def main():
    # デバイスの一覧を取得
    device_list: list = fetch_device_list()
    if device_list == None:
        return
    
    # 取得開始時間と終了時間を設定
    jst = zoneinfo.ZoneInfo("Asia/Tokyo")
    start = (datetime.datetime.now(jst) + datetime.timedelta(days=TIMEDELTA_DAYS)).strftime("%Y-%m-%dT00:00:00.000000+09:00")
    end = (datetime.datetime.now(jst) + datetime.timedelta(days=TIMEDELTA_DAYS)).strftime("%Y-%m-%dT23:59:59.999999+09:00")
    
    # デバイスごとにカウント結果を取得
    outcome: list = []
    for device in tqdm.tqdm(device_list):
        count_list: list = fetch_apc_count_data(device["device_id"], start, end)
        if count_list == None:
            return
        outcome.append({"device_name": device["setting"]["name"], "count_list": count_list})
        
    pprint(outcome)
    # outcomeが下記形式のカウント結果です
    # [{device_name: カメラ名称,
    #  count_list: カメラごとのカウント結果}]

def fetch_device_list() -> list:
    # APIキーに紐づくデバイス一覧を取得
    # item_idでAPC APIオプションがあるカメラのみにフィルターする
    # 各オプションのitem_idはhttps://developers.safie.link/terms-of-api下部に記載
    
    url = f"{BASE_URL}/v2/devices"
    item_id = 960 # AI People Count APIのオプションitem_id 
    headers = {"Safie-API-key": API_KEY}
    
    limit = 100
    offset = 0
    device_list = []
    while True:
        params = {
            "item_id": item_id,
            "limit": limit,
            "offset": offset
        }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
        except:
            print(f"デバイス一覧取得失敗 {res.text}")
            return None
        total = res.json()["total"]
        device_list += res.json()["list"]
        offset += limit
        
        if offset >= total:
            break
    
    return device_list

def fetch_apc_count_data(device_id: str, start: str,  end: str) -> list:
    # デバイスごとにstartとendの間のカウントデータを取得
    url = f"{BASE_URL}/v2/devices/{device_id}/pd_captures"
    headers = {"Safie-API-key": API_KEY}
    
    limit = 500
    offset = 0
    count_list = []
    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "sort": "ascending",
            "start": start,
            "end": end
        }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
        except:
            print(f"結果取得エラー {device_id} {res.text}")
            return None
            
        total = res.json()["total"]
        count_list += res.json()["list"]
        offset += limit
        if offset >= total:
            break
        
        # Rate Limit 60req / 15min  
        # time.sleep(15)
        
    return count_list
        
if __name__ == "__main__":
    main()
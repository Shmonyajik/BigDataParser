import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
from datetime import datetime
import time

def request(url):
    headers = {
        "accept": "*/*",
        "x-api-key": "ff96c522-df70-5747-8273-9eabfa7d6488"
    }
    return requests.get(url, headers=headers).text

def delete_old_documents(es: Elasticsearch, new_documents: list[str], index_name: str):
    query = {
        "query": {
            "bool": {
                "must_not": {
                    "terms": {
                        "_id": new_documents
                    }
                }
            }
        }
    }

    results = scan(es, query=query, index=index_name)
    for doc in results:
        doc_id = doc['_id']
        es.delete(index=index_name, id=doc_id)

def get_max_divisor(number, limit):
    max_divisor = 1
    for i in range(2, min(number, limit) + 1):
        if number % i == 0:
            max_divisor = i
    return max_divisor

def get_rarity_price_data(collection_addresses: dict[str, str], es: Elasticsearch):
    collection_ownerscount = {}

    for key in collection_addresses:
        #cтрока запроса для выборки токенов
        tokens_url = "https://api.reservoir.tools/tokens/v6?collection="+collection_addresses[key]+"&flagStatus=-1&sortBy=tokenId&sortDirection=asc&limit=100&includeDynamicPricing=true&includeLastSale=true"
        
        # строка запроса для выборки метаданных коллекции(для получения колва токенов)
        collection_metadata_url = "https://api.reservoir.tools/collections/v7?id="+ collection_addresses[key] 
    
        tokens_count = json.loads(request(collection_metadata_url)).get("collections", [])[0]["tokenCount"]
        collection_ownerscount[key] = json.loads(request(collection_metadata_url)).get("collections", [])[0]["ownerCount"]
        
########################################################## сохранение метаданных в файл для отладки
        file_path = "token.json"
        with open(file_path, 'w') as file:
            json.dump(json.loads(request(tokens_url)).get("tokens", [])[0], file, indent=4)
###########################################################  

        continuation = None # токен смещения
        new_tokens: list[str] = []
    
        i = 0
        while i < int(tokens_count):
            if(continuation):
                if(tokens_url.__contains__("&continuation=")):
                    tokens_url=tokens_url[:(tokens_url.find("&continuation=")+14)]+continuation #14
                else:
                    tokens_url = tokens_url+"&continuation="+continuation
            data = json.loads(request(tokens_url))
            continuation = data.get("continuation")
            for token in enumerate(data.get("tokens", [])):
                _token = token[1]["token"]
                token_id = f"{_token.get("contract")}-{_token.get("tokenId")}"
                new_tokens.append(token_id)
                es.index(
                    index=key+"_tokens",
                    body=_token,
                    id=token_id
                )
                i+=1
                print(f"Токен {i}/{tokens_count} из коллекции {collection_addresses[key]}")
        
        delete_old_documents(es, new_documents=new_tokens, index_name=key+"_tokens")
        es.indices.refresh(index=key+"_tokens")
    return collection_ownerscount

def get_owners_destribution(
    collection_addresses: dict[str, str],
    collection_ownerscount: dict,
    es: Elasticsearch
):
    for key in collection_addresses:
        divisor = get_max_divisor(collection_ownerscount[key], 501)
        #cтрока запроса для выборки держателей токенов
        owners_url = "https://api.reservoir.tools/owners/v2?collection="+collection_addresses[key]+"&offset=0&limit="+str(divisor)+"&displayCurrency=0xdAC17F958D2ee523a2206206994597C13D831ec7"

########################################################### сохранение метаданных в файл для отладки
        file_path = "owner.json"
        with open(file_path, 'w') as file:
            json.dump(json.loads(request(owners_url)).get("owners", [])[0], file, indent=4)
###########################################################  

        continuation = 0 # токен смещения
        new_owners: list[str] = []
    
        i = 0
        while i < int(collection_ownerscount[key]):
            
            if(owners_url.__contains__("&offset=")):
                owners_url=owners_url[:(owners_url.find("&offset=")+8)]+str(continuation)+"&limit="+str(divisor)+"&displayCurrency=0xdAC17F958D2ee523a2206206994597C13D831ec7"
            else:
                owners_url = owners_url+"&offset="+str(continuation)+"&limit="+str(divisor)+"&displayCurrency=0xdAC17F958D2ee523a2206206994597C13D831ec7"
            data = json.loads(request(owners_url))
            continuation +=divisor
            for owner in enumerate(data.get("owners", [])):
                _owner = owner[1]
                owner_id = f"{collection_addresses[key]}-{_owner.get("address")}"
                new_owners.append(owner_id)
                es.index(
                    index=key+"_owners",
                    body=_owner,
                    id=owner_id)
                i+=1
                print(f"Владелец {i}/{collection_ownerscount[key]} из коллекции {collection_addresses[key]}")
                
        delete_old_documents(es, new_documents=new_owners, index=key+"_owners")
        es.indices.refresh(index=key+"_owners")

def get_user_acrtivity(
    collection_addresses: dict[str, str],
    collections_realese_date: dict[str, str],
    es: Elasticsearch
):
    for key in collection_addresses:
        #cтрока запроса для выборки активностей
        activities_url = "https://api.reservoir.tools/collections/activity/v6?collection="+collection_addresses[key]+"&excludeSpam=true&limit=1000&sortBy=createdAt&includeMetadata=false"  
        
########################################################## сохранение метаданных в файл для отладки
        file_path = "activity.json"
        with open(file_path, 'w') as file:
            json.dump(json.loads(request(activities_url)).get("activities", [])[0], file, indent=4)
###########################################################  

        continuation = None # токен смещения
        createdAt = "2023-10-01T00:00:00.000Z"
        
        while datetime.strptime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ") > datetime.strptime(collections_realese_date[key], "%Y-%m-%dT%H:%M:%S.%fZ"):
            if(continuation):
                if(activities_url.__contains__("&continuation=")):
                    activities_url=activities_url[:(activities_url.find("&continuation=")+14)]+continuation #14
                else:
                    activities_url = activities_url+"&continuation="+continuation
            data = json.loads(request(activities_url)).get("activities", [])
            continuation = json.loads(request(activities_url)).get("continuation")
            y=0
            while y < len(data):
                es.index(index=key+"_activities", body={"createdAt": data[y]["createdAt"]})
                y+=1    
            createdAt = data[y-1]["createdAt"]
            print(f"Дата активности: {createdAt}")
        es.indices.refresh(index=key+"_activities")

def main():
    es = Elasticsearch(hosts=['http://elasticsearch-node1:9200', 'http://elasticsearch-node2:9200'])

    collections_addresses = {
        "shonen_junk":"0xF4121a2880c225f90DC3B3466226908c9cB2b085",
        "azuki": "0xED5AF388653567Af2F388E6224dC7C4b3241C544",
        "kiwami": "0x701A038aF4Bd0fc9b69A829DdcB2f61185a49568"
        }
    collections_realese_date = {
        "shonen_junk":"2023-01-31T03:00:00.000Z" ,
        "azuki": "2023-01-10T03:00:00.000Z",
        "kiwami": "2023-03-21T03:00:00.000Z"
        }
    
    for key in collections_addresses:
        es.indices.create(index=key+"_tokens")
        es.indices.create(index=key+"_owners")
        es.indices.create(index=key+"_activities")
    
    while True:
        print("Начало индексации")
        collection_ownerscount = get_rarity_price_data(collections_addresses, es)
        get_owners_destribution(collections_addresses, collection_ownerscount, es)
        get_user_acrtivity(collections_addresses,collections_realese_date, es)

        print("Индексация завершена")
        time.sleep(24 * 60 * 60)


if(__name__ == "__main__"):
    main()
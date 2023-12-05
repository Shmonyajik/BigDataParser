import requests
from elasticsearch import Elasticsearch
import json

def request(url):
    headers = {
        "accept": "*/*",
        "x-api-key": "demo-api-key"
    }
    return requests.get(url, headers=headers).text

def get_data():
    index_name = "shonen-junk"
    es = Elasticsearch(hosts=['http://elasticsearch-node1:9200', 'http://elasticsearch-node2:9200'])

    number_of_shards = 3
    settings = {
        "settings": {
            "number_of_shards": number_of_shards
        }
    }

    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name, body=settings)

    collection_metadata_url = "https://api.reservoir.tools/collections/v7?id=0xf4121a2880c225f90dc3b3466226908c9cb2b085"
    #tokens_url = "https://api.reservoir.tools/tokens/v6?collection=0xf4121a2880c225f90dc3b3466226908c9cb2b085&flagStatus=-1&sortBy=tokenId&sortDirection=asc&limit=100&includeAttributes=true&includeDynamicPricing=true&continuation=MHhmNDEyMWEyODgwYzIyNWY5MGRjM2IzNDY2MjI2OTA4YzljYjJiMDg1Xzk5"

    #tokens_url = "https://api.reservoir.tools/tokens/v6?collection=0xf4121a2880c225f90dc3b3466226908c9cb2b085&flagStatus=-1&sortBy=tokenId&sortDirection=asc&limit=100&includeAttributes=true&includeDynamicPricing=true"
    
    tokens_url = "https://api.reservoir.tools/tokens/v6?collection=0x701A038aF4Bd0fc9b69A829DdcB2f61185a49568&flagStatus=-1&sortBy=tokenId&sortDirection=asc&limit=100&includeDynamicPricing=true&includeLastSale=true"

    
###########################################################
    file_path = "token.json"
    with open(file_path, 'w') as file:
        json.dump(json.loads(request(tokens_url)).get("tokens", [])[0], file, indent=4)
###########################################################  
    tokens_count = json.loads(request(collection_metadata_url)).get("collections", [])[0]["tokenCount"]
    # json_token = json.loads(request(tokens_url)).get("tokens", [])[0]
    # create_index(json_token)
    continuation = None
    
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
            es.index(index=index_name, body=token[1]["token"])
            i+=1
            print(f"{i}/{tokens_count}")
            
    es.indices.refresh(index=index_name)

def main():
    get_data()


if(__name__ == "__main__"):
    main()
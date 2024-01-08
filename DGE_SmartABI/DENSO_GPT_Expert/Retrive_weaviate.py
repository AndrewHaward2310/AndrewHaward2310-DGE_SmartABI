import weaviate



#response = client.query.get("Denso_Document", ['source','page','content']).do()
#User_query = "Làm thế nào để Sửa lỗi int3170 LNCT800 ở dây chuyền 1.1.1.1"

def filter_machine_name(client, query):
    response = (
        client.query
        .get("Denso_Document",properties=["machine_name"])
        .with_bm25(
          query=query,
          properties=["machine_name"]
        )
        .with_limit(1)
        .do()
    )
    try:
        return response["data"]["Get"]["Denso_Document"][0]["machine_name"]
    except:
        return '*'

def filter_line(client , query ):
    response = (
        client.query
        .get("Denso_Document",properties=["line","code"])
        .with_bm25(
          query=query,
          properties=["line","code"]
        )
        .with_limit(1)
        .do()
    )
    line_filter= {
        "line": '*',
        "code": '*'
    }
    try:
        line_filter["line"] = response["data"]["Get"]["Denso_Document"][0]["line"]
    except:
        pass
    try:
        line_filter["code"] = response["data"]["Get"]["Denso_Document"][0]["code"]
    except:
        pass
    return line_filter

def get_filter(client,query):
    machine_name  = filter_machine_name(client=client,query=query)
    line_filter = filter_line(client=client,query=query)
    filter = {
        "operator": "And",
        "operands": [
            {
                "path": ["machine_name"],
                "operator": "Like",
                "valueText": machine_name,
            },
            {
                "operator": "And",
                "operands": [
                    {
                        "path": ["line"],
                        "operator": "Like",
                        "valueText": line_filter["line"],
                    },
                    {
                        "path": ["code"],
                        "operator": "Like",
                        #"valueText": 'CNC1'
                        "valueText": line_filter["code"],
                    },
                ]
            }
        ]
    }
    return filter


def keyword_retrive(client,query,filter):
    
    response = (
        client.query
        .get("Denso_Document",properties=['source','page','content',"machine_name","code","line","description"])
        .with_where(filter)
        .with_bm25(
          query=query,
          properties=['description^2',"content"]
        )
        .with_additional("score")
        .with_limit(2)
        .do()
    )
    list = []
    for result in response["data"]["Get"]['Denso_Document']:
        list.append({
            'source' :result["source"],
            'page' :result["page"],
            'type': '1_kw',
            'score': result["_additional"]["score"]
        })
    return list
    
    
def hybrid_retrive(client , query,filter ):
    response2 = (
        client.query
        .get("Denso_Document", properties=['source','page','content',"machine_name","code","line","description"])
        .with_where(filter)
        .with_hybrid(
            query=query,
            alpha= 0.4,
            properties=['description^2',"content"]
        )
        .with_additional(["score"])
        .with_limit(2)
        .do()
    )
    list = []
    for result in response2["data"]["Get"]['Denso_Document']:
        list.append({
            'source' :result["source"],
            'page' :result["page"],
            'type': '2_hb',
            'score': result["_additional"]["score"]
        })
    return list

def semantic_retrive(client, query,filter ):
    response3 = (
        client.query
        .get("Denso_Document", properties=['source','page','content',"machine_name","code","line","description"])
        .with_where(filter)
        .with_near_text({
            "concepts": query
        })
        .with_limit(2)
        .with_additional(["certainty"])
        .do()
    )
    list = []
    for result in response3["data"]["Get"]['Denso_Document']:
        list.append({
            'source' :result["source"],
            'page' :result["page"],
            'type': '3_sm',
            'score': result["_additional"]["certainty"]
        })
    return list

#responses_list = keyword_retrive() + hybrid_retrive()+semantic_retrive()


def get_3_page(list_of_responses):
    import pandas as pd
    df = pd.DataFrame(list_of_responses)
    df['value_count']=df.groupby(["source","page"])['score'].transform('count')
    df["score"]=df["score"].astype(float)
    df['rank'] = df.sort_values('score', ascending=False).groupby("type").cumcount() + 1
    df = df.sort_values(by= ["value_count","rank","type"], ascending=[False,True,True]).drop_duplicates(subset=["source","page"], keep= "first")
    list = df.head(3).to_dict(orient='records')
    return list


if __name__ == "__main__":
    client = weaviate.Client("http://localhost:8081")
    print("weaviatedb is ready: ",client.is_ready())
    query = "Làm thế nào để sửa lỗi int3170 trên máy CNC1"
    filter = get_filter(client=client,query=query)
    list1 = keyword_retrive(client=client,query= query,filter=filter)
    list2 = hybrid_retrive(client=client,query= query,filter=filter)
    list3 = semantic_retrive(client=client,query=query,filter=filter)
    responses_list = list1+list2+list3
    ##print(get_4_page(responses_list))
    import pandas as pd
    df = pd.DataFrame(responses_list)
    result = get_3_page(responses_list)
    
    print(filter)
    print(df)
    print(result)
    #print(list3)
    #print(list1)

    #print("keyword\n",keyword_retrive())
    #print("Hybrid\n",hybrid_retrive())
    #print("semantic\n",semantic_retrive())

def List_of_meta_data(query):
    client = weaviate.Client("http://localhost:8081")
    print("weaviatedb is ready: ",client.is_ready())
    query = query
    filter = get_filter(client=client,query=query)
    list1 = keyword_retrive(client=client,query= query,filter=filter)
    list2 = hybrid_retrive(client=client,query= query,filter=filter)
    list3 = semantic_retrive(client=client,query=query,filter=filter)
    responses_list = list1+list2+list3
    ##print(get_4_page(responses_list))
    #import pandas as pd
    #df = pd.DataFrame(responses_list)
    result = get_3_page(responses_list)
    return result

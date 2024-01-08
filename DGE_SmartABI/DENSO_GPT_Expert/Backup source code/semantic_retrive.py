from langchain.vectorstores.chroma import Chroma
import Model

model = Model.Embedding_Model.embedding_model2
database = Chroma(persist_directory="./chroma_db", embedding_function=model)

def get_similar_chunks(query,db=database,k=5):
 chunks = db.similarity_search_with_score(query=query,k=k)
 return chunks

def retrive_Semantic(query):
 query = query
 chunks = get_similar_chunks(query=query.lower())
 dict = []
 i = 1
 for chunk in chunks:
  #if chunk[1]>30:
    dict.append({
      chunk[0].metadata['source']:chunk[0].metadata['page']
    })
    #print("      Score:",chunk[1])
    #print("source:",chunk[0].metadata['source'],"page",chunk[0].metadata['page'])
    #print(chunk[0].page_content)
    #print(chunk[0].page_content)
    #with open("result.txt",'a',encoding='utf-8') as f:
    # f.write(str(i))
    # 
    # f.write(". Score:")
    # f.write(str(chunk[1]))
    # f.write("\n")
    # f.writelines(str(chunk[0].metadata['source']))
    # f.writelines(str(chunk[0].metadata['page']))
    # #f.write("source:",chunk[0].metadata['source'],"page",chunk[0].metadata['page'])
    # f.write(str(chunk[0].page_content))
    # f.write("\n-------------------------------------------\n")
    #i = i+1
 return dict

#print("Semantic Result: ")
#query = "sửa lỗi INt3170"
#dict1 = retrive_Semantic(query=query)
#print(dict1)
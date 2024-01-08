import Model
import pinecone

def retrive_Keyword(query):
 embedding_model = Model.Embedding_Model.embedding_model
#sparse_model = Model.Sparse_Model.sparse_model
 import pickle
 with open('model.pkl', 'rb') as f:
    sparse_model = pickle.load(f)

 
 index_name = "test3"
 pinecone.init(
    api_key='b4c87a8a-b071-4410-b6ca-a61ec0e8e019',
    environment="gcp-starter"
 )
 if index_name not in pinecone.list_indexes():
  print("Cant find  ", index_name, " .Try another indexname")
 else:
  index = pinecone.Index(index_name)
 

 def hybrid_scale(dense, sparse, alpha: float):
    """Hybrid vector scaling using a convex combination

    alpha * dense + (1 - alpha) * sparse

    Args:
        dense: Array of floats representing
        sparse: a dict of `indices` and `values`
        alpha: float between 0 and 1 where 0 == sparse only
               and 1 == dense only
    """
    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be between 0 and 1")
    # scale sparse and dense vectors to create hybrid search vecs
    hsparse = {
        'indices': sparse['indices'],
        'values':  [v * (1 - alpha) for v in sparse['values']]
    }
    hdense = [v * alpha for v in dense]
    return hdense, hsparse

#######################



 query = query
# create sparse and dense vectors
#sparse = sparse_model.encode_documents(query)
 sparse = sparse_model.encode_queries(query)
 dense = embedding_model.encode(query).tolist()
 dict = []
 hdense, hsparse = hybrid_scale(dense, sparse, alpha=0)# KEYWORD
 # search
 result = index.query(
     top_k=5,
     vector=hdense,
     sparse_vector=hsparse,
     include_metadata=True,
     include_values=False,
     filter={
       'source':'sample pdf\LNCT800SoftwareApplicationManual-265-280.pdf'
     }
 )
 #print(result)
 scores = {}
 #print(result['matches'][0].metadata)
 for chunk in result['matches']:
    index = 'source: '+str(chunk.metadata['source'])+ " page: "+str(chunk.metadata['page'])
    dict.append({
       str(chunk.metadata['source']) : int(chunk.metadata['page'])
    })
    scores[index] ={'score':0,'count':0, 'mean':0}
 for chunk in result['matches']:
    index = 'source: '+str(chunk.metadata['source'])+ " page: "+str(chunk.metadata['page'])
    scores[index]['score'] =scores[index]['score']+ float(chunk.score)
    scores[index]['count'] = scores[index]['count'] +1
    scores[index]['mean'] = scores[index]['score']/scores[index]['count']


# for score in scores:
#   print(score,'.....',scores[score]['count'],'......',scores[score]['score'])
 return dict


#print("Keyword Result: ")
#query = "Sửa lỗi INT3170"
#dict1 = retrive_Keyword(query=query)
#print(dict1)


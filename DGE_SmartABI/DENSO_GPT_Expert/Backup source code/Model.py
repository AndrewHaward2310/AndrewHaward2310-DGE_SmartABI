from langchain.embeddings import HuggingFaceEmbeddings
from pinecone_text.sparse import BM25Encoder
from pinecone_text.sparse import SpladeEncoder
from sentence_transformers import SentenceTransformer



class Embedding_Model:
 embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
 embedding_model2 = HuggingFaceEmbeddings(model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
 dim = 384
 name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

class Sparse_Model:
 #sparse_model = SpladeEncoder()
 sparse_model = BM25Encoder()
#vector = Sparse_Model.sparse_model.encode_documents("Hello my name is Nguyen")
#print((vector))

#embeding_vector = Embedding_Model.embedding_model.encode("Hello my name is Nguyeeeeeeeeeeeeen")
#print(Embedding_Model.embedding_model.decode(embeding_vector))
#print(type(embeding_vector.tolist()))



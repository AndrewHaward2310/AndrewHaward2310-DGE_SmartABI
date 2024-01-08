import pinecone
import os
from dotenv import load_dotenv,find_dotenv
import Model
from langchain.docstore.document import Document
import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas

#Chưa load đc
#load_dotenv(find_dotenv(),override=True)
#PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
#PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")

#Load Model Embedding và BM25
embedding_model = Model.Embedding_Model.embedding_model
#sparse_model = Model.Sparse_Model.sparse_model
embedding_model2 = Model.Embedding_Model.embedding_model2
try: 
	import pickle
	with open('model.pkl', 'rb') as f:
		sparse_model = pickle.load(f)
except:
	sparse_model = Model.Sparse_Model.sparse_model


#Splitter 
def split_document(docs,chunk_size = 1000, chunk_overlap = 0):
	text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap
	) 
	chunks = text_splitter.create_documents([docs])
	return chunks


#CREATE CHUNKS
def load_data(file_path):
	"""
	important features: id, page name, page number, document text
	"""
	chunks = []#create empty chunks
	data = []
	if file_path.split('.')[-1] == 'pdf':
		#Load pdf into pages
		pages = fitz.open(file_path)
		#insert từng chunk vào chunk
		id = 0
		for page in pages:
			text = page.get_text().replace('\n', ' ').lower() # get text, remove \n and lowercase.
			docs = split_document(text) # return Langchain Documents list
	
			for doc in docs:
				id += 1
				
				#gen chunk.
				chunk = Document(
					page_content=doc.page_content, 
					metadata={'id' : id,'source': pages.name,'page': page.number,'text' : doc.page_content})
				data.append(doc.page_content)
				chunks.append(chunk)

	if file_path.split('.')[-1] == 'xlsx':
		#Load xlsx file
		xls = pandas.ExcelFile(file_path)
		id = 0
		for sheet in xls.sheet_names:
			# get text, remove \n and lowercase.
			df = pandas.read_excel(xls, sheet)
			df = df.fillna('')
			text = df.values.astype(str)
			lines = []
			for txt in text:
				lines.append(', '.join(txt))
			text = '\n'.join(lines)
			docs = split_document(text) # return Langchain Documents list
	
			for doc in docs:
				id += 1
				#gen chunk.
				chunk = Document(
					page_content=doc.page_content, 
					metadata={
						'id' : id,
						'source': file_path,
						'page': xls.sheet_names.index(sheet),
						'text' : doc.page_content
						}
					)
				data.append(doc.page_content)
				chunks.append(chunk)
	sparse_model.fit(data)
	import pickle
	with open('model.pkl','wb') as f:
		pickle.dump(sparse_model,f)
	return chunks

#INSERT TO PINECONE
def upsert_to_pinecone(chunks,index_name):
 pinecone.init(
    api_key='b4c87a8a-b071-4410-b6ca-a61ec0e8e019',
    environment="gcp-starter"
  )



 if index_name not in pinecone.list_indexes():
   # create the index
   pinecone.create_index(
     index_name,
     dimension=Model.Embedding_Model.dim,
     metric="dotproduct",
     pod_type="s1"
   )
 index = pinecone.Index(index_name)
 
 sparse_vector = []
 dense_vector = []
 for chunk in chunks:
   sparse_vector.append(sparse_model.encode_documents(chunk.page_content))
   dense_vector.append(embedding_model.encode(chunk.page_content).tolist())
 
 
 upsert = []
 for chunk,sparse, dense in zip(chunks,sparse_vector,dense_vector):
   upsert.append({
     'id' : str(chunk.metadata['id']),
     'sparse_values': sparse,
     'values': dense,
     'metadata': chunk.metadata
   })
 index.upsert(upsert)
 print(index.describe_index_stats())

#INSERT TO CHROMA
def insert_to_chroma(chunks):
  from langchain.vectorstores.chroma import Chroma
  model = embedding_model2
  Chroma.from_documents(chunks, model, persist_directory="./chroma_db")
  print("Inserted to Chroma")


####TESTTING

#index_name = "test3"
p1 = "DENSO Document\Thao tác thay filter máy hút bụi - May Shot Blast.xlsx"
#p2 = "sample pdf/LNCT800SoftwareApplicationManual (1).pdf"
chunks = load_data(p1)
##return list of langchain core Document.
#print(type(chunks[0]))
print(chunks)

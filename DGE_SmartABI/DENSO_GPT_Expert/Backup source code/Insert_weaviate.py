import weaviate
import weaviate.classes as wvc
import os

client = weaviate.Client("http://localhost:8081")
print("weaviatedb is ready: ",client.is_ready())
client.schema.delete_all()
class_obj = {
    "class": "Denso_Document",
    "vectorizer": "text2vec-transformers",  # this could be any vectorizer
    "moduleConfig": {
        "text2vec-transformers": {  # this must match the vectorizer used
            "vectorizeClassName": False,
            "model": "paraphrase-multilingual-MiniLM-L12-v2",
        }
    },
    "properties": [
        {
            "name": "source",
            "dataType": ["text"],
            "moduleConfig": {
                "text2vec-transformers": {  # this must match the vectorizer used
                    "skip": True,
                    #"tokenization": "lowercase"
                }
            }
        },
        {
            "name": "page",
            "dataType": ["text"],
            "moduleConfig": {
                "text2vec-transformers": {  # this must match the vectorizer used
                    "skip": True  # Don't vectorize body
                    #"tokenization": "whitespace"
                }
            }
        },
        {
            "name": "content",
            "dataType": ["text"],
            "moduleConfig": {
                "text2vec-transformers": {  # this must match the vectorizer used
                    "vectorizePropertyName": True,  # vectorize body
                    #"tokenization": "whitespace"
                }
            }
        },
    ],
}
# Add the PDFDocument schema
try:
    client.schema.create_class(class_obj)
except:
   print("Using Denso Document collection")
# Get the schema to verify that it worked
#schema = client.schema.get()
#import json
#print(json.dumps(schema, indent=4))



import fitz
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_document(docs,chunk_size = 1000, chunk_overlap = 0):
 text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    ) 
 chunks = text_splitter.create_documents([docs])
 return chunks


def pdf_readable_chunk(file_path):
    pages = fitz.open(file_path)
    chunks =[]
    # insert từng chunk vào chunk
    for page in pages:
        docs = split_document(page.get_text().replace('\n', ' ').lower())  # Return Langchain Documents list

        for doc in docs:
            chunk_data = {
                'content': doc.page_content,
                'source': str(pages.name), 
                'page': str(page.number)
            }
            chunks.append(chunk_data)
    return chunks

def excel_chunk(file_path):
 import pandas
 xls = pandas.ExcelFile(file_path)
 id = 0
 chunks = []
 for sheet in xls.sheet_names:
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
   chunk ={
			'content' : doc.page_content,
			'source': file_path,
			'page': str(xls.sheet_names.index(sheet)),
					
	}
   chunks.append(chunk)
 return chunks


def insert_pdf_to_db(client, file_path):
    chunks = [] 
    if file_path.split('.')[-1] == 'pdf':
        chunks = pdf_readable_chunk(file_path=file_path)
    if file_path.split('.')[-1] == 'xlsx':
       chunks = excel_chunk(file_path=file_path)
    #print (chunks)
    client = client
    import time
    counter = 0
    for chunk in chunks:
        try:
            client.batch.configure(batch_size=100)
            with client.batch as batch:
                batch.add_data_object(chunk,'Denso_Document')
            counter = counter+1
        except Exception as e:
            error_message = str(e)
            if "rate_limit_exceeded" in error_message:
                # Implement rate limit handling, e.g., wait for a certain period and retry
                print("Rate limit exceeded. Waiting and retrying...")
                time.sleep(5)  # Wait for 60 seconds
                client.batch.configure(batch_size=100)
                with client.batch as batch:
                    batch.add_data_object(chunk,'Denso_Document')
                counter = counter+1
            else:
                print(f"Error adding chunk: {chunk}. Error: {error_message}")

    print("Inserted ",counter," chunks to Denso_Document from ", file_path)
    


import os

dir = os.listdir("sample pdf")
for file in dir:
   insert_pdf_to_db(client=client, file_path="sample pdf/"+file)


doc1 = {
   'filepath': "sample pdf\LNCT800SoftwareApplicationManual.pdf",
   'machine_name': "DCM",
   'code': "VDCM0001.2.3.a",
   'line': ' 1.2.3.a',
   'description': "Thao tác Nạp khí nito vào bình cho Injection"

}






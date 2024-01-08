

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv,find_dotenv
import os
import fitz

####################STAGE 0 LOAD CONFIG ############################
load_dotenv(find_dotenv(),override=True)
OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")
#print(CHROMADB_HOST)


#####################STAGE 1 BUILDING VECTOR DB########################


###Part2: Chunking Document
#Spliter model
def split_document(docs,chunk_size = 1000, chunk_overlap = 0):
 text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    ) 
    # Splitting the documents into chunks
 chunks = text_splitter.create_documents([docs])
 return chunks


###Part3: Embedding Document
#Create embedding model 
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.chroma import Chroma
model = HuggingFaceEmbeddings(model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
#model = HuggingFaceEmbeddings(model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
database = Chroma(persist_directory="./chroma_db", embedding_function=model)

#INSERT document to db
def insert_pdf_to_db(file_path):
 #Load pdf into pages
 pages = fitz.open(file_path)
 chunks = []#create empty chunks
 #insert từng chunk vào chunk
 for page in pages:
  docs = split_document(page.get_text().replace('\n', ' ').lower())#Return Langchain Documents list
  
  for doc in docs:
   chunk = Document(page_content=doc.page_content, metadata={'source': pages.name,'page': page.number})
   chunks.append(chunk)
   
 #Tạo DB
 Chroma.from_documents(chunks, model, persist_directory="./chroma_db")
 #print(chunks)


def get_similar_chunks(query,db=database,k=5):
 chunks = db.similarity_search_with_score(query=query,k=k)
 return chunks
 
def get_response_from_query(query,chunks):
 chunks = chunks
 docs = " ".join([chunk[0].page_content for chunk in chunks if chunk[1]>33])

 from langchain.chat_models import ChatOpenAI
 from langchain.prompts import PromptTemplate
 from langchain.chains import LLMChain

 llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5,openai_api_key=OPEN_AI_API_KEY)

 prompt =PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        ###
         You are an Process assistants, you have knowledge of process, guidelines, machine document of the factory.

         Given the document bellow, Provide the instruction about the question below base on the provided provided document
         You use the tone that instructional,technical and concisely.
         Answer in Vietnamese
        ###
         Document: {docs}
         Question: {question}
        """,
    )
 chain = LLMChain(llm=llm, prompt=prompt)
 output = chain.run({'question': query, 'docs': docs})
 return output



#############TEST###############

#insert_pdf_to_db('sample pdf\LNCT800SoftwareApplicationManual-265-280.pdf')
#insert_pdf_to_db(sample_pdf_path2)
insert_pdf_to_db("sample pdf/tachtsst3.pdf")
#insert_pdf_to_db("sample pdf\LNCT800SoftwareApplicationManual (1).pdf")


#response = get_response_from_query(chunks=chunks,query=query)
#print(response)




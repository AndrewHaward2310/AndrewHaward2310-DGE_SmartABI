import weaviate
import weaviate.classes as wvc
import os
from pdf2image import convert_from_path
import fitz
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy
import easyocr
reader = easyocr.Reader(['en'])

def detect_easy_OCR(image):
    output = reader.readtext(image)
    text = [val[1] for val in output]
    return text

def pdf_not_read(file_path):
    images = convert_from_path(file_path)
    chunks =[]
    for page in range(len(images)):
        image = images[page]
        image = numpy.array(image)
        t = detect_easy_OCR(image)
        t = ' '.join(t)
        docs = split_document(t.lower())  # Return Langchain Documents list

        for doc in docs:
            chunk_data = {
                'content': doc.page_content,
                'source': file_path, 
                'page': str(page)
            }
            chunks.append(chunk_data)
    return chunks

def split_document(docs,chunk_size = 1000, chunk_overlap = 0):
 text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    ) 
 chunks = text_splitter.create_documents([docs])
 return chunks


def pdf_readable_chunk(file_path):
    pages = fitz.open(file_path)
    if pages[0].get_text():
       return pdf_not_read(file_path)
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
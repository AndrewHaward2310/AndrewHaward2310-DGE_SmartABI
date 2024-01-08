import weaviate
import pandas
import numpy
###########HAMM ĐÓNg GÓI
def history_show(filepath):
     name = filepath
     # name = 'History_hutbui.xlsx'
     if name == 'history\History_mayshotblash.xlsx':
         exc = pandas.ExcelFile(name)
         data = pandas.read_excel(exc, sheet_name=exc.sheet_names[0]).values
         data = data[2:]
         data = pandas.DataFrame(data)
     if name == 'history\History_hutbui.xlsx':
         exc = pandas.ExcelFile(name)
         data = pandas.read_excel(exc, sheet_name=exc.sheet_names[0]).values
         data = data[3:]
         data = pandas.DataFrame(data)
     nps = data[17].values[1:]
     true = []
     for day in nps:
         if type(day) == type('s'):
             d, month, year = numpy.array(day.split('-')).astype(int)
             true.append([year, month, d])
             continue
         date = [day.year, day.month, day.day]
         true.append(date)
     true = numpy.array(true).astype(str)
     true = ['-'.join(val) for val in true]
     true = ['Ngày Phát Sinh'] + true
     data[0] = true
     return data
     # exc = pandas.ExcelFile(name)
def retrive_history(query):
 client = weaviate.Client("http://localhost:8081")
 print("weaviatedb is ready: ",client.is_ready())
 response = (
        client.query
        .get("Denso_history",properties=["source"])
        .with_bm25(
          query=query,
          properties=["source","year","month","code","machine_name","line","description"]
        )
        .with_limit(1)
        .do()
    )
 #print(response)
 try:
  filepath = response["data"]["Get"]["Denso_history"][0]["source"]
  dataframe = history_show(filepath=filepath)
  return dataframe,filepath
  
 except:
  return "Tôi không tìm thấy lịch sử máy bạn đang cần.Xin hãy thử Câu hỏi khác cụ thể hơn",''
 

if __name__ == "__main__":
 query = "Cho tôi lịch sử máy hút bụi"
 response,meta = retrive_history(query=query)
 print(response)
 print(meta)
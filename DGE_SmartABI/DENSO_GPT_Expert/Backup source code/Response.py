from hybrid_retrive import retrive_Hybrid
from semantic_retrive import retrive_Semantic
from keyword_retrive import retrive_Keyword
import numpy
import pandas

query = "Lỗi int3170"

#print("Semantic Result: ")
list1 = retrive_Semantic(query=query)
#print(list1)

#print("Keyword Result:")
list2 = retrive_Keyword(query=query)
#print(list2)

#print("Hybrid Result:")
list3 = retrive_Hybrid(query=query)
#print(list3)

result = list2+list1+list3
counter = {}

def sort_paper(arr: list, k: int = 3):
    sources = [list(val.keys())[0] for val in arr]
    values = [list(val.values())[0] for val in arr]
    new_arr = list(zip(sources, values))
    a, b = numpy.unique(new_arr, axis=0, return_counts=True)
    df = numpy.array([a[:, 0], a[:, 1], b]).T
    df = pandas.DataFrame(df, columns=['tai lieu', 'trang', 'so lan xuat hien']).values
    df = list(df)
    df.sort(key=lambda x: x[2], reverse=True)
    return df[:k]

print(sort_paper(result))
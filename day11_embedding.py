#要做RAG(檢索增強生成)的話，先要做embedding，將文本轉成向量，然後存到向量資料庫中，之後再做檢索。
#所以呼叫專門做Embedding的API
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

#--------建立embedding向量-----------

result = client.models.embed_content(
    model = "gemini-embedding-001",
    contents = "染完頭多久可以洗頭?"
)

vector = result.embeddings[0].values
print(f"向量維度數量：{len(vector)}") #算總共有幾個數字，也就是維度
print(f"前 5 個數字：{vector[:5]}") #先只取前五個看一下就好

result2 = client.models.embed_content(
    model = "gemini-embedding-001",
    contents = "染髮後多久能洗頭?"
)

vector2 = result2.embeddings[0].values
print(f"向量維度數量：{len(vector2)}") #算總共有幾個數字，也就是維度
print(f"前 5 個數字：{vector2[:5]}") #先只取前五個看一下就好

#--------計算兩向量的餘弦相似度，看方向-----------
import numpy as np

def cosine_similarity(a, b):
    a = np.array(a) #將一班的list轉成numpy array做計算
    b = np.array(b)
    dot_product = np.dot(a,b)
    norm_a = np.linalg.norm(a) #向量的長度:平方，加總，開根號
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b) #最後計算餘弦相似度，也就是夾角

similarity = cosine_similarity(vector, vector2)
print(f"相似度：{similarity}")
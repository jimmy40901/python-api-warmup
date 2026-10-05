import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

faq_list = [
    "我們的剪髮服務包含洗髮、剪髮、吹整，約需 1 小時",
    "染髮後建議 48 小時內避免洗頭，讓染劑完全附著",
    "燙髮後一週內請勿使用電棒夾，以免影響捲度",
    "初次來店建議先預約，假日現場候位時間較長",
    "我們使用的染劑為日系進口品牌，低敏配方，但仍建議事先告知過敏史",
]

#-----------建立一個可以不斷embedding向量的迴圈-----------
faq_vectors = []
for faq in faq_list:
    result = client.models.embed_content(
        model = "gemini-embedding-001",
        contents = faq
    )
    faq_vectors.append(result.embeddings[0].values)

print(f"總共轉換了 {len(faq_vectors)} 段 FAQ")

#--------計算兩向量的餘弦相似度，看方向-----------
import numpy as np

def cosine_similarity(a, b):
    a = np.array(a) #將一班的list轉成numpy array做計算
    b = np.array(b)
    dot_product = np.dot(a,b)
    norm_a = np.linalg.norm(a) #向量的長度:平方，加總，開根號
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b) #最後計算餘弦相似度，也就是夾角

#-----------寫檢索函式:輸入新問題，自動找出最相關的那一段----------

def retrieve(question: str, faq_list: list[str], faq_vectors: list) -> str:
    question_result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )
    question_vector = question_result.embeddings[0].values

    best_score = -1 #因為餘弦相似度最小是-1，設-1確保他會更新
    best_faq = ""

    for i in range(len(faq_list)):
        score = cosine_similarity(question_vector, faq_vectors[i])
        if score > best_score:
            best_score = score
            best_faq = faq_list[i]

    return best_faq

answer = retrieve("染完頭多久可以洗頭？", faq_list, faq_vectors)
print(f"最相關的 FAQ：{answer}")

answer2 = retrieve("可以直接去店裡嗎？不先約時間", faq_list, faq_vectors)
print(f"最相關的 FAQ：{answer2}")
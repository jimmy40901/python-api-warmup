import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(api_key is not None)  #看API_KEY是否不為空的


from google import genai

#建立一個客戶端
client = genai.Client(api_key=api_key)

#generate_content()發出請求
response = client.models.generate_content(
    model = "gemini-3.5-flash-lite",
    contents = "請用一句話跟我打招呼"
)

print(response.text)
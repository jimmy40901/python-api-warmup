import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

from google import genai

#建立一個客戶端
client = genai.Client(api_key=api_key)

#generate_content()發出請求
response = client.models.generate_content(
    model = "gemini-3.5-flash-lite",
    contents = "你們禮拜天有營業嗎？",
    config = {"system_instruction": "你是一間咖啡廳的客服人員，名字叫小豆。回答要簡短、親切，只回答跟咖啡廳營業、菜單、訂位有關的問題，不要聊無關話題。"}
)

print(response.text)
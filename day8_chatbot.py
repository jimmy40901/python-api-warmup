import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# ---------- 真實工具函式 ----------

def check_opening_hours(day: str) -> str:
    """查詢指定星期幾的營業時間"""
    schedule = {
        "禮拜一": "公休",
        "禮拜二": "10:00-20:00",
        "禮拜三": "10:00-20:00",
        "禮拜四": "10:00-20:00",
        "禮拜五": "10:00-21:00",
        "禮拜六": "9:00-21:00",
        "禮拜天": "9:00-18:00",
    }
    return schedule.get(day, "查無此資料")

def check_service_price(service: str) -> str:
    """查詢指定服務項目的價格"""
    prices = {
        "剪髮": "500元",
        "洗髮": "300元",
        "染髮": "1500元",
        "燙髮": "2000元",
    }
    return prices.get(service, "查無此服務項目")

# ---------- 工具說明書(給 Gemini 看) ----------

tools = types.Tool(function_declarations=[
    {
        "name": "check_opening_hours",
        "description": "查詢指定星期幾的營業時間",
        "parameters": {
            "type": "object",
            "properties": {
                "day": {"type": "string", "description": "星期幾，例如：禮拜一、禮拜二"}
            },
            "required": ["day"]
        }
    },
    {
        "name": "check_service_price",
        "description": "查詢指定服務項目的價格",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "服務項目名稱，例如：剪髮、染髮"}
            },
            "required": ["service"]
        }
    }
])

# ---------- 把整套流程包成可重複呼叫的函式 ----------

def ask(question: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=question,
        config=types.GenerateContentConfig(tools=[tools])
    )
    part = response.candidates[0].content.parts[0]

    # 如果不需要呼叫工具，則直接回應
    if part.function_call is None:
        return response.text

    # 要呼叫工具：先判斷 Gemini 要的是哪一個，再真的去執行
    function_call = part.function_call
    if function_call.name == "check_opening_hours":
        tool_result = check_opening_hours(**function_call.args)
    elif function_call.name == "check_service_price":
        tool_result = check_service_price(**function_call.args)

    final_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            question,
            response.candidates[0].content,
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": tool_result}
                )]
            )
        ],
        config=types.GenerateContentConfig(tools=[tools])
    )
    return final_response.text

# ---------- 測試 ----------

print(ask("你們禮拜天有營業嗎？"))
print(ask("你好"))
print(ask("剪髮多少錢？"))
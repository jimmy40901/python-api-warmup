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

assert check_opening_hours("禮拜一") == "公休"
assert check_opening_hours("禮拜二") == "10:00-20:00"
assert check_opening_hours("禮拜八") == "查無此資料"
print("check_opening_hours() 測試通過")

from google import genai
from google.genai import types

#types套件是用來定義工具的資料格式
#functions_declarations是tools這個工具的工具清單，裡面放了所有工具的宣告
#定義一個可以查詢上面函式的工具說明tools
tools = types.Tool(function_declarations = [
    {
        "name": "check_opening_hours", #工具名稱
        "description": "查詢指定星期幾的營業時間", #工具的功能
        "parameters": { #要使用的時候需要提供的參數
            "type": "object", #這小包資料是物件型態
            "properties": { #其中有哪些欄位
                "day": {
                    "type": "string",
                    "description": "星期幾，例如：禮拜一、禮拜二"
                }
            },
            "required": ["day"] #一定要填，不能為空的欄位
        }
    }
])


#把上面的工具說明給AI，讓他自己判斷問題需不需要呼叫
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model = "gemini-3.5-flash-lite",
    contents = "你們禮拜天有營業嗎？",
    config = types.GenerateContentConfig(tools = [tools])
)

#輸出第一個候選的回覆(AI會生成很多種回覆，這裡只取第一個)，內容裡面的第一個parts
print(response.candidates[0].content.parts[0])

# 從 Gemini 的回應裡，取出它想呼叫的工具資訊，.function_call 會是一個 FunctionCall 物件，裡面有 name、args、type 等屬性
function_call = response.candidates[0].content.parts[0].function_call

# python來執行AI想呼叫的工具，這裡是呼叫check_opening_hours()函式
# function_call.args 是 {'day': '禮拜天'}，** 把它拆開變成 day='禮拜天'，餵給check_opening_hours函式
tool_result = check_opening_hours(**function_call.args)
print(f"工具執行結果：{tool_result}")

# 把工具執行結果，送回去給 Gemini，再讓它生成回覆
final_response = client.models.generate_content(
    #因為每次請求完記憶不會保留，所以要把前面所有的對話內容都放進來，讓AI知道之前發生了什麼事
    model="gemini-3.5-flash-lite",
    contents=[
        "你們禮拜天有營業嗎？",
        response.candidates[0].content,  # Gemini 剛剛那次「我想呼叫工具」的回應
        #工具的執行結果
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

print(final_response.text)
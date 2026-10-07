from typing import TypedDict  # LangGraph要求要使用的格式
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# ---------- State 定義 ----------

class BookingState(TypedDict):
    user_message: str
    service: str
    day: str
    is_available: bool

# ---------- Node：Node是流程裡「一個步驟」：一個 Node 函式，接收目前的State，回傳「要更新的部分」 ----------

# 讓LLM自己從使用者的語句裡判斷他要做甚麼項目
def extract_service(state: BookingState) -> dict:
    user_input = state['user_message']  # 在BookingState新增一個放使用者原話的欄位

    prompt = f"""從以下客人的話中，判斷他想預約的服務項目，只能是：剪髮、洗髮、染髮、燙髮 其中一種。
如果判斷不出來，回傳「不明確」。
只回傳服務項目這兩三個字，不要有其他文字。

客人的話：{user_input}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    service = response.text.strip()
    print(f"判斷出的服務項目：{service}")
    return {"service": service}

# 處理如果判斷不出要做的服務項目的情況
def ask_clarification(state: BookingState) -> dict:
    print("不好意思，請問您想預約剪髮、洗髮、染髮還是燙髮呢？")
    return {}

# 查詢空位
def check_availability(state: BookingState) -> dict:
    print(f"查詢 {state['day']} 是否有空位...")
    # 先寫死一個假邏輯：只有禮拜一公休，其他都有空位
    available = state['day'] != "禮拜一"
    return {"is_available": available}

def confirm_booking(state: BookingState) -> dict:
    print(f"已為您確認預約：{state['service']}，{state['day']}")
    return {}

def suggest_reschedule(state: BookingState) -> dict:
    print(f"很抱歉，{state['day']} 公休，建議您改約其他時間")
    return {}

# ---------- 條件邊：讓圖有分岔的能力 ----------

# 後續的判斷處理(extract_service 之後，判斷有沒有問出服務項目)
def route_after_extract(state: BookingState) -> str:
    if state['service'] == "不明確":
        return "ask_clarification"
    else:
        return "check_availability"

# 函式的輸入一樣是state，但回傳的跟Node不一樣，Node是字典，他是迴船要到的Node的名字
def route_after_check(state: BookingState) -> str:
    if state['is_available']:
        return "confirm_booking"
    else:
        return "suggest_reschedule"

# ---------- 建圖：讓圖知道他要收到的預期的格式 ----------

graph = StateGraph(BookingState)

graph.add_node("extract_service", extract_service)  # 前者是Node的名字，畫邊的時候用的
graph.add_node("ask_clarification", ask_clarification)
graph.add_node("check_availability", check_availability)
graph.add_node("confirm_booking", confirm_booking)
graph.add_node("suggest_reschedule", suggest_reschedule)

graph.set_entry_point("extract_service")  # 設定langgraph從哪裡開始跑

graph.add_conditional_edges(
    "extract_service",       # 從哪個Node開始
    route_after_extract,      # 用哪個判斷函式
    {
        "ask_clarification": "ask_clarification",  # 看函式回傳的字串可以對應到哪個Node，並執行該Node對應的動作
        "check_availability": "check_availability"
    }
)

graph.add_edge("ask_clarification", END)

graph.add_conditional_edges(
    "check_availability",
    route_after_check,
    {
        "confirm_booking": "confirm_booking",
        "suggest_reschedule": "suggest_reschedule"
    }
)

graph.add_edge("confirm_booking", END)
graph.add_edge("suggest_reschedule", END)

app = graph.compile()  # 將這個圖編譯成可以執行的東西

# ---------- 測試 ----------

print("=== 測試 1：明確的服務 + 公休日 ===")
result1 = app.invoke({"user_message": "我想染頭髮", "service": "", "day": "禮拜一", "is_available": False})
print(result1)

print("=== 測試 2：模糊的服務 ===")
result2 = app.invoke({"user_message": "我想處理一下頭髮", "service": "", "day": "禮拜二", "is_available": False})
print(result2)
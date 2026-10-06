from typing import TypedDict #LandGraph要求要使用的格式

class BookingState(TypedDict):
    service: str
    day: str
    is_available: bool

# Node是流程裡「一個步驟」：一個 Node 函式，接收目前的State，回傳「要更新的部分」。
# 1.確認服務項目
def ask_service(state: BookingState) -> dict:
    print(f"客人想預約的服務：{state['service']}")
    return {} #用空字典表示這個Node不會更新到State原本的內容

# 2.查詢空位
def check_availability(state: BookingState) -> dict:
    print(f"查詢 {state['day']} 是否有空位...")
    # 先寫死一個假邏輯：只有禮拜一公休，其他都有空位
    available = state['day'] != "禮拜一"
    return {"is_available": available}

from langgraph.graph import StateGraph, END

#讓圖知道他要收到的預期的格式
graph = StateGraph(BookingState)

graph.add_node("ask_service", ask_service)  #前者是Node的名字，畫邊的時候用的
graph.add_node("check_availability", check_availability)

graph.set_entry_point("ask_service") #設定landgraph從哪裡開始跑
graph.add_edge("ask_service", "check_availability")
graph.add_edge("check_availability", END)

app = graph.compile() #將這個圖編譯成可以執行的東西，之後讓LLM可以執行

initial_state = {"service": "剪髮", "day": "禮拜一", "is_available": False}
result = app.invoke(initial_state)
print(result)
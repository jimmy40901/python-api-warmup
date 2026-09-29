from dataclasses import dataclass

@dataclass
class Customer:
    name: str
    is_new: bool
    visit_count: int = 0   # 等號後面是預設值，建立時沒給就用 0
    is_birthday_month: bool = False

new_customer = Customer(name="小明", is_new=True)
print(new_customer.name)          # 小明
print(new_customer.visit_count)   # 0（用了預設值）

old_customer = Customer(name="小華", is_new=False, visit_count=6)
print(old_customer.name)          # 小華
print(old_customer.visit_count)   # 6（給了 visit_count 的值）

def calc_discount(customer: Customer) -> float:
    if customer.is_new:
        return 0.9  # 新客戶折扣 10%
    elif customer.visit_count >= 5:
        return 0.8  # 老客戶且訪問次數大於等於 5，折扣 20%
    elif customer.is_birthday_month:
        return 0.95
    else:
        return 1.0  # 其他情況 

assert calc_discount(new_customer) == 0.9
assert calc_discount(old_customer) == 0.8
assert calc_discount(Customer(name = "小張", is_new = False, visit_count= 2, is_birthday_month= True)) == 0.95
assert calc_discount(Customer(name="小美", is_new=False, visit_count=2)) == 1.0
print("所有測試都通過！")

print(new_customer)
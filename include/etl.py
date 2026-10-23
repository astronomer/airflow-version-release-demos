def extract():
    return {"orders": [{"id": 1, "amount": 20}, {"id": 2, "amount": 35}, {"id": 3, "amount": 45}]}


def transform(data):
    return sum(order["amount"] for order in data["orders"])


def load(total):
    print(f"Total order amount: {total}")

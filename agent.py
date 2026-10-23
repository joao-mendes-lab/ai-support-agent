import os
import time
from datetime import date, timedelta
from google import genai
from google.genai import types
from google.genai import errors

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
MAX_STEPS = 6

def days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()

ORDERS = {
    "A100": {"customer": "Marta", "product": "Headphones X1", "price": 59.90, "date": days_ago(14), "status": "delivered"},
    "A101": {"customer": "John", "product": "Laptop Pro", "price": 1199.00, "date": days_ago(5), "status": "delivered"},
    "A102": {"customer": "Rita", "product": "Wireless Mouse", "price": 19.90, "date": days_ago(2), "status": "in transit"},
    "A103": {"customer": "Rui", "product": "Keyboard K2", "price": 45.00, "date": days_ago(60), "status": "delivered"},
}
TICKETS = []

def get_order(order_id: str) -> dict:
    o = ORDERS.get(order_id.upper())
    return o if o else {"error": f"Order {order_id} not found"}

def request_refund(order_id: str, reason: str) -> dict:
    o = ORDERS.get(order_id.upper())
    if not o:
        return {"approved": False, "reason": "Order not found"}
    if o["status"] != "delivered":
        return {"approved": False, "reason": "Only delivered orders can be returned"}
    days = (date.today() - date.fromisoformat(o["date"])).days
    if days > 30:
        return {"approved": False, "reason": f"{days} days have passed (max 30)"}
    if o["price"] > 100:
        return {"approved": False, "reason": "Amount over €100: requires human decision"}
    return {"approved": True, "amount_refunded": o["price"], "reason": reason}

def open_human_ticket(summary: str) -> dict:
    TICKETS.append(summary)
    return {"ticket_id": f"T{len(TICKETS):03d}", "status": "open"}

FUNCTIONS = {f.__name__: f for f in (get_order, request_refund, open_human_ticket)}
TOOLS = [get_order, request_refund, open_human_ticket]

def send(chat, content):
    for attempt in range(4):
        try:
            return chat.send_message(content)
        except errors.ClientError as e:
            if e.code == 429:
                wait = 5 * 2 ** attempt
                print(f"  (free tier rate limit hit, waiting {wait}s...)")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Free tier quota exhausted. The daily quota resets at the end of the day.")

def run_agent(chat, message):
    response = send(chat, message)
    for step in range(1, MAX_STEPS + 1):
        calls = [p.function_call for p in response.candidates[0].content.parts if p.function_call]
        if not calls:
            return response.text

        parts = []
        for fc in calls:
            args = dict(fc.args)
            print(f"  [step {step}] ACT: {fc.name}({args})")
            try:
                result = FUNCTIONS[fc.name](**args)
            except Exception as e:
                result = {"error": str(e)}
            print(f"  [step {step}] OBSERVE: {result}")
            parts.append(types.Part.from_function_response(name=fc.name, response={"result": result}))
        response = send(chat, parts)

    ticket = open_human_ticket(f"Agent couldn't resolve this. Last request: {message}")
    return f"I couldn't solve this on my own. I opened ticket {ticket['ticket_id']} for a colleague."

SYSTEM_PROMPT = """You are LojaTech's customer support assistant.
Rules:
- Always ask for the order number before taking any action.
- Look up the order before requesting a refund.
- Never make up order data.
- If the refund isn't approved, explain why. If the case needs a human
  (or the customer asks for one), open a ticket with a clear summary.
- Reply briefly and politely."""

CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=TOOLS,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

def main():
    chat = client.chats.create(model=MODEL, config=CONFIG)
    print("LojaTech Support (type 'exit' to quit)")
    while True:
        text = input("Customer: ")
        if text.strip().lower() == "exit":
            break
        try:
            print("Assistant:", run_agent(chat, text), "\n")
        except RuntimeError as error:
            print("Error:", error)
            break

if __name__ == "__main__":
    main()
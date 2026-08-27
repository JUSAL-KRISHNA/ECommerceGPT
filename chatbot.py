# CLI version of the same chatbot logic.
from modules.chatbot import EcommerceChatbot

bot = EcommerceChatbot()
print("ECommerceGPT - type 'exit' to quit")
while True:
    q = input("\nYou: ").strip()
    if q.lower() == "exit":
        break
    result = bot.answer(q)
    print("Detected Intent:", result["intent"])
    print("Assistant:", result.get("answer", ""))

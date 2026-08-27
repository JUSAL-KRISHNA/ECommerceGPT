from flask import Flask, render_template, request, jsonify
from modules.chatbot import EcommerceChatbot

app = Flask(__name__)
bot = EcommerceChatbot()

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    query = (data.get("message") or "").strip()
    if not query:
        return jsonify({"error": "Please enter a message."}), 400
    return jsonify(bot.answer(query))

@app.get("/api/products")
def products():
    return jsonify(bot.products.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)

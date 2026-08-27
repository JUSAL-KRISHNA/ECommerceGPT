# For this lightweight lab version, TF-IDF matrices are generated when the chatbot starts.
# This script verifies the datasets and vectorization pipeline.

from modules.chatbot import EcommerceChatbot

bot = EcommerceChatbot()
print("FAQ embeddings/vector matrix:", bot.faq_matrix.shape)
print("Product TF-IDF matrix:", bot.product_matrix.shape)
print("Embeddings/vectorization initialized successfully.")

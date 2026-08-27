import json
import re
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

class EcommerceChatbot:
    def __init__(self):
        self.products = pd.read_csv("data/products.csv")
        self.faq = pd.read_csv("data/faq.csv")
        self.reviews = pd.read_csv("data/reviews.csv")

        self.faq_vectorizer = TfidfVectorizer(stop_words="english")
        self.faq_matrix = self.faq_vectorizer.fit_transform(self.faq["question"].fillna(""))

        self.product_vectorizer = TfidfVectorizer(stop_words="english")
        product_text = (
            self.products["product_name"].fillna("") + " " +
            self.products["brand"].fillna("") + " " +
            self.products["category"].fillna("") + " " +
            self.products["description"].fillna("")
        )
        self.product_matrix = self.product_vectorizer.fit_transform(product_text)

    def intent(self, query):
        q = query.lower()
        if any(x in q for x in ["track", "parcel", "delivery", "cancel", "return", "refund", "order"]):
            return "FAQ"
        if any(x in q for x in ["recommend", "suggest", "best", "gaming", "under", "laptop"]):
            return "RECOMMENDATION"
        if any(x in q for x in ["review", "reviews", "customers", "opinion", "feedback", "sentiment"]):
            return "REVIEW"
        return "PRODUCT"

    def ollama(self, prompt):
        try:
            r = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": prompt, "stream": False},
                timeout=30
            )
            r.raise_for_status()
            return r.json().get("response", "").strip()
        except Exception:
            return None

    def faq_answer(self, query):
        qv = self.faq_vectorizer.transform([query])
        scores = cosine_similarity(qv, self.faq_matrix)[0]
        i = scores.argmax()
        score = float(scores[i])
        row = self.faq.iloc[i]

        if score < 0.18:
            return {"matched": False, "score": score}

        prompt = f"""You are an e-commerce support assistant.
Answer using ONLY this FAQ information.

Question: {row['question']}
Answer: {row['answer']}

User question: {query}
Give a concise, professional answer."""
        response = self.ollama(prompt) or row["answer"]
        return {
            "matched": True, "score": round(score, 2),
            "answer": response,
            "source": row["question"]
        }

    def recommendation(self, query):
        qv = self.product_vectorizer.transform([query])
        scores = cosine_similarity(qv, self.product_matrix)[0]
        top = scores.argsort()[::-1][:3]
        rows = self.products.iloc[top].copy()
        rows["similarity"] = scores[top]
        context = "\n".join(
            f"{r.product_name} | {r.brand} | ₹{int(r.price):,} | {r.description}"
            for _, r in rows.iterrows()
        )
        prompt = f"""You are an e-commerce product advisor.
Recommend the best product from ONLY these retrieved products.

{context}

Customer request: {query}
Give the product name, brand, price and a short reason."""
        response = self.ollama(prompt)
        if not response:
            best = rows.iloc[0]
            response = (
                f"I recommend {best.product_name} from {best.brand}. "
                f"It costs ₹{int(best.price):,} and is the closest match to your request."
            )
        return {
            "answer": response,
            "products": rows[["product_name", "brand", "category", "price", "description", "similarity"]].round(2).to_dict("records")
        }

    def product_qa(self, query):
        qv = self.product_vectorizer.transform([query])
        scores = cosine_similarity(qv, self.product_matrix)[0]
        i = scores.argmax()
        row = self.products.iloc[i]
        context = (
            f"Product: {row.product_name}\nBrand: {row.brand}\n"
            f"Category: {row.category}\nPrice: ₹{int(row.price):,}\n"
            f"Description: {row.description}"
        )
        prompt = f"""Answer the customer using ONLY the product context below.
If the answer is not in the context, say that the available product data does not provide it.

{context}

Customer question: {query}"""
        response = self.ollama(prompt)
        if not response:
            response = (
                f"{row.product_name} is manufactured by {row.brand} and is priced at "
                f"₹{int(row.price):,}. {row.description}"
            )
        return {"answer": response, "product": row.to_dict(), "score": round(float(scores[i]), 2)}

    def review(self, query):
        # Simple lexicon sentiment keeps the project runnable without a large model.
        positive = {"excellent", "good", "great", "amazing", "worth", "quality", "fast", "reliable", "satisfied"}
        negative = {"poor", "bad", "issue", "heating", "slow", "worst", "average", "disappointing"}
        rows = self.reviews.copy()
        def classify(text):
            words = set(re.findall(r"\b[a-z]+\b", text.lower()))
            p, n = len(words & positive), len(words & negative)
            return "Positive" if p > n else ("Negative" if n > p else "Neutral")
        rows["sentiment"] = rows["review"].map(classify)
        product_terms = query.lower().replace("reviews", "").replace("review", "").strip()
        if product_terms:
            mask = rows["product"].str.lower().str.contains(product_terms, regex=False, na=False)
            filtered = rows[mask]
            if len(filtered):
                rows = filtered
        counts = rows["sentiment"].value_counts().to_dict()
        details = rows[["product", "review", "sentiment"]].to_dict("records")
        prompt = f"""Summarize these e-commerce reviews.
Reviews: {json.dumps(details)}
Give overall opinion, strengths, weaknesses and buying suggestion."""
        response = self.ollama(prompt)
        if not response:
            response = (
                f"Overall, customers are mostly {max(counts, key=counts.get).lower()}. "
                f"Positive: {counts.get('Positive',0)}, Neutral: {counts.get('Neutral',0)}, "
                f"Negative: {counts.get('Negative',0)}."
            )
        return {"answer": response, "counts": counts, "reviews": details}

    def answer(self, query):
        intent = self.intent(query)
        if intent == "FAQ":
            result = self.faq_answer(query)
            if not result.get("matched"):
                intent = "PRODUCT"
            else:
                return {"intent": intent, **result}
        if intent == "RECOMMENDATION":
            return {"intent": intent, **self.recommendation(query)}
        if intent == "REVIEW":
            return {"intent": intent, **self.review(query)}
        return {"intent": "PRODUCT", **self.product_qa(query)}

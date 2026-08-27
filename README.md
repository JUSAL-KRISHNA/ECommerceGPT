# ECommerceGPT — AI-Powered E-Commerce Chatbot

A modular Retrieval-Augmented Generation (RAG) e-commerce chatbot built for **24CS2506 – Building Applications using GPT-4, Experiment 1**.

The project implements:
- FAQ semantic search
- Product recommendation using TF-IDF + cosine similarity
- Product-specific question answering using retrieved context
- Customer review sentiment analysis and summary
- Intent-based routing
- Ollama + Qwen local LLM integration
- A responsive web interface

## Project Structure

```text
ECommerceGPT/
├── app.py
├── chatbot.py
├── create_embeddings.py
├── requirements.txt
├── README.md
├── modules/
│   ├── chatbot.py
│   ├── intent_module.py
│   ├── faq_module.py
│   ├── recommendation_module.py
│   ├── product_module.py
│   └── review_module.py
├── data/
│   ├── products.csv
│   ├── faq.csv
│   └── reviews.csv
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
├── models/
└── screenshots/
```

## 1. Install Python dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

For macOS/Linux:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Install Ollama

Install Ollama from the official Ollama website, then download Qwen:

```bash
ollama pull qwen2.5:3b
```

Start Ollama if it is not already running:

```bash
ollama serve
```

The application calls:

```text
http://localhost:11434/api/generate
```

If Ollama is unavailable, the application still runs using deterministic fallback responses.

## 3. Run the web application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 4. Test queries

### FAQ
- Where is my parcel?
- How do I cancel my order?
- How can I return my order?

### Recommendation
- Recommend a gaming laptop
- Suggest a laptop for gaming
- Recommend a phone

### Product
- Tell me about Lenovo Laptop 3
- What is the price of Samsung Galaxy?
- What brand is Pixel Pro?

### Reviews
- What do customers think about Lenovo Laptop 3?
- Show reviews for Samsung Galaxy

## Mapping to the Lab Questions

| Lab question | Implementation |
|---|---|
| Q1 | `data/*.csv` + Pandas |
| Q2 | README + module architecture |
| Q3 | FAQ TF-IDF vector matrix |
| Q4 | Cosine similarity |
| Q5 | FAQ threshold + Ollama response |
| Q6 | Product TF-IDF |
| Q7 | Top-3 retrieval + Ollama recommendation |
| Q8 | Most relevant product retrieval |
| Q9 | Constrained product-context prompt |
| Q10 | Review sentiment classifier |
| Q11 | Review counts + Ollama summary |
| Q12 | Intent routing |
| Q13 | Continuous chatbot through the web UI |

## GitHub submission

Create a GitHub repository named:

```text
ECommerceGPT
```

Then:

```bash
git init
git add .
git commit -m "Build AI powered e-commerce chatbot"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Before submitting, add screenshots of:
1. Home page
2. FAQ response
3. Product recommendation
4. Product Q&A
5. Review analysis
6. GitHub repository structure

## Dataset note

The included CSV files are small demonstration datasets so the project runs immediately. Replace them with the datasets supplied by your faculty while keeping the required column names, or update the column references in `modules/chatbot.py`.

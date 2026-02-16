# pipeline.py
from openai import OpenAI
from ddgs import DDGS
import weaviate
import json
from prompting import search_system_prompt, reliability_prompt, urgency_prompt, question, current_date

# Local LLM
chat_client = OpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required"
)

# Local embeddings
embed_client = OpenAI(
    base_url="http://127.0.0.1:8082/v1",
    api_key="sk-no-key-required"
)

# Weaviate
weaviate_client = weaviate.connect_to_local()

def search(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    return "\n".join([f"{r['title']}: {r['body']}" for r in results])



def score_reliability(product, prompt):
    """Get reliability score from JSON output"""
    search_results = search(f"{product} supplier reliability Australia")
    
    response = chat_client.chat.completions.create(
        model="local-model",
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Product: {product}\n\nSearch Results:\n{search_results}\n\nAnalyze source reliability. Return JSON."}
        ]
    )
    
    data = json.loads(response.choices[0].message.content)
    url=data["rankings"][0]["url"]           # Output: daly.com
    r=data["rankings"][0]["score"]         # Output: 3
    verification=data["rankings"][0]["verification_method"]
    print(data, r, url, verification)
    print("DONE RELIABILITY")

    return r, url, verification


def score_urgency(product, prompt):
    """Get urgency score from JSON output"""
    search_results = search(f"{product} medical shortage urgent 2026")
    
    response = chat_client.chat.completions.create(
        model="local-model",
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Product: {product}\n\nSearch Results:\n{search_results}\n\nAnalyze urgency. Return JSON."}
        ]
    )
    
    data = json.loads(response.choices[0].message.content)
    u = data.get("urgency_score")
    top_urgency = data.get("verification_method")
    print(data, u, top_urgency)
    print("DONE URGENCY")
    return u, top_urgency

def get_embedding(text):
    response = embed_client.embeddings.create(
        model="local-embedding-model",
        input=text
    )
    return response.data[0].embedding

def main():
    products = ["Product B", "Product C"]
    
    if weaviate_client.collections.exists("Question"):
        collection = weaviate_client.collections.get("Question")
    else:
        collection = weaviate_client.collections.create(
            name="Question",
            vectorizer_config=None
        )
    
    for product in products:
        print(f"\n📦 {product}")
        
        r, url, verification = score_reliability(product, reliability_prompt)
        u, top_urgency = score_urgency(product, urgency_prompt)
        
        print(float(r), float(u))
        final = float(r) * float(u)
        
        text = f"{product} reliability:{r} urgency:{u} final:{final}"
        vector = get_embedding(text)
        
        collection.data.insert(
            properties={
                "product": product,
                "score_reliability": r,
                "score_urgency": u,
                "score_final": final,
                "link": url,
                "verification_method": verification,
                "top_urgency_indicators": top_urgency
            },
            vector=vector
        )
        
        print(f"✅ {product}: {final:.3f} ({r:.2f} × {u:.2f})")
    
    weaviate_client.close()

if __name__ == "__main__":
    main()
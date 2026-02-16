# pipeline.py
from openai import OpenAI
from ddgs import DDGS
import weaviate
import json
from prompting import search_system_prompt, reliability_prompt, urgency_prompt, question, current_date
import time
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



def score_reliability(product, prompt, max_attempts=10, attempt=1):
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
    print("DEBUG - Full data:", data)
    print("DEBUG - Rankings:", data.get("rankings", "KEY MISSING"))
    print("DEBUG - Rankings length:", len(data.get("rankings", [])))
    print("DONE RELIABILITY")
    rankings = data.get("rankings", [])
    if not rankings:
        if attempt >= max_attempts:
            print(f"ERROR: No rankings found after {max_attempts} attempts. Defaulting to 0 reliability.")
            return 0, None, "No rankings found"
        return score_reliability(product, prompt, max_attempts, attempt + 1)  # Retry if no rankings found

    return r, url, verification

def score_reliability(product, prompt, max_attempts=10):
    """
    Score product reliability with retry logic for empty rankings.
    
    Args:
        product: The product to evaluate
        reliability_prompt: The prompt to send to the LLM
        max_attempts: Maximum number of retry attempts (default: 10)
    
    Returns:
        tuple: (score, url, verification) or (None, None, None) on failure
    """
    search_results = search(f"{product} supplier reliability Australia")
    
    response = chat_client.chat.completions.create(
        model="local-model",
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Product: {product}\n\nSearch Results:\n{search_results}\n\nAnalyze source reliability. Return JSON."}
        ]
    )

    for attempt in range(1, max_attempts + 1):
        try:
            # Parse the JSON response (raw JSON, no markdown)
            data = json.loads(response.choices[0].message.content)
            
            # Debug output (optional - remove in production)
            print(f"Attempt {attempt}: Rankings = {data.get('rankings')}")
            
            # Validate data structure
            if not isinstance(data, dict):
                print(f"Attempt {attempt}: Invalid response type (expected dict)")
                if attempt < max_attempts:
                    time.sleep(0.5)
                continue
            
            # Safely access rankings
            rankings = data.get("rankings", [])
            
            # Check if rankings exists and has data
            if not rankings or not isinstance(rankings, list) or len(rankings) == 0:
                print(f"Attempt {attempt}: No rankings found ({attempt}/{max_attempts})")
                if attempt < max_attempts:
                    time.sleep(0.5)
                continue
            
            # Success - extract data safely
            first_ranking = rankings[0]
            if not isinstance(first_ranking, dict):
                print(f"Attempt {attempt}: First ranking is not a dict")
                if attempt < max_attempts:
                    time.sleep(0.5)
                continue
            
            url = first_ranking.get("url", "")
            score = first_ranking.get("score", 0)
            verification = first_ranking.get("verification", "")
            
            print(f"Attempt {attempt}: Success! URL: {url}")
            return score, url, verification
            
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt}: JSON parsing error - {str(e)}")
            print(f"Raw response: {response}")
            if attempt < max_attempts:
                time.sleep(0.5)
                continue
            else:
                return None, None, None
                
        except Exception as e:
            print(f"Attempt {attempt}: Error occurred - {str(e)}")
            if attempt < max_attempts:
                time.sleep(0.5)
                continue
            else:
                return None, None, None
    
    # All attempts exhausted
    print(f"WARNING: Max attempts ({max_attempts}) reached. Returning None values.")
    return None, None, None

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
    try:
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

            Reliability = f"{search_system_prompt} {reliability_prompt}"
            Urgency = f"{search_system_prompt} {urgency_prompt}"

            r, url, verification = score_reliability(product, Reliability)
            u, top_urgency = score_urgency(product, Urgency)
            
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
    except Exception as e:
        if e: 
            print("An error occurred:", str(e))
            weaviate_client.close()

if __name__ == "__main__":
    main()
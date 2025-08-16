import requests
import json

# ⚙️ Settings
OPENROUTER_API_KEY = "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"  # ← Put your API key here
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 📦 Strategy definitions
STRATEGIES = {
    "concise": {
        "prompt": "Respond concisely and accurately, without unnecessary details.",
        "max_tokens": 100
    },
    "detailed": {
        "prompt": "Respond in detail, explaining steps and reasoning.",
        "max_tokens": 300
    },
    "interactive": {
        "prompt": "Ask one question to better understand the context. Be brief and clear.",
        "max_tokens": 60
    }
}

# 🧠 Strategy selection based on context
def choose_strategy(user_input, context_memory):
    full_text = user_input + " " + " ".join(context_memory[-2:]) if context_memory else user_input
    words = full_text.lower().split()

    if any(word in words for word in ["recommendation", "choose", "what's best", "suits me"]):
        return "interactive" if len(context_memory) < 2 else "detailed"
    elif len(words) < 12:
        return "interactive"
    else:
        return "detailed"

# 🤖 Send request to OpenRouter
def query_openrouter(prompt, system_prompt, max_tokens=200, model="mistralai/mistral-7b-instruct"):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,  # You can change the model as needed
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "presence_penalty": 0,
        "frequency_penalty": 0
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            return f"❌ OpenRouter error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ Connection error: {str(e)}"

# 🔄 Main interaction loop
def handle_client_request():
    print("🤖 Hello! How can I assist you? (Type 'exit' to quit)")
    context_memory = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "done", "stop", "quit"]:
            print("👋 Goodbye!")
            break

        # Select strategy
        strategy = choose_strategy(user_input, context_memory)
        config = STRATEGIES[strategy]

        # Build prompt with context
        full_prompt = user_input
        if context_memory:
            full_prompt += "\nPrevious info: " + " | ".join(context_memory)

        # Query the model
        print("...")
        response = query_openrouter(
            prompt=full_prompt,
            system_prompt=config["prompt"],
            max_tokens=config["max_tokens"],
            model="mistralai/mistral-7b-instruct"  # Fast model with good Arabic support
        )

        print(f"Model response: {response}")

        # Save context based on strategy
        if strategy == "interactive" and ("question" in response or "?" in response):
            context_memory.append(f"Question: {user_input}")
            context_memory.append(f"Partial reply: {response}")
        else:
            context_memory.append(f"Request: {user_input}")
            context_memory.append(f"Answer: {response}")
            # Ask if user wants to continue
            continue_ask = input("\nDo you need further clarification? (yes/no): ")
            if continue_ask.lower() in ["no", "stop", "done"]:
                break

# 🚀 Run the program
if __name__ == "__main__":
    handle_client_request()

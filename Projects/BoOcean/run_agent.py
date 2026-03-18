import requests
import json
from typing import Dict, Any, Optional

class BlackboxAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.blackbox.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, 
                       messages: list[Dict[str, str]], 
                       model: str = "blackbox-mixtral-8x7b",
                       temperature: float = 0.7,
                       max_tokens: int = 2048,
                       stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Send a chat completion request to Blackbox AI.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Model to use (default: blackbox-mixtral-8x7b)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            Response JSON or None if error
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if response.text:
                print(f"Error response: {response.text}")
            return None

def main():
    # Replace with your actual Blackbox AI API key
    API_KEY = "sk-WGEKhxE57qTp-ZLWgoP_Gw" 
    
    # Initialize client
    client = BlackboxAI(API_KEY)
    
    # Example conversation
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Write a Python function to calculate fibonacci numbers."}
    ]
    
    print("Sending request to Blackbox AI...")
    response = client.chat_completion(messages)
    
    if response:
        # Print the generated response
        content = response['choices'][0]['message']['content']
        print("\nResponse:")
        print("-" * 50)
        print(content)
    else:
        print("Failed to get response from Blackbox AI")

# Interactive chat example
def interactive_chat():
    API_KEY = "sk-WGEKhxE57qTp-ZLWgoP_Gw"  # Replace with your API key
    client = BlackboxAI(API_KEY)
    
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    
    print("Blackbox AI Chat (type 'quit' to exit)")
    print("-" * 40)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat_completion(messages)
        
        if response and response['choices']:
            ai_response = response['choices'][0]['message']['content']
            print(f"\nBlackbox AI: {ai_response}")
            messages.append({"role": "assistant", "content": ai_response})
        else:
            print("Sorry, I couldn't get a response.")

if __name__ == "__main__":
    # Run the main example
    main()
    
    # Uncomment the line below to run interactive chat instead
    # interactive_chat()
"""
Chat service - AI chat with MiniMax/Ollama/Cloudflare
"""

import os
import requests


class ChatProvider:
    """Base chat provider."""
    
    def chat(self, message, system_prompt=None):
        """Send chat message and return response."""
        raise NotImplementedError


class MiniMaxProvider(ChatProvider):
    """MiniMax chat API provider."""
    
    def __init__(self, api_key=None, model='MiniMax-M2.1'):
        self.api_key = api_key or os.environ.get('MINIMAX_API_KEY', '')
        self.model = model or os.environ.get('MINIMAX_MODEL', 'MiniMax-M2.1')
        self.api_url = 'https://api.minimax.chat/v1/text/chatcompletion_v2'
    
    def chat(self, message, system_prompt=None):
        if not self.api_key:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': message})
            
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 500
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            print(f'MiniMax error: {e}')
        return None


class OllamaProvider(ChatProvider):
    """Ollama local AI provider."""
    
    def __init__(self, base_url=None, model='llama3.2'):
        self.base_url = base_url or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or os.environ.get('OLLAMA_MODEL', 'llama3.2')
        self.api_url = f'{self.base_url}/api/chat'
    
    def chat(self, message, system_prompt=None):
        try:
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': message})
            
            payload = {
                'model': self.model,
                'messages': messages,
                'stream': False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '')
        except Exception as e:
            print(f'Ollama error: {e}')
        return None


class CloudflareProvider(ChatProvider):
    """Cloudflare Workers AI provider."""
    
    def __init__(self, token=None, account_id=None, model='@cf/meta/llama-3.1-8b-instruct'):
        self.token = token or os.environ.get('CF_API_TOKEN', '')
        self.account_id = account_id or os.environ.get('CF_ACCOUNT_ID', '')
        self.model = model
        self.api_url = f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}'
    
    def chat(self, message, system_prompt=None):
        if not self.token or not self.account_id:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': message})
            
            payload = {
                'messages': messages,
                'max_tokens': 500
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result.get('result', {}).get('response', '')
        except Exception as e:
            print(f'Cloudflare error: {e}')
        return None


def get_chat_provider():
    """
    Get the best available chat provider.
    Priority: MiniMax -> Ollama -> Cloudflare
    """
    # Try MiniMax first
    minimax = MiniMaxProvider()
    if minimax.api_key:
        return minimax, 'minimax'
    
    # Try Ollama
    ollama = OllamaProvider()
    try:
        response = requests.get(f'{ollama.base_url}/api/tags', timeout=2)
        if response.status_code == 200:
            return ollama, 'ollama'
    except:
        pass
    
    # Try Cloudflare
    cloudflare = CloudflareProvider()
    if cloudflare.token and cloudflare.account_id:
        return cloudflare, 'cloudflare'
    
    return None, 'none'


def chat_with_ai(message, system_prompt=None):
    """Send chat message and get AI response."""
    provider, name = get_chat_provider()
    if provider:
        response = provider.chat(message, system_prompt)
        if response:
            return response, name
    return None, 'none'

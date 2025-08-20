"""
Multi-model support for AI agents (Anthropic, OpenAI, Google)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import anthropic
import openai
from openai import OpenAI
import google.generativeai as genai
from abc import ABC, abstractmethod
import streamlit as st


class BaseModelClient(ABC):
    """Base class for model clients"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from the model"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass


class AnthropicClient(BaseModelClient):
    """Anthropic Claude client"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Claude"""
        try:
            # Using the latest Anthropic API (v0.64.0+)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 2048),
                temperature=kwargs.get('temperature', 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Extract text from the response
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            else:
                return str(response.content[0])
        except Exception as e:
            st.error(f"Anthropic API 오류: {str(e)}")
            # Log the detailed error for debugging
            import traceback
            print(f"Anthropic Error Details: {traceback.format_exc()}")
            return ""
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "Anthropic",
            "model": self.model,
            "features": ["긴 컨텍스트", "코드 생성", "분석", "창의적 작문"]
        }


class OpenAIClient(BaseModelClient):
    """OpenAI GPT client"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using GPT"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', 2048),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API 오류: {str(e)}")
            return ""
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "OpenAI",
            "model": self.model,
            "features": ["범용 AI", "코드 생성", "추론", "다국어 지원"]
        }


class GeminiClient(BaseModelClient):
    """Google Gemini client"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Gemini"""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get('temperature', 0.7),
                max_output_tokens=kwargs.get('max_tokens', 2048),
            )
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            st.error(f"Gemini API 오류: {str(e)}")
            return ""
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "Google",
            "model": self.model_name,
            "features": ["빠른 응답", "멀티모달", "코드 생성", "효율적"]
        }


class ModelFactory:
    """Factory class for creating model clients"""
    
    MODELS = {
        "Anthropic": {
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (최신/최고 성능)",
            "claude-3-5-haiku-20241022": "Claude 3.5 Haiku (빠른 응답)",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet (균형)",
            "claude-3-haiku-20240307": "Claude 3 Haiku (경제적)"
        },
        "OpenAI": {
            "gpt-4-turbo": "GPT-4 Turbo (최신)",
            "gpt-4": "GPT-4 (표준)",
            "gpt-4o": "GPT-4o (최적화)",
            "gpt-4o-mini": "GPT-4o Mini (경제적)",
            "gpt-3.5-turbo": "GPT-3.5 Turbo (빠른 응답)"
        },
        "Google": {
            "gemini-1.5-pro": "Gemini 1.5 Pro (최고 성능)",
            "gemini-1.5-flash": "Gemini 1.5 Flash (빠른 응답)",
            "gemini-pro": "Gemini Pro (표준)"
        }
    }
    
    @classmethod
    def create_client(cls, provider: str, api_key: str, model: str) -> BaseModelClient:
        """Create a model client based on provider"""
        if provider == "Anthropic":
            return AnthropicClient(api_key, model)
        elif provider == "OpenAI":
            return OpenAIClient(api_key, model)
        elif provider == "Google":
            return GeminiClient(api_key, model)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @classmethod
    def get_available_models(cls) -> Dict[str, Dict[str, str]]:
        """Get all available models"""
        return cls.MODELS


@dataclass
class MultiModelAgentResponse:
    """Response from multi-model agent"""
    content: str
    model_used: str
    provider: str
    quality_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "model_used": self.model_used,
            "provider": self.provider,
            "quality_score": self.quality_score,
            "metadata": self.metadata or {}
        }


class MultiModelAgent:
    """Agent that can use multiple AI models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize model clients based on configuration"""
        # Anthropic
        if self.config.get('anthropic_api_key'):
            self.clients['Anthropic'] = AnthropicClient(
                self.config['anthropic_api_key'],
                self.config.get('anthropic_model', 'claude-3-5-sonnet-20241022')
            )
        
        # OpenAI
        if self.config.get('openai_api_key'):
            self.clients['OpenAI'] = OpenAIClient(
                self.config['openai_api_key'],
                self.config.get('openai_model', 'gpt-4-turbo')
            )
        
        # Google
        if self.config.get('google_api_key'):
            self.clients['Google'] = GeminiClient(
                self.config['google_api_key'],
                self.config.get('google_model', 'gemini-1.5-flash')
            )
    
    def generate(self, prompt: str, provider: str = None, **kwargs) -> MultiModelAgentResponse:
        """Generate response using specified or default provider"""
        # Use specified provider or default
        if provider is None:
            provider = self.config.get('default_provider', 'Anthropic')
        
        if provider not in self.clients:
            available = list(self.clients.keys())
            if available:
                provider = available[0]
                st.warning(f"요청한 제공자를 사용할 수 없습니다. {provider}를 사용합니다.")
            else:
                raise ValueError("사용 가능한 AI 모델이 없습니다. API 키를 확인해주세요.")
        
        client = self.clients[provider]
        content = client.generate(prompt, **kwargs)
        model_info = client.get_model_info()
        
        return MultiModelAgentResponse(
            content=content,
            model_used=model_info['model'],
            provider=provider,
            metadata=model_info
        )
    
    def compare_models(self, prompt: str, providers: List[str] = None) -> Dict[str, MultiModelAgentResponse]:
        """Compare responses from multiple models"""
        if providers is None:
            providers = list(self.clients.keys())
        
        results = {}
        for provider in providers:
            if provider in self.clients:
                results[provider] = self.generate(prompt, provider)
        
        return results
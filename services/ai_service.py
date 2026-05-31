import openai
from typing import Optional
import json

from config import Config

class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"
    
    async def summarize_pdf(self, text: str, language: str = 'en') -> str:
        """Summarize PDF content"""
        if not Config.AI_ENABLED:
            return "AI features are not enabled."
        
        prompt = f"Please summarize the following document text in {language}:\n\n{text[:4000]}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    async def translate_document(self, text: str, target_language: str) -> str:
        """Translate document content"""
        if not Config.AI_ENABLED:
            return "AI features are not enabled."
        
        prompt = f"Translate the following text to {target_language}:\n\n{text[:4000]}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    async def rewrite_document(self, text: str, style: str = 'professional') -> str:
        """Rewrite document in different style"""
        if not Config.AI_ENABLED:
            return "AI features are not enabled."
        
        prompt = f"Rewrite the following text in a {style} style:\n\n{text[:4000]}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional document rewriter."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    async def extract_and_cleanup_text(self, text: str) -> str:
        """Extract and clean up text from document"""
        if not Config.AI_ENABLED:
            return "AI features are not enabled."
        
        prompt = f"Extract and clean up the following text, removing noise and formatting it properly:\n\n{text[:4000]}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a text processing expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    async def answer_questions(self, document_text: str, question: str) -> str:
        """Answer questions about document"""
        if not Config.AI_ENABLED:
            return "AI features are not enabled."
        
        prompt = f"Based on the following document, answer this question: {question}\n\nDocument:\n{document_text[:8000]}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    async def analyze_document(self, text: str) -> dict:
        """Analyze document and provide insights"""
        if not Config.AI_ENABLED:
            return {"error": "AI features are not enabled."}
        
        prompt = f"Analyze the following document and provide key insights, main topics, sentiment, and important points in JSON format:\n\n{text[:4000]}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a document analysis expert. Always respond in JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"analysis": response.choices[0].message.content}

# Global service instance
ai_service = AIService()

import os
import re

import requests


class AIAnalyzer:

    def __init__(self,
                 model_name=None,
                 host="http://localhost:11434",
                 num_ctx=4096,
                 timeout=300):

        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3:4b")
        self.host = host
        self.num_ctx = num_ctx
        self.timeout = timeout

    def analyze(self, text: str):

        prompt = f"""
Ты помощник специалиста по компьютерной экспертизе.

Проанализируй документ и верни JSON следующего вида:

{{
    "document_type": "...",
    "importance": "Высокая/Средняя/Низкая",
    "summary": "...",
    "suspicious_data": [
        ...
    ]
}}

Документ:

{text[:5000]}
"""

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "think": False,
            "options": {
                "num_ctx": self.num_ctx
            }
        }

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Не удалось подключиться к Ollama ({self.host}). "
                f"Запущен ли сервер? Запустите 'ollama serve'. Детали: {e}"
            )

        try:
            result = response.json()
        except ValueError:
            raise RuntimeError(
                f"Ollama вернул не-JSON ответ (HTTP {response.status_code}): "
                f"{response.text[:500]}"
            )

        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(
                f"Ollama сообщил об ошибке: {result['error']}\n"
                f"Чаще всего модель не скачана — выполните: "
                f"ollama pull {self.model_name}"
            )

        message = result.get("message") if isinstance(result, dict) else None

        if not isinstance(message, dict) or "content" not in message:
            raise RuntimeError(
                f"В ответе Ollama нет поля message.content. Получено: "
                f"{str(result)[:500]}"
            )

        return self._clean(message["content"])

    @staticmethod
    def _clean(answer: str) -> str:

        answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL)
        answer = re.sub(r"<think>.*", "", answer, flags=re.DOTALL)
        answer = answer.strip()

        start = answer.find("{")
        end = answer.rfind("}")

        if start != -1 and end != -1 and end > start:
            return answer[start:end + 1].strip()

        return answer
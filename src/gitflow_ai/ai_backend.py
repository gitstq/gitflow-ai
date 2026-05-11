"""
AI Backend Module
AI后端模块 - 支持多种AI提供商
"""

import os
import json
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class AIBackend(ABC):
    """AI后端抽象基类"""

    @abstractmethod
    def generate_commit_message(self, diff: str, context: Dict[str, Any]) -> Optional[str]:
        """生成提交信息"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取后端名称"""
        pass


class OpenAIBackend(AIBackend):
    """OpenAI后端"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                return None
        return self._client

    def is_available(self) -> bool:
        return self.api_key is not None and self._get_client() is not None

    def get_name(self) -> str:
        return f"OpenAI ({self.model})"

    def generate_commit_message(self, diff: str, context: Dict[str, Any]) -> Optional[str]:
        client = self._get_client()
        if not client:
            return None

        try:
            # 截断diff以避免超出token限制
            max_diff_length = 3000
            truncated_diff = diff[:max_diff_length]
            if len(diff) > max_diff_length:
                truncated_diff += "\n... (diff truncated)"

            prompt = self._build_prompt(truncated_diff, context)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Git commit message generator. Follow Conventional Commits format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return None

    def _build_prompt(self, diff: str, context: Dict[str, Any]) -> str:
        return f"""Generate a commit message following Conventional Commits format based on this git diff.

Format: <type>(<scope>): <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Code style (formatting)
- refactor: Code refactoring
- test: Tests
- chore: Maintenance

Context:
- Files changed: {context.get('files_changed', 'unknown')}
- Additions: {context.get('total_additions', 0)}
- Deletions: {context.get('total_deletions', 0)}

Git diff:
```diff
{diff}
```

Generate a concise commit message:"""


class AnthropicBackend(AIBackend):
    """Anthropic Claude后端"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                return None
        return self._client

    def is_available(self) -> bool:
        return self.api_key is not None and self._get_client() is not None

    def get_name(self) -> str:
        return f"Anthropic ({self.model})"

    def generate_commit_message(self, diff: str, context: Dict[str, Any]) -> Optional[str]:
        client = self._get_client()
        if not client:
            return None

        try:
            max_diff_length = 3000
            truncated_diff = diff[:max_diff_length]
            if len(diff) > max_diff_length:
                truncated_diff += "\n... (diff truncated)"

            prompt = self._build_prompt(truncated_diff, context)

            response = client.messages.create(
                model=self.model,
                max_tokens=100,
                temperature=0.3,
                system="You are a Git commit message generator. Follow Conventional Commits format.",
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()
        except Exception as e:
            return None

    def _build_prompt(self, diff: str, context: Dict[str, Any]) -> str:
        return f"""Generate a commit message following Conventional Commits format based on this git diff.

Format: <type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore

Files changed: {context.get('files_changed', 'unknown')}
Additions: +{context.get('total_additions', 0)}, Deletions: -{context.get('total_deletions', 0)}

Git diff:
```diff
{diff}
```

Commit message:"""


class OllamaBackend(AIBackend):
    """Ollama本地模型后端"""

    def __init__(self, model: str = "llama2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self._available = None

    def is_available(self) -> bool:
        if self._available is None:
            try:
                import urllib.request
                import urllib.error
                req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
                with urllib.request.urlopen(req, timeout=2) as response:
                    self._available = response.status == 200
            except Exception:
                self._available = False
        return self._available

    def get_name(self) -> str:
        return f"Ollama ({self.model})"

    def generate_commit_message(self, diff: str, context: Dict[str, Any]) -> Optional[str]:
        try:
            import urllib.request
            import urllib.error

            max_diff_length = 2000
            truncated_diff = diff[:max_diff_length]
            if len(diff) > max_diff_length:
                truncated_diff += "\n... (diff truncated)"

            prompt = self._build_prompt(truncated_diff, context)

            data = json.dumps({
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.host}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception as e:
            return None

    def _build_prompt(self, diff: str, context: Dict[str, Any]) -> str:
        return f"""Generate a git commit message in Conventional Commits format.

Format: type(scope): description

Types: feat, fix, docs, style, refactor, test, chore

Changed {context.get('files_changed', 'unknown')} files (+{context.get('total_additions', 0)}, -{context.get('total_deletions', 0)})

Diff:
{diff}

Commit message only:"""


class DeepSeekBackend(AIBackend):
    """DeepSeek后端"""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
        self.base_url = "https://api.deepseek.com"

    def is_available(self) -> bool:
        return self.api_key is not None

    def get_name(self) -> str:
        return f"DeepSeek ({self.model})"

    def generate_commit_message(self, diff: str, context: Dict[str, Any]) -> Optional[str]:
        try:
            import urllib.request
            import urllib.error

            max_diff_length = 3000
            truncated_diff = diff[:max_diff_length]
            if len(diff) > max_diff_length:
                truncated_diff += "\n... (diff truncated)"

            prompt = self._build_prompt(truncated_diff, context)

            data = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a Git commit message generator. Follow Conventional Commits format."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 100,
                "temperature": 0.3
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return None

    def _build_prompt(self, diff: str, context: Dict[str, Any]) -> str:
        return f"""根据以下git diff生成符合Conventional Commits格式的提交信息。

格式: <类型>(<作用域>): <描述>

类型: feat(新功能), fix(修复), docs(文档), style(格式), refactor(重构), test(测试), chore(维护)

变更: {context.get('files_changed', 'unknown')}个文件, +{context.get('total_additions', 0)}, -{context.get('total_deletions', 0)}

Diff:
```diff
{diff}
```

提交信息:"""


class AIBackendManager:
    """AI后端管理器"""

    def __init__(self):
        self.backends: List[AIBackend] = [
            OpenAIBackend(),
            AnthropicBackend(),
            DeepSeekBackend(),
            OllamaBackend(),
        ]

    def get_available_backends(self) -> List[AIBackend]:
        """获取所有可用的后端"""
        return [b for b in self.backends if b.is_available()]

    def get_default_backend(self) -> Optional[AIBackend]:
        """获取默认后端"""
        available = self.get_available_backends()
        return available[0] if available else None

    def generate_with_fallback(self, diff: str, context: Dict[str, Any]) -> Optional[str]:
        """使用可用的后端生成，带降级机制"""
        available = self.get_available_backends()

        for backend in available:
            result = backend.generate_commit_message(diff, context)
            if result:
                return result

        return None

"""Base agent class for all roles."""

from abc import ABC, abstractmethod
from typing import Any, Optional
import os

from ..state.models import IterationState


class BaseAgent(ABC):
    """Base class for PROPOSER, CRITIC, REFINER, META-REASONER."""

    def __init__(self, config: dict):
        self.config = config
        self.provider = config["llm"]["provider"]
        self.model = config["llm"]["model"]
        self._client: Optional[Any] = None

    @property
    def client(self):
        """Lazy-load the LLM client."""
        if self._client is None:
            if self.provider == "anthropic":
                import anthropic
                self._client = anthropic.Anthropic()
            else:
                import openai
                self._client = openai.OpenAI()
        return self._client

    @property
    @abstractmethod
    def role_name(self) -> str:
        """Name of this agent role."""
        pass

    @property
    @abstractmethod
    def temperature(self) -> float:
        """Temperature for this agent's LLM calls."""
        pass

    @abstractmethod
    def build_system_prompt(self, state: IterationState, **kwargs) -> str:
        """Build the system prompt for this role."""
        pass

    @abstractmethod
    def build_user_prompt(self, state: IterationState, **kwargs) -> str:
        """Build the user prompt for this role."""
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Any:
        """Parse the LLM response into structured data."""
        pass

    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make an LLM call and return the response."""
        max_tokens = self.config["llm"]["max_tokens"]

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content

    def execute(self, state: IterationState, **kwargs) -> tuple[Any, str]:
        """
        Execute this agent's role.

        Returns:
            Tuple of (parsed_result, raw_response)
        """
        system_prompt = self.build_system_prompt(state, **kwargs)
        user_prompt = self.build_user_prompt(state, **kwargs)

        raw_response = self.call_llm(system_prompt, user_prompt)
        parsed_result = self.parse_response(raw_response)

        return parsed_result, raw_response

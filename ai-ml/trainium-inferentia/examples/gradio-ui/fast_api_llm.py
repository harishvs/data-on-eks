from typing import Any, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
import requests

class AnyFastAPILlm(LLM):
    end_point: str

    @property
    def _llm_type(self) -> str:
        return "AnyFastAPILlm"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        response = requests.get(self.end_point, params={"sentence": prompt}, timeout=180)
        response.raise_for_status()
        return response.text

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"end_point": self.end_point}
from typing import Any, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
import requests
import re

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
        print("prompt",prompt)
        response = requests.get(self.end_point, params={"sentence": prompt}, timeout=180)
        response.raise_for_status()
        response = bytes(response.text, "utf-8").decode("unicode_escape")
        generated_text = response.replace('["', "")
        generated_text = generated_text.replace('"]', "")
        # add the input and response to session state
        
        lines = generated_text.splitlines()
        # print("lines")
        # print(lines)
        answer_index = None
        for i,line in enumerate(lines):
            # print(i,".",line.strip())
            if re.search(r"Answer:",line.strip()):
                answer_index = i
                break
        if answer_index is not None:
            if answer_index < len(lines)-1:                
                generated_text = "\n".join(lines[answer_index:])
            else:
                generated_text = "Shall i transfer to a human"
        return generated_text

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"end_point": self.end_point}
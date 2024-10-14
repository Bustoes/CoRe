from loguru import logger
from langchain_openai import ChatOpenAI, OpenAI
from langchain.schema import HumanMessage

from core.llms.basellm import BaseLLM

class AnyOpenAILLM(BaseLLM):
    def __init__(self, model_name: str = 'gpt-3.5-turbo', json_mode: bool = False, *args, **kwargs):
        """Initialize the OpenAI LLM.
        
        Args:
            `model_name` (`str`, optional): The name of the OpenAI model. Defaults to `gpt-3.5-turbo`.
            `json_mode` (`bool`, optional): Whether to use the JSON mode of the OpenAI API. Defaults to `False`.
        """
        self.model_name = model_name
        self.json_mode = json_mode
        if json_mode and self.model_name not in ['gpt-3.5-turbo-1106', 'gpt-4-1106-preview', "gpt-4o-mini", "gpt-4o-2024-08-06", "o1-mini"]:
            raise ValueError("json_mode is only available for gpt-3.5-turbo-1106, gpt-4-1106-preview, gpt-4o-mini, gpt-4o-2024-08-06, o1-mini")
        self.max_tokens: int = kwargs.get('max_tokens', 256)
        self.max_context_length: int = 16384# if '16k' in model_name else 32768 if '32k' in model_name else 4096
        if model_name.split('-')[0] == 'text' or model_name in ['gpt-3.5-turbo-instruct', "o1-mini"]:
            self.model = OpenAI(model_name=model_name, *args, **kwargs)
            self.model_type = 'completion'
        else:
            if json_mode:
                logger.info(f"Creating OpenAI agent. Model {self.model_name}. JSON mode.")
                if 'model_kwargs' in kwargs:
                    kwargs['model_kwargs']['response_format'] = {
                        "type": "json_object"
                    }
                else:
                    kwargs['model_kwargs'] = {
                        "response_format": {
                            "type": "json_object"
                        }
                    }
            else:
                logger.info(f"Creating OpenAI agent. Model {self.model_name}.")
            self.model = ChatOpenAI(model_name=model_name, *args, **kwargs)
            self.model_type = 'chat'
    
    def __call__(self, prompt: str, *args, **kwargs) -> str:
        """Forward pass of the OpenAI LLM.
        
        Args:
            `prompt` (`str`): The prompt to feed into the LLM.
        Returns:
            `str`: The OpenAI LLM output.
        """
        if self.model_type == 'completion':
            return self.model.invoke(prompt).content.replace('\n', ' ').strip()
        else:
            return self.model.invoke(
                [
                    HumanMessage(
                        content=prompt,
                    )
                ]
            ).content.replace('\n', ' ').strip()
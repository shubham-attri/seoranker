from enum import Enum
from typing import Dict
from pathlib import Path
import json

class TaskType(Enum):
    BLOG = "blog"
    SOCIAL = "social"

class ModelProvider(Enum):
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"

class ModelConfig:
    def __init__(self):
        self.config_file = Path("config/models.json")
        self._load_config()
    
    def _load_config(self):
        if not self.config_file.exists():
            self._create_default_config()
        
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
    
    def _create_default_config(self):
        default_config = {
            "blog": {
                "provider": "local",
                "model": "llama-3.2-3b-instruct",
                "fallback": {
                    "provider": "groq",
                    "model": "mixtral-8x7b-32768"
                }
            },
            "social": {
                "provider": "groq",
                "model": "mixtral-8x7b-32768",
                "fallback": {
                    "provider": "local",
                    "model": "llama-3.2-3b-instruct"
                }
            }
        }
        
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.config = default_config
    
    def get_model_config(self, task: TaskType) -> Dict:
        return self.config[task.value]
    
    def update_model_config(self, task: TaskType, provider: ModelProvider, model: str):
        self.config[task.value] = {
            "provider": provider.value,
            "model": model
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
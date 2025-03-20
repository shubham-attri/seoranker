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
            
    def configure_models(self) -> bool:
        """Interactive configuration of model settings"""
        try:
            print("\n=== Model Configuration ===")
            
            # Display current configuration
            print("\nCurrent configuration:")
            for task, config in self.config.items():
                provider = config.get("provider", "unknown")
                model = config.get("model", "unknown")
                print(f"- {task.upper()}: {provider} / {model}")
            
            # Select task to configure
            print("\nSelect task to configure:")
            print("1. Blog Content")
            print("2. Social Media Content")
            print("3. Back to main menu")
            
            choice = input("Select option (1-3): ")
            
            if choice == "3":
                return True
                
            if choice == "1":
                task = TaskType.BLOG
                print("\n=== Configure Blog Content Model ===")
            elif choice == "2":
                task = TaskType.SOCIAL
                print("\n=== Configure Social Media Model ===")
            else:
                print("\n✗ Invalid option")
                return False
            
            # Configure provider
            print("\nSelect provider:")
            print("1. Anthropic (Claude)")
            print("2. Groq")
            print("3. Local")
            provider_choice = input("Select option (1-3): ")
            
            if provider_choice == "1":
                provider = ModelProvider.ANTHROPIC
                print("\nSelect Anthropic model:")
                print("1. claude-3-opus-20240229")
                print("2. claude-3-sonnet-20240229")
                print("3. claude-3-haiku-20240307")
                model_choice = input("Select option (1-3): ")
                
                if model_choice == "1":
                    model = "claude-3-opus-20240229"
                elif model_choice == "2":
                    model = "claude-3-sonnet-20240229"
                elif model_choice == "3":
                    model = "claude-3-haiku-20240307"
                else:
                    print("\n✗ Invalid option, using default")
                    model = "claude-3-sonnet-20240229"
                    
            elif provider_choice == "2":
                provider = ModelProvider.GROQ
                print("\nSelect Groq model:")
                print("1. llama2-70b-4096")
                print("2. mixtral-8x7b-32768")
                print("3. gemma-7b-it")
                model_choice = input("Select option (1-3): ")
                
                if model_choice == "1":
                    model = "llama2-70b-4096"
                elif model_choice == "2":
                    model = "mixtral-8x7b-32768"
                elif model_choice == "3":
                    model = "gemma-7b-it"
                else:
                    print("\n✗ Invalid option, using default")
                    model = "mixtral-8x7b-32768"
            elif provider_choice == "3":
                provider = ModelProvider.LOCAL
                print("\nSelect Local model:")
                print("1. llama-3.2-3b-instruct")
                print("2. llama-3.2-8b-instruct")
                print("3. phi-3-mini-4k-instruct")
                model_choice = input("Select option (1-3): ")
                
                if model_choice == "1":
                    model = "llama-3.2-3b-instruct"
                elif model_choice == "2":
                    model = "llama-3.2-8b-instruct"
                elif model_choice == "3":
                    model = "phi-3-mini-4k-instruct"
                else:
                    print("\n✗ Invalid option, using default")
                    model = "llama-3.2-3b-instruct"
            else:
                print("\n✗ Invalid option")
                return False
            
            # Update configuration
            self.update_model_config(task, provider, model)
                
            print(f"\n✓ Configuration updated for {task.value.upper()}")
            print(f"Provider: {provider.value}")
            print(f"Model: {model}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error configuring models: {str(e)}")
            return False
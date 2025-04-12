from typing import List, Dict
from transformers import pipeline
import torch
import logging
import threading

logger = logging.getLogger(__name__)

class CodeExplainer:
    _model = None
    
    _model_lock = threading.Lock()
    
    @classmethod
    def get_model(cls):
        with cls._model_lock:
            if cls._model is None:
                logger.info("Loading AI model...")
                try:
                    try:
                        # Try with 4-bit quantized model first
                        from transformers import BitsAndBytesConfig
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16
                        )
                        cls._model = pipeline(
                            "text-generation",
                            model="codellama/CodeLlama-7b-instruct-hf",
                            device_map="auto",
                            model_kwargs={"quantization_config": quantization_config},
                            torch_dtype=torch.float16
                        )
                    except Exception as e:
                        logger.warning(f"4-bit loading failed: {str(e)}")
                        # Fallback to CPU with smaller model
                        cls._model = pipeline(
                            "text-generation",
                            model="codellama/CodeLlama-7b-instruct-hf",
                            device="cpu",
                            torch_dtype=torch.float32
                        )
                    logger.info("Model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load model: {str(e)}")
                    # Fallback to CPU
                    cls._model = pipeline(
                        "text-generation",
                        model="codellama/CodeLlama-7b-instruct-hf", 
                        device="cpu",
                        torch_dtype=torch.float32
                    )
                    logger.info("Using CPU fallback model")
            return cls._model

    def __init__(self):
        self.model = self.get_model()
        self.system_prompt = """[INST] <<SYS>>
You are a Python code execution analyzer. 
Explain what happens at each step of execution in simple terms.
Focus on variable changes and control flow.
<</SYS>>"""

    def explain_step(self, 
                   code: str, 
                   step: Dict[str, any]) -> str:
        try:
            prompt = f"""{self.system_prompt}
Code being executed:
{code}

Current execution state:
- Line {step['line_no']}: {step['event']}
- Stack: {', '.join(step['stack'])}
- Variables: {step['variables']}

Explain what's happening in this step: [/INST]"""

            if not hasattr(self, 'model') or self.model is None:
                return "Explanation service not ready"
                
            response = self.model(
                prompt,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True
            )
            
            if not response or len(response) == 0:
                return "No explanation generated"
                
            full_text = response[0].get('generated_text', '')
            if '[/INST]' not in full_text:
                return "Explanation format error"
                
            explanation = full_text.split('[/INST]')[-1].strip()            
            return explanation
            
            
        except torch.cuda.OutOfMemoryError:
            return "GPU memory exhausted - try smaller code segments"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Explanation error: {str(e)}"

    def explain_full_trace(self,
                         code: str,
                         trace: List[Dict[str, any]]) -> List[str]:
        # Process in batches to manage memory
        batch_size = 3
        explanations = []
        for i in range(0, len(trace), batch_size):
            batch = trace[i:i+batch_size]
            try:
                explanations.extend([self.explain_step(code, step) for step in batch])
            except Exception as e:
                logger.error(f"Batch processing failed: {str(e)}")
                explanations.extend(["Explanation failed"] * len(batch))
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        return explanations

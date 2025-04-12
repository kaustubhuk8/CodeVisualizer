from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
from typing import Dict, Any
import json
from pydantic import BaseModel
from tracer import CodeTracer
from explain import CodeExplainer
import io
import contextlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeExecutionRequest(BaseModel):
    code: str
    input_data: Dict[str, Any] = {}

@app.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    try:
        # Create tracer and set up execution environment
        tracer = CodeTracer()
        sys.settrace(tracer.trace_execution)
        
        # Prepare globals with input data
        globals_dict = request.input_data.copy()
        
        # Redirect stdout during execution
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            try:
                exec(request.code, globals_dict)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Execution error: {str(e)}"
                )
            finally:
                sys.settrace(None)
        
        # Get execution trace
        trace = tracer.get_trace()
        
        # Generate AI explanations
        try:
            explainer = CodeExplainer()
            logger.info("Generating AI explanations...")
            explanations = explainer.explain_full_trace(request.code, trace)
            
            # Combine trace with explanations and visualization data
            for step, explanation in zip(trace, explanations):
                if isinstance(explanation, dict):
                    step.update({
                        'explanation': explanation.get('explanation', ''),
                        'visualization': explanation.get('visualization', {})
                    })
                else:
                    step['explanation'] = explanation
                    step['visualization'] = {}
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            # Continue with empty explanations if generation fails
            for step in trace:
                step['explanation'] = "Explanation unavailable"
            
        # Prepare response
        response_data = {
            "status": "success",
            "trace": trace,
            "output": stdout.getvalue()
        }
        try:
            return json.loads(json.dumps(response_data, default=str))
        except Exception as e:
            logger.error(f"Response serialization failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to prepare response"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

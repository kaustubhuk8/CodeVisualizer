import sys
import ast
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class VariableState:
    name: str
    type: str
    value: Any
    changed: bool = False

@dataclass
class ExecutionStep:
    line_no: int
    event: str  # 'call', 'line', 'return', etc.
    code: str
    variables: Dict[str, VariableState]
    stack: List[str]
    timestamp: float

class CodeTracer:
    def __init__(self):
        self.trace: List[ExecutionStep] = []
        self.current_vars: Dict[str, Any] = {}
        self.prev_vars: Dict[str, Any] = {}
        self.stack: List[str] = []

    def trace_execution(self, frame, event, arg):
        # Skip internal Python frames
        if frame.f_code.co_filename.startswith('<'):
            return self.trace_execution

        # Get current line and code
        line_no = frame.f_lineno
        code = frame.f_code.co_code

        # Track variable changes
        self._track_variable_changes(frame)

        # Create execution step
        step = ExecutionStep(
            line_no=line_no,
            event=event,
            code=code,
            variables=self._get_variable_states(),
            stack=self.stack.copy(),
            timestamp=time.time()
        )
        self.trace.append(step)

        # Handle stack for call/return events
        if event == 'call':
            self.stack.append(frame.f_code.co_name)
        elif event == 'return':
            if self.stack:
                self.stack.pop()

        return self.trace_execution

    def _track_variable_changes(self, frame):
        self.prev_vars = self.current_vars.copy()
        self.current_vars = {
            name: frame.f_locals[name]
            for name in frame.f_locals
            if not name.startswith('_')
        }

    def _get_variable_states(self) -> Dict[str, VariableState]:
        var_states = {}
        for name, value in self.current_vars.items():
            # Handle bytes and other non-JSON-serializable types
            if isinstance(value, bytes):
                value_repr = f"<bytes: {len(value)} bytes>"
            else:
                try:
                    value_repr = repr(value)
                except:
                    value_repr = str(value)
            
            var_states[name] = VariableState(
                name=name,
                type=type(value).__name__,
                value=value_repr,
                changed=name not in self.prev_vars or self.prev_vars[name] != value
            )
        return var_states

    def get_trace(self) -> List[Dict[str, Any]]:
        trace_data = []
        for step in self.trace:
            step_dict = {
                'line_no': step.line_no,
                'event': step.event,
                'code': step.code,
                'stack': step.stack,
                'timestamp': step.timestamp,
                'variables': {}
            }
            for name, var in step.variables.items():
                step_dict['variables'][name] = {
                    'name': var.name,
                    'type': var.type,
                    'value': var.value if isinstance(var.value, (str, int, float, bool)) else str(var.value),
                    'changed': var.changed
                }
            trace_data.append(step_dict)
        return trace_data

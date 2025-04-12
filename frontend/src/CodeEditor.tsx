import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { 
  Button, 
  Box, 
  Typography, 
  Paper, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Divider,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import TerminalIcon from '@mui/icons-material/Terminal';
import CodeIcon from '@mui/icons-material/Code';
import InfoIcon from '@mui/icons-material/Info';

interface TraceStep {
  line_no: number;
  event: string;
  code: string;
  variables: Record<string, {
    name: string;
    type: string;
    value: string;
    changed: boolean;
  }>;
  stack: string[];
  timestamp: number;
  explanation?: string;
}

const CodeEditor: React.FC = () => {
  const [code, setCode] = useState<string>(
    `def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(5)`
  );
  const [trace, setTrace] = useState<TraceStep[]>([]);
  const [output, setOutput] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [expandedStep, setExpandedStep] = useState<number | false>(false);

  const handleStepChange = (panel: number) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedStep(isExpanded ? panel : false);
  };

  const executeCode = async () => {
    setIsExecuting(true);
    setTrace([]);
    setOutput('');
    try {
      const response = await fetch('http://localhost:8000/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          input_data: {}
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setTrace(data.trace);
        setOutput(data.output);
        if (data.trace.length > 0) {
          setExpandedStep(0);
        }
      }
    } catch (error) {
      console.error('Execution error:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      height: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      {/* Code Editor Panel */}
      <Paper elevation={3} sx={{ 
        flex: 1, 
        margin: 2,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <Box sx={{
          padding: 2,
          backgroundColor: '#1976d2',
          color: 'white',
          display: 'flex',
          alignItems: 'center'
        }}>
          <CodeIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Python Code Editor</Typography>
        </Box>
        <Box sx={{ flex: 1 }}>
          <Editor
            height="100%"
            defaultLanguage="python"
            value={code}
            onChange={(value) => setCode(value || '')}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              theme: 'vs-light',
              scrollBeyondLastLine: false
            }}
          />
        </Box>
        <Box sx={{ padding: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            onClick={executeCode}
            disabled={isExecuting}
            startIcon={<PlayArrowIcon />}
            sx={{ 
              minWidth: 120,
              backgroundColor: '#1976d2',
              '&:hover': { backgroundColor: '#1565c0' }
            }}
          >
            {isExecuting ? 'Executing...' : 'Execute'}
          </Button>
        </Box>
      </Paper>

      {/* Execution Trace Panel */}
      <Paper elevation={3} sx={{ 
        flex: 1, 
        margin: 2,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <Box sx={{
          padding: 2,
          backgroundColor: '#1976d2',
          color: 'white',
          display: 'flex',
          alignItems: 'center'
        }}>
          <TerminalIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Execution Trace</Typography>
        </Box>
        
        <Box sx={{ 
          flex: 1, 
          padding: 2, 
          overflow: 'auto',
          backgroundColor: '#fafafa'
        }}>
          {trace.length === 0 ? (
            <Typography variant="body1" color="textSecondary" sx={{ textAlign: 'center', mt: 4 }}>
              No execution trace available. Run your code to see the execution flow.
            </Typography>
          ) : (
            trace.map((step, index) => (
              <Accordion 
                key={index} 
                expanded={expandedStep === index}
                onChange={handleStepChange(index)}
                sx={{ mb: 2 }}
              >
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  sx={{ 
                    backgroundColor: expandedStep === index ? '#e3f2fd' : 'inherit',
                    '&:hover': { backgroundColor: '#e3f2fd' }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip 
                      label={`Line ${step.line_no}`} 
                      color="primary" 
                      size="small" 
                    />
                    <Typography variant="subtitle1">
                      {step.event === 'call' ? 'Function call' : 
                       step.event === 'return' ? 'Function return' : 
                       'Line execution'}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Stack Trace:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {step.stack.map((frame, i) => (
                        <Chip key={i} label={frame} size="small" />
                      ))}
                    </Box>
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Variables:
                  </Typography>
                  <Box sx={{ 
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                    gap: 1
                  }}>
                    {Object.entries(step.variables).map(([name, variable]) => (
                      <Card 
                        key={name}
                        variant="outlined" 
                        sx={{ 
                          borderLeft: variable.changed ? '4px solid #1976d2' : '4px solid #e0e0e0'
                        }}
                      >
                        <CardContent sx={{ py: 1, px: 2 }}>
                          <Typography variant="body2">
                            <strong>{name}</strong>: {variable.value}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Type: {variable.type}
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </Box>

                  {step.explanation && (
                    <>
                      <Divider sx={{ my: 2 }} />
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: 1,
                        mb: 1
                      }}>
                        <InfoIcon color="primary" />
                        <Typography variant="subtitle2">
                          What's happening:
                        </Typography>
                      </Box>
                      <Paper variant="outlined" sx={{ 
                        p: 2,
                        backgroundColor: '#e8f5e9',
                        borderLeft: '4px solid #4caf50'
                      }}>
                        <Typography component="div" sx={{ 
                          whiteSpace: 'pre-wrap',
                          lineHeight: 1.6,
                          '& .highlight': {
                            backgroundColor: '#fff9c4',
                            padding: '0 2px',
                            borderRadius: '2px'
                          }
                        }}>
                          {step.explanation.split('\n').map((line, i) => (
                            <div key={i}>{line}</div>
                          ))}
                        </Typography>
                      </Paper>
                    </>
                  )}
                </AccordionDetails>
              </Accordion>
            ))
          )}
          
          {output && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom>
                Program Output:
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#fff' }}>
                <Typography component="pre" sx={{ 
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0
                }}>
                  {output}
                </Typography>
              </Paper>
            </>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default CodeEditor;

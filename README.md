# Code Visualizer

An interactive tool that visualizes Python code execution with AI-powered explanations.

![Screenshot](assets/screenshot.png)

## Features

- Step-by-step execution visualization
- AI-generated explanations for each step
- Variable state tracking
- Call stack visualization
- Interactive debugging interface

## Technologies

- **Frontend**: React + TypeScript + Vite + Material UI
- **Backend**: FastAPI + Python
- **AI**: CodeLlama 7B (Hugging Face Transformers)
- **Code Analysis**: Python AST + Execution Tracing

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- GPU (recommended for AI explanations)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/code-visualizer.git
cd code-visualizer
```

2. Install backend dependencies:
```bash
cd visualizer/backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd visualizer/backend
python main.py
```

2. Start the frontend development server:
```bash
cd ../frontend
npm run dev
```

3. Open http://localhost:3000 in your browser

## Project Structure

```
visualizer/
├── backend/          # Python backend server
│   ├── main.py       # FastAPI server
│   ├── explain.py    # AI explanation service
│   └── tracer.py     # Code execution tracer
├── frontend/         # React frontend
│   ├── src/          # Frontend source code
│   └── public/       # Static assets
├── examples/         # Sample Python code
└── shared/           # Shared utilities
```

## Configuration

Create a `.env` file in the backend directory with your Hugging Face token:

```
HF_TOKEN=your_huggingface_token
```

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your

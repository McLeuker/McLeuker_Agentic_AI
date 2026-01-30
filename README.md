# McLeuker Agentic AI Platform

**The execution-first, agentic AI system that acts as a digital team member for professionals across various industries.**

---

## 1. Overview

The McLeuker Agentic AI Platform is a sophisticated backend system designed to understand complex user prompts, perform real-time research, structure information, and execute tasks to generate ready-to-use deliverables. Unlike traditional AI chatbots that provide text-only responses, this platform gets the work done, delivering outputs in formats like Excel, PDF, PowerPoint, and more.

This repository contains the complete backend source code for the platform, built with a modular, scalable, and high-performance architecture using Python and FastAPI.

## 2. Architecture

The platform is built around a **Unified Agent Orchestrator** that coordinates a multi-layer pipeline to process requests. This ensures a clear separation of concerns and a robust workflow.

- **Client UI**: The entry point for user requests.
- **Unified Agent (Orchestrator)**: The brain of the system that manages the entire task lifecycle.
- **Task Interpretation Layer**: Understands the user's intent, detects the domain, and determines the required outputs.
- **LLM Reasoning Layer**: Creates a strategic plan, defines research questions, and outlines the logical steps for execution.
- **Real-Time Web Research Layer**: Gathers up-to-date information from the web using advanced search and scraping tools.
- **General Logic & Structuring Layer**: Transforms raw research into structured data (tables, report outlines, etc.) ready for file generation.
- **Execution Layer**: A suite of specialized agents that generate the final files in various formats (Excel, PDF, PPT, Code, etc.).
- **Output Delivery**: The final, ready-to-use deliverables.

For a more detailed breakdown, see the [Architecture Document](./docs/ARCHITECTURE.md).

## 3. Features

- **Multi-Layer Agentic System**: A robust pipeline that mimics a human workflow: understanding, planning, researching, structuring, and executing.
- **Multi-LLM Support**: Easily switch between top-tier LLMs like OpenAI's GPT-4 and xAI's Grok.
- **Real-Time Intelligence**: Integrated web research capabilities to provide up-to-date and relevant information.
- **Execution-First Approach**: Delivers tangible outputs (files) rather than just text, making it a true productivity tool.
- **Multi-Format Output**: Dynamically generates a wide range of professional documents:
  - **Excel (`.xlsx`) & CSV (`.csv`)**: For datasets, tables, and lists.
  - **PDF (`.pdf`) & Word (`.docx`)**: For professional reports, briefs, and summaries.
  - **PowerPoint (`.pptx`)**: For presentations and slide decks.
  - **Web (`.html`)**: For web snippets and dashboards.
  - **Code (`.py`, `.js`, etc.)**: For scripts and automation pipelines.
- **AI-Powered Search**: A standalone search platform similar to Manus AI or Perplexity for advanced information retrieval.
- **Scalable & Modular**: Built with Python and FastAPI for high performance and easy extension.
- **Lovable Integration Ready**: Designed with CORS and WebSocket support for seamless integration with front-end platforms like Lovable.

## 4. Technology Stack

| Component                 | Technology                                       |
| ------------------------- | ------------------------------------------------ |
| **Backend Framework**     | FastAPI                                          |
| **LLM Providers**         | OpenAI (GPT-4), Grok                             |
| **Agent Orchestration**   | Custom Orchestrator                              |
| **Web Research**          | Serper, Tavily, DuckDuckGo, BeautifulSoup, HTTPX |
| **File Generation**       | Pandas, OpenPyXL, ReportLab, python-pptx, python-docx |
| **Data Validation**       | Pydantic                                         |
| **Server**                | Uvicorn                                          |

## 5. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/mcleuker-agentic-ai.git
    cd mcleuker-agentic-ai
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 6. Configuration

1.  **Create a `.env` file** in the root directory of the project by copying the example file:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** to add your API keys and other settings:
    ```env
    # --- API Keys ---
    # At least one LLM key is required
    OPENAI_API_KEY="sk-..."
    GROK_API_KEY="..."

    # At least one search key is recommended for best results
    SERPER_API_KEY="..."  # For Google Search results via serper.dev
    TAVILY_API_KEY="..."  # For AI-optimized search via tavily.com

    # --- LLM Settings ---
    # Set the default LLM provider ('openai' or 'grok')
    DEFAULT_LLM_PROVIDER="openai"
    OPENAI_MODEL="gpt-4-turbo-preview"
    GROK_MODEL="grok-1.5-flash" # Or other available models

    # --- Application Settings ---
    DEBUG=True
    ```

## 7. Usage

### Running the Server

Start the FastAPI server using Uvicorn:

```bash
python -m src.api.main
```

Or for development with auto-reload:

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### API Documentation

Once the server is running, interactive API documentation (Swagger UI) is available at:

`http://127.0.0.1:8000/docs`

### Example API Calls

#### 1. Process a Task Synchronously

This endpoint is great for quick tasks where you want to wait for the result.

```bash
curl -X POST "http://127.0.0.1:8000/api/tasks/sync" \
-H "Content-Type: application/json" \
-d '{
  "prompt": "Create a competitor analysis and trend report for sustainable fashion brands in Europe for SS26. Export Excel and PDF."
}'
```

#### 2. Perform an AI-Powered Search

```bash
curl -X POST "http://127.0.0.1:8000/api/search" \
-H "Content-Type: application/json" \
-d '{
  "query": "latest trends in AI-driven fashion design"
}'
```

#### 3. Chat with the Agent

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "What are the key sustainability certifications for textiles?"
}'
```

## 8. Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

## 9. Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](./CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## 10. License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

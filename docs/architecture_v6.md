# McLeuker AI V6 - Manus AI-Style Architecture

**Date:** 2026-02-04
**Author:** Manus AI

## 1. Overview

This document outlines the architecture for McLeuker AI V6, a comprehensive upgrade designed to emulate the reasoning, transparency, and structured output capabilities of Manus AI. The goal is to provide users with a clear, real-time view into the AI's thinking process, from task decomposition to final response generation.

This architecture introduces a **Reasoning-First** approach, where the AI's thought process is a primary output, not a hidden detail.

## 2. Core Principles

- **Transparency:** Users should always know what the AI is doing and why.
- **Structure:** All outputs must follow a strict, predictable contract.
- **Memory:** The AI must maintain context across conversational turns.
- **Real-time:** The user interface should update in real-time with the AI's progress.

## 3. High-Level Architecture

The system is composed of two main parts: the **Backend (FastAPI)** and the **Frontend (Next.js)**.

```mermaid
graph TD
    subgraph Frontend (Next.js)
        A[Dashboard UI] --> B{Reasoning Panel};
        A --> C{Structured Output};
    end

    subgraph Backend (FastAPI)
        D[API Endpoint: /api/chat/stream] --> E[Orchestrator];
        E --> F{Reasoning Engine};
        E --> G{Task Decomposer};
        E --> H{Memory Manager};
        E --> I{Search Layer};
        E --> J{Content Generator};
    end

    A -- HTTP Request --> D;
    D -- SSE Stream --> A;
```

## 4. Backend Architecture

The backend is responsible for processing user queries, managing the AI's reasoning, and streaming events to the frontend.

### 4.1. Streaming API Endpoint (`/api/chat/stream`)

This will be the primary endpoint for all chat interactions. It will use Server-Sent Events (SSE) to stream a series of JSON objects to the frontend.

**Event Structure:**

Each event will have the following structure:

```json
{
  "type": "event_type",
  "data": { ... },
  "step": 1,
  "total_steps": 6,
  "timestamp": "2026-02-04T22:30:00Z"
}
```

**Event Types (`StreamEventType`):**

- `THINKING`: The AI's internal monologue or reasoning.
- `PLANNING`: The breakdown of the task into steps.
- `SEARCHING`: The status of the information retrieval process.
- `ANALYZING`: The process of analyzing the retrieved information.
- `GENERATING`: The generation of the final response.
- `SOURCE`: A single source that has been found.
- `INSIGHT`: A key insight that has been discovered.
- `PROGRESS`: A percentage-based progress update.
- `CONTENT`: A chunk of the final response content.
- `COMPLETE`: The final, complete `ResponseContract` object.
- `ERROR`: An error message.

### 4.2. Orchestrator (`orchestrator.py`)

The orchestrator will be the central component that manages the entire workflow. It will be responsible for:

1.  Receiving the user query.
2.  Invoking the `Reasoning Engine` to generate an initial plan.
3.  Using the `Task Decomposer` to break the plan into executable steps.
4.  Managing the `Memory Manager` to maintain context.
5.  Executing each step, which may involve calling the `Search Layer` or other tools.
6.  Streaming progress events to the frontend at each stage.
7.  Calling the `Content Generator` to create the final structured response.

### 4.3. Reasoning Engine

This new component will be a dedicated module that takes a user query and generates a chain-of-thought reasoning process. It will output a structured plan that the `Task Decomposer` can use.

### 4.4. Memory Manager

The `session_contexts` dictionary will be expanded into a more robust `MemoryManager` class. It will be responsible for:

- Storing and retrieving conversation history for a given `session_id`.
- Extracting key entities and concepts from the conversation to maintain context.
- Summarizing previous turns to keep the context window manageable.

### 4.5. Response Contract (`response_contract.py`)

The existing `ResponseContract` will be strictly enforced. The `Content Generator` will be responsible for populating this contract at the end of the process.

## 5. Frontend Architecture

The frontend will be updated to provide a rich, real-time user experience.

### 5.1. Dashboard (`dashboard/page.tsx`)

The main dashboard component will be responsible for:

- Managing the connection to the `/api/chat/stream` SSE endpoint.
- Receiving and parsing the streaming events.
- Updating the state of the `Reasoning Panel` and `Structured Output` components.

### 5.2. Reasoning Panel

A new component will be created to display the real-time progress of the AI. It will show:

- The current step in the process (e.g., "Thinking", "Searching").
- The AI's reasoning and plan.
- A progress bar indicating the overall completion.
- A list of sources as they are found.

### 5.3. Structured Output

The main content area will be updated to render the components of the `ResponseContract` once the `COMPLETE` event is received. This will include dedicated components for:

- Summary
- Key Insights
- Main Content (prose)
- Sources
- Tables
- Generated Files
- Follow-up Questions

## 6. Implementation Plan

1.  **Phase 3: Backend - Reasoning & Decomposition:** Implement the `ReasoningEngine` and enhance the `Orchestrator` to use it.
2.  **Phase 4: Backend - Memory:** Build the `MemoryManager` class and integrate it into the `Orchestrator`.
3.  **Phase 5: Backend - Streaming:** Refine the `process_stream` method to send all the new event types.
4.  **Phase 6: Frontend - Reasoning Panel:** Build the new `ReasoningPanel` component and connect it to the streaming endpoint.
5.  **Phase 7: Frontend - Structured Output:** Create the components to render the `ResponseContract`.
6.  **Phase 8: Testing:** Thorough end-to-end testing and deployment.

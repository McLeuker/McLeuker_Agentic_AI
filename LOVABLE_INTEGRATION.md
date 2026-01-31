# Lovable Frontend Integration Guide (v2.0.0)

To connect your Lovable frontend with the new Agentic AI backend, follow these instructions and use the provided prompts.

## 1. Core Changes Required
The new backend (v2.0.0) introduces several breaking changes to improve functionality:
- **Conversation ID**: Must be sent with every request to enable memory.
- **New Response Format**: Includes `reasoning`, `sources`, and `files` fields.
- **Markdown Rendering**: The `message` field now contains rich Markdown with emojis and sections.

## 2. Lovable Prompts

### Prompt 1: Update API Service
Copy and paste this into Lovable to update the backend connection:
> "Update the API service to connect to the new v2.0.0 backend. 
> 1. Change the base URL to my Railway deployment URL.
> 2. Update the `/api/chat` request body to include `conversation_id` (stored in local state or URL params).
> 3. Update the response handling to support the new JSON structure:
>    - `message`: Main Markdown content.
>    - `reasoning`: Optional string containing the AI's thought process.
>    - `sources`: Array of `{title, url}` objects.
>    - `files`: Array of `{filename, filepath, type, size}` objects.
> 4. Add a `mode` toggle (Quick/Deep) to the chat input that sends 'quick' or 'deep' in the request."

### Prompt 2: Update Chat UI
Copy and paste this to improve the UI for the new features:
> "Enhance the Chat UI to support the new Agentic AI features:
> 1. Use a Markdown renderer (like `react-markdown`) for the AI messages to support emojis, bold text, and sections.
> 2. Add a collapsible 'Reasoning' component at the top of AI responses that displays the `reasoning` field when available.
> 3. Add a 'Sources' section at the bottom of messages to display the `sources` array as clickable links.
> 4. Add a 'Generated Files' component that shows the `files` array with download buttons pointing to `${BACKEND_URL}/api/files/${filename}`.
> 5. Ensure the `conversation_id` is persisted so the AI remembers previous messages."

## 3. API Reference for Lovable

### Chat Endpoint
- **URL**: `POST /api/chat`
- **Request**:
```json
{
  "message": "User query here",
  "conversation_id": "unique-session-id",
  "mode": "deep"
}
```
- **Response**:
```json
{
  "message": "Markdown content...",
  "conversation_id": "unique-session-id",
  "reasoning": "Thought process...",
  "sources": [{"title": "Source", "url": "https://..."}],
  "files": [{"filename": "data.xlsx", "type": "Excel", "size": "5KB"}],
  "follow_up_questions": ["Question 1?"]
}
```

### File Download
- **URL**: `GET /api/files/{filename}`
- **Usage**: Direct link for users to download generated Excel/PDF/Word files.

# Lovable Integration Files

This folder contains ready-to-use files for integrating the McLeuker Agentic AI Platform backend with a Lovable frontend.

## Contents

| File/Folder | Description |
|-------------|-------------|
| `api.ts` | Complete API client with TypeScript types |
| `hooks.ts` | Custom React hooks for using the API |
| `components/ChatInterface.tsx` | Full-featured chat interface component |
| `components/SearchInterface.tsx` | AI-powered search interface component |
| `components/TaskSubmitter.tsx` | Task submission and file download component |

## Quick Start

1. **Copy the files to your Lovable project:**
   - Copy `api.ts` to `src/lib/api.ts`
   - Copy `hooks.ts` to `src/hooks/` (you may need to split into individual files)
   - Copy components to `src/components/`

2. **Set up environment variables:**
   Create a `.env` file in your Lovable project:
   ```env
   VITE_API_BASE_URL=https://your-backend-url.com
   VITE_WS_BASE_URL=wss://your-backend-url.com
   ```

3. **Use the components:**
   ```tsx
   import { ChatInterface } from '@/components/ChatInterface';
   import { SearchInterface } from '@/components/SearchInterface';
   import { TaskSubmitter } from '@/components/TaskSubmitter';

   function App() {
     return (
       <div className="container mx-auto p-4">
         <ChatInterface />
         {/* or */}
         <SearchInterface />
         {/* or */}
         <TaskSubmitter />
       </div>
     );
   }
   ```

## Dependencies

These components assume you have the following shadcn/ui components installed:
- Button
- Input
- Textarea
- Card
- Badge
- ScrollArea
- Progress

If you don't have these, install them using the shadcn/ui CLI:
```bash
npx shadcn-ui@latest add button input textarea card badge scroll-area progress
```

## Full Documentation

See [LOVABLE_INTEGRATION.md](../docs/LOVABLE_INTEGRATION.md) for complete integration instructions.

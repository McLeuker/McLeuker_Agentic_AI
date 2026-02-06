# McLeuker AI Frontend

A modern, production-ready frontend for McLeuker AI - your intelligent assistant for fashion, beauty, skincare, and sustainability insights.

## Tech Stack

- **Framework:** Next.js 16 with App Router
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Icons:** Lucide React

## Features

- 🎨 Modern, responsive chat interface
- 💬 Real-time conversation with AI
- 📊 Rich response display (insights, sources, follow-up questions)
- 📱 Mobile-friendly design
- 🔄 Conversation history
- ⚡ Fast, optimized performance

## Getting Started

### Prerequisites

- Node.js 18+ or 20+
- pnpm (recommended) or npm

### Installation

```bash
# Clone the repository
git clone https://github.com/mcleuker/mcleuker-frontend.git
cd mcleuker-frontend

# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env.local

# Start development server
pnpm dev
```

### Environment Variables

Create a `.env.local` file with:

```env
# Backend API URL (Railway deployment)
NEXT_PUBLIC_API_URL=https://web-production-29f3c.up.railway.app
```

## Deployment to Vercel

### Option 1: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mcleuker/mcleuker-frontend)

### Option 2: Manual Deploy

1. Push this repository to GitHub
2. Go to [Vercel](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Add environment variable: `NEXT_PUBLIC_API_URL`
6. Click "Deploy"

### Custom Domain

After deployment:
1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add `mcleukerai.com`
4. Update DNS records as instructed

## Project Structure

```
src/
├── app/
│   ├── layout.tsx      # Root layout with metadata
│   ├── page.tsx        # Main chat page
│   └── globals.css     # Global styles
├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx   # Main chat area
│   │   ├── ChatInput.tsx       # Message input
│   │   └── MessageBubble.tsx   # Message display
│   └── layout/
│       ├── MainLayout.tsx      # App layout
│       └── Sidebar.tsx         # Navigation sidebar
├── lib/
│   └── api.ts          # API client & V5.1 parser
├── stores/
│   └── useStore.ts     # Zustand state management
└── types/
    └── index.ts        # TypeScript definitions
```

## API Integration

This frontend connects to the McLeuker AI V5.1 backend API, which provides:

- **Intent Detection:** Automatically categorizes queries
- **Real-time Research:** Searches and synthesizes information
- **Rich Responses:** Structured data with insights, sources, and recommendations
- **Follow-up Suggestions:** Contextual next questions

## Development

```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Lint code
pnpm lint
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

Built with ❤️ for McLeuker AI

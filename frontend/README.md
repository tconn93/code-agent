# AI Agent Platform - Frontend

React-based web interface for the AI Agent Platform.

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

## Environment Configuration

The frontend uses environment variables for configuration. Create a `.env` file from the example:

```bash
cp .env.example .env
```

### Environment Variables

- `VITE_API_URL` - Backend API URL
  - **Development**: `http://localhost:8000`
  - **Production**: Your production API URL

### How It Works

**Development Mode:**
- The frontend uses Vite's dev server proxy
- All `/api` requests are proxied to `VITE_API_URL`
- This avoids CORS issues during development
- Example: `GET /api/projects` → `http://localhost:8000/projects`

**Production Mode:**
- The frontend makes direct requests to `VITE_API_URL`
- Set `VITE_API_URL` to your production API endpoint before building

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── public/              # Static assets
│   └── vite.svg
├── src/
│   ├── assets/         # Images, fonts, etc.
│   ├── pages/          # Page components
│   │   ├── Projects.jsx    # Projects management
│   │   ├── Agents.jsx      # Agent management
│   │   ├── Jobs.jsx        # Job monitoring
│   │   └── Settings.jsx    # System settings
│   ├── App.jsx         # Main app component
│   ├── Layout.jsx      # Layout wrapper
│   ├── api.js          # API client
│   └── main.jsx        # Entry point
├── .env                # Environment variables (gitignored)
├── .env.example        # Environment template
├── index.html          # HTML template
├── package.json        # Dependencies
├── vite.config.js      # Vite configuration
└── eslint.config.js    # ESLint configuration
```

## API Integration

The frontend communicates with the backend API using Axios. All API calls are defined in `src/api.js`:

```javascript
import { getProjects, createProject } from './api';

// Get all projects
const projects = await getProjects();

// Create a project
const newProject = await createProject({
  name: 'My Project',
  description: 'Project description'
});
```

### Available API Methods

**Projects:**
- `getProjects()` - Get all projects
- `createProject(data)` - Create a new project

**Agents:**
- `getAgents()` - Get all agents
- `createAgent(data)` - Create a new agent

**Jobs:**
- `getAllJobs()` - Get all jobs
- `getJobs(projectId)` - Get jobs for a project
- `createJob(data)` - Create a new job
- `getJob(jobId)` - Get job details

**Settings:**
- `getSettings()` - Get all settings
- `saveSetting(data)` - Save a setting

## Development

### Adding a New Page

1. Create a new component in `src/pages/`:

```jsx
// src/pages/MyPage.jsx
import React from 'react';

function MyPage() {
  return (
    <div>
      <h1>My New Page</h1>
    </div>
  );
}

export default MyPage;
```

2. Add route in `src/App.jsx`:

```jsx
import MyPage from './pages/MyPage';

<Route path="mypage" element={<MyPage />} />
```

3. Add navigation link in `src/Layout.jsx` (if needed)

### Adding API Calls

Add new API methods to `src/api.js`:

```javascript
// Get something
export const getSomething = () => api.get('/something');

// Create something
export const createSomething = (data) => api.post('/something', data);
```

### Styling

The project uses Tailwind CSS. Add utility classes to components:

```jsx
<div className="bg-white rounded-lg shadow p-6">
  <h2 className="text-2xl font-bold mb-4">Title</h2>
  <p className="text-gray-600">Content</p>
</div>
```

## Building for Production

```bash
# Build the app
npm run build

# The output will be in the dist/ folder
# Serve it with any static file server
```

### Deployment Options

**Static Hosting (Netlify, Vercel, etc.):**
1. Set `VITE_API_URL` to your production API
2. Build: `npm run build`
3. Deploy the `dist/` folder

**Docker:**
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**With Backend:**
- Configure your backend to serve the built frontend from `dist/`
- Or use a reverse proxy (nginx, Caddy) to serve both

## Troubleshooting

### API calls failing

1. Check that the backend is running on `http://localhost:8000`
2. Verify `VITE_API_URL` in `.env`
3. Check browser console for CORS errors
4. Ensure the API endpoint paths are correct

### Development server won't start

1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
2. Check Node.js version: `node --version` (should be 18+)
3. Check for port conflicts (default: 5173)

### Build errors

1. Run linter: `npm run lint`
2. Check for TypeScript errors (if using TypeScript)
3. Ensure all dependencies are installed

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) in the project root.

## License

Same as the main project.

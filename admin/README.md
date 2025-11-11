# Restaurant Admin Panel

Modern admin panel built with React + TypeScript + Vite + TailwindCSS

## Features

- 🔐 **Authentication** - Secure login with JWT tokens
- 📊 **Dashboard** - Statistics and overview
- 📦 **Orders Management** - View, update status, see details
- 🍕 **Menu Management** - Add, edit, delete menu items
- 🏪 **Restaurant Info** - Update restaurant details
- ⭐ **Reviews** - View and moderate customer reviews
- 👥 **User Management** - Assign roles to users

## Getting Started

### Installation

```bash
cd E:\ippt\ippt_project\admin
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

## Tech Stack

- ⚛️ React 18
- 📘 TypeScript
- ⚡ Vite
- 🎨 TailwindCSS
- 🔗 React Router
- 🌐 Axios
- 🎯 Lucide Icons

## API Configuration

Backend API URL is configured in `src/api/client.ts`:
```typescript
const API_URL = 'http://localhost:8000';
```

Make sure your backend is running before starting the admin panel.

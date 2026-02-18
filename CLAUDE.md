# Go CRM

A comprehensive Customer Relationship Management system built with Django (backend) and Next.js (frontend).

## Project Overview

Go CRM is a full-stack application designed to manage contacts, tasks, communications, and AI-powered research. It provides a modern interface for lead management and includes automated research capabilities through the Super Researcher module.

## Tech Stack

### Backend
- **Framework**: Django REST Framework with Django Ninja
- **Language**: Python
- **Database**: PostgreSQL (configurable)
- **Task Queue**: Celery for async processing
- **AI Integration**: OpenAI GPT for lead generation and research
- **Vector Database**: Weaviate for research storage
- **Communication**: Django Email, SMS API

### Frontend
- **Framework**: Next.js 16.1.1 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **State Management**: React Context
- **UI Components**: Custom component library

## Architecture

### Backend Structure

The backend follows Django's app-based architecture with the following apps:

| App | Description |
|-----|-------------|
| `contacts` | Contact management, lead classification, and tracking |
| `super_researcher` | AI-powered lead generation and research engine |
| `todo` | Task and project management system |
| `user` | Custom user authentication and authorization |
| `communications` | Email and SMS communication tracking |
| `apex` | Additional research features |
| `core` | Django settings and configuration |

### Frontend Structure

The frontend uses Next.js App Router with a component-based architecture:

```
frontend/src/
├── app/              # Page routes and layouts
├── components/       # Reusable UI components
│   ├── auth/        # Authentication components
│   ├── contacts/    # Contact management components
│   ├── todos/       # Task management components
│   ├── communications/  # Communication components
│   ├── layout/      # Layout components (Header, Sidebar)
│   └── ui/          # Base UI components
└── lib/             # Utilities and type definitions
```

## API Endpoints

The backend exposes REST APIs through Django Ninja:

| Endpoint | Description |
|----------|-------------|
| `/api/contact/` | Contact CRUD operations |
| `/api/super_researcher/` | AI lead generation and research |
| `/api/todo/` | Task management |
| `/api/auth/` | User authentication |
| `/api/communications/` | Email and SMS operations |

## Lead Classification System

The CRM uses a comprehensive lead classification system:

- **New**: Newly created leads
- **Contacted**: Leads that have been reached out to
- **Growing Interest**: Leads showing increased engagement
- **Leading**: High-priority leads close to conversion
- **Converted**: Successfully converted customers
- **Dying**: Leads losing interest
- **Cold**: Inactive leads

## Key Features

1. **Contact Management**
   - Create, update, delete contacts
   - Lead classification tracking
   - Search and filter functionality
   - Inline editing capabilities

2. **AI-Powered Research** (Super Researcher)
   - Automated lead generation
   - Web search integration
   - Reliability scoring
   - Urgency analysis
   - Celery-based async processing

3. **Task Management**
   - Create and manage todos
   - Priority levels (low, medium, high)
   - Completion tracking
   - Statistics dashboard

4. **Communication**
   - Email sending and logging
   - SMS sending and logging
   - Communication history
   - Automatic lead status updates

5. **Authentication**
   - Custom user model
   - Session-based authentication
   - CSRF protection

## Development

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Key environment variables needed:

```env
# Backend
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/db
OPENAI_API_KEY=your-openai-key
WEAVIATE_API_KEY=your-weaviate-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Deployment

The project includes Docker configuration for containerized deployment:

```bash
docker-compose up
```

See `DEPLOYMENT.md` for detailed deployment instructions.

## Contributing

When contributing to this project:
1. Add Google-style docstrings to all new functions and classes
2. Follow the existing code structure and patterns
3. Use TypeScript for all new frontend components
4. Test API endpoints before submitting
5. Update documentation as needed

## License

[Add your license information here]

# Knowledge Base App - Project Summary

**Status:** ✅ Deployed to Production on Railway  
**Deployment URL:** https://knowledge-base-app-production.up.railway.app (or your Railway URL)  
**Last Updated:** December 3, 2025

---

## 🎯 What This App Does

A full-stack knowledge management system with RAG (Retrieval-Augmented Generation) powered chat:

- **User Authentication:** Session-based auth with secure cookies
- **Article Management:** Full CRUD operations (Create, Read, Update, Delete)
- **Tag System:** Organize articles with tags, filter by tags
- **RAG Chat:** Ask questions and get answers from your knowledge base using Azure OpenAI
- **Vector Search:** Semantic search across articles using embeddings
- **Modern UI:** HTMX-powered frontend with Tailwind CSS

---

## 🏗️ Technical Architecture

### **Backend**
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL (production) / SQLite (local dev)
- **ORM:** SQLAlchemy with Alembic migrations
- **Auth:** Session-based with cookies (not JWT)
- **AI/ML:** 
  - Azure OpenAI for embeddings (text-embedding-ada-002)
  - Azure OpenAI for chat (GPT-4)
  - ChromaDB for vector storage
- **Validation:** Pydantic schemas

### **Frontend**
- **Templates:** Jinja2
- **Interactivity:** HTMX 1.9.10
- **Styling:** Tailwind CSS (CDN)
- **JavaScript:** Vanilla JS for complex interactions (chat, modals, search)

### **Deployment**
- **Platform:** Railway
- **Container:** Docker (Python 3.11-slim base)
- **Database:** Railway PostgreSQL (auto-provisioned)
- **Environment:** Production with environment variables

---

## 📁 Project Structure

```
knowledge_base_app/
├── api/                  # API routes
│   ├── articles.py       # Article CRUD endpoints
│   ├── auth.py           # Authentication (signup, login, logout)
│   ├── chat.py           # RAG chat endpoints
│   ├── comments.py       # Comment functionality
│   ├── users.py          # User management
│   └── views.py          # HTML template routes (HTMX pages)
├── core/                 # Core utilities
│   ├── deps.py           # Dependency injection (services, auth)
│   └── security.py       # Password hashing
├── db/                   # Database configuration
│   └── session.py        # DB connection (SQLite/PostgreSQL)
├── models/               # SQLAlchemy ORM models
├── repositories/         # Data access layer
├── schemas/              # Pydantic validation schemas
├── services/             # Business logic
│   ├── embedding.py      # Azure OpenAI embeddings
│   ├── search.py         # Vector search with ChromaDB
│   └── chat.py           # RAG chat service
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with Tailwind/HTMX
│   ├── login.html        # Login page
│   ├── signup.html       # Signup page
│   ├── articles.html     # Articles browser with CRUD modals
│   └── chat.html         # RAG chat interface
├── tests/                # Pytest test suite (36 tests)
├── alembic/              # Database migrations
├── Dockerfile            # Docker container definition
├── requirements.txt      # Python dependencies
└── main.py               # FastAPI app entry point
```

---

## 🚀 Key Features Implemented

### **1. Authentication System**
- Session-based auth with secure cookies
- Password hashing with bcrypt
- Login/signup pages with HTMX form submission
- Session expiry (7 days)
- Logout functionality

### **2. Article Management**
- Create, read, update, delete articles
- Author ownership (only author/admin can edit/delete)
- Tag system for categorization
- Search functionality (title, content, tags)
- Full-text preview in list view
- Modal-based UI for create/edit/view

### **3. RAG Chat System**
- Chat with your knowledge base
- Session-based chat history
- Vector similarity search for context retrieval
- Azure OpenAI integration for responses
- Display of source articles used for answers
- Real-time message streaming

### **4. UI/UX**
- Dark theme with Tailwind CSS
- Responsive design
- Modal overlays for article operations
- Client-side search filtering
- Click-outside-to-close modals
- Loading states during API calls

---

## 🔧 Configuration & Environment Variables

### **Required Environment Variables (Railway)**
```bash
# Database (auto-set by Railway)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Application
SECRET_KEY=your-secret-key-for-sessions
ENVIRONMENT=production
```

### **Local Development (.env)**
```bash
# No DATABASE_URL = uses SQLite (test.db)
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
SECRET_KEY=local-dev-secret
ENVIRONMENT=development
```

---

## 🐛 Issues Resolved During Development

### **1. Deployment: Module Import Errors**
**Problem:** `ModuleNotFoundError: No module named 'knowledge_base_app'`  
**Root Cause:** Project structure wasn't recognized as a Python package by Railway  
**Solution:** 
- Changed Dockerfile to run from parent directory
- Used `uvicorn knowledge_base_app.main:app` instead of `main:app`
- Set `WORKDIR /workspace` and copy code to `knowledge_base_app/` subdirectory

### **2. Relative Imports Failing**
**Problem:** `ImportError: attempted relative import with no known parent package`  
**Root Cause:** Running `main.py` as a script vs as a module  
**Solution:** Keep relative imports, but run uvicorn with full module path from parent directory

### **3. Timezone Comparison Error**
**Problem:** `TypeError: can't compare offset-naive and offset-aware datetimes`  
**Root Cause:** SQLite returns naive datetimes, PostgreSQL returns aware datetimes  
**Solution:** Changed `datetime.utcnow()` to `datetime.now(timezone.utc)` throughout codebase

### **4. Cookie Not Set on Login**
**Problem:** Login succeeded but session cookie wasn't sent to browser  
**Root Cause:** Created `JSONResponse` without setting cookie on the response object  
**Solution:** Create response first, call `.set_cookie()` on it, then return

### **5. HTMX Form Encoding**
**Problem:** 422 Unprocessable Entity on form submissions  
**Root Cause:** HTMX sends form-encoded data by default, FastAPI expected JSON  
**Solution:** Created separate `/form/*` endpoints accepting `Form()` parameters

---

## 📊 Current State

### **What Works**
- ✅ User signup, login, logout
- ✅ Create, read, update, delete articles
- ✅ Tag-based organization and filtering
- ✅ Search across articles
- ✅ RAG-powered chat with context retrieval
- ✅ Session management with 7-day expiry
- ✅ Author-based permissions (edit/delete)
- ✅ Deployed on Railway with PostgreSQL
- ✅ Docker containerization
- ✅ 36 passing tests

### **Known Limitations**
- ⚠️ Uses `alert()` for notifications (should use toast notifications)
- ⚠️ No inline form validation (only alerts)
- ⚠️ Forms don't auto-clear after submission
- ⚠️ No loading spinners during API calls
- ⚠️ No ESC key handler for modals
- ⚠️ No markdown rendering for article content
- ⚠️ No user profile page
- ⚠️ No article versioning/history
- ⚠️ No file upload support

---

## 🎓 Learning Outcomes & Key Concepts

### **Backend Patterns**
- **Repository Pattern:** Data access layer separation
- **Service Layer:** Business logic isolation
- **Dependency Injection:** FastAPI's `Depends()` for service instantiation
- **Session Management:** Custom session table instead of JWT
- **Alembic Migrations:** Database schema versioning

### **Frontend Patterns**
- **HTMX:** Declarative AJAX with `hx-` attributes
- **Template Inheritance:** Jinja2 `{% extends %}` and `{% block %}`
- **Modal Management:** JavaScript state tracking (`currentArticleId`)
- **Client-Side Filtering:** Array methods (`.filter()`, `.map()`, `.some()`)
- **Defensive Coding:** `tag.name || tag` for flexible type handling

### **JavaScript Concepts**
- **`async/await`:** Modern promise handling
- **Optional Chaining (`?.`):** Safe property access
- **Template Literals:** String interpolation with backticks
- **Event Bubbling:** Click-outside-to-close pattern
- **`this` vs `event.target`:** Context in onclick handlers

### **Docker & Deployment**
- **Multi-stage awareness:** Requirements before code (layer caching)
- **Working directory context:** How `WORKDIR` affects imports
- **Environment variables:** Runtime configuration
- **Railway specifics:** Procfile vs Dockerfile priority

### **Database Differences**
- **SQLite vs PostgreSQL:** Timezone handling differences
- **Connection strings:** `sqlite:///` vs `postgresql://`
- **Type awareness:** Naive vs aware datetime objects

---

## 🔮 Future Improvement Ideas

### **High Priority (Polish)**
1. Replace `alert()` with toast notifications (e.g., Toastify)
2. Add loading spinners to all async operations
3. Implement inline form validation with error messages
4. Auto-clear forms after successful submission
5. Add ESC key handler to close modals
6. Form field validation feedback (red borders, etc.)

### **Medium Priority (Features)**
1. Markdown rendering for article content (with syntax highlighting)
2. Rich text editor (TinyMCE or SimpleMDE)
3. User profile page with avatar upload
4. Article bookmarks/favorites
5. Export articles as PDF
6. Share links with OpenGraph preview cards
7. Article versioning/history tracking
8. Bulk operations (multi-select delete)

### **Low Priority (Advanced)**
1. Real-time collaboration (WebSockets)
2. Article categories/folders
3. Advanced search filters (date range, author)
4. Analytics dashboard (views, popular articles)
5. API rate limiting
6. Redis caching for search results
7. Elasticsearch for full-text search
8. Image upload and hosting

---

## 🛠️ How to Run Locally

```bash
# Clone and navigate
cd /home/ubuntu/dev/learn/ai-dev/knowledge_base_app

# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Run migrations (creates SQLite DB)
alembic upgrade head

# Start server (from parent directory!)
cd ..
uvicorn knowledge_base_app.main:app --reload

# Visit: http://localhost:8000
```

---

## 🐳 Docker Build & Run

```bash
# Build image
docker build -t knowledge-base-app .

# Run container
docker run -p 8000:8000 \
  -e AZURE_OPENAI_API_KEY=your_key \
  -e AZURE_OPENAI_ENDPOINT=your_endpoint \
  knowledge-base-app

# Visit: http://localhost:8000
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=knowledge_base_app --cov-report=html

# Run specific test file
pytest tests/test_articles.py

# Current status: 36 tests passing ✅
```

---

## 📝 Git Repository

**Repo:** https://github.com/tommy2k0/knowledge_base_app  
**Branch:** main  
**Key commits:**
- Initial backend implementation
- HTMX frontend development
- Docker containerization
- Railway deployment fixes
- Timezone bug fixes

---

## 🎯 Quick Reference

### **API Endpoints**
```
POST   /api/v1/signup          - Create new user
POST   /api/v1/login           - Login user
POST   /api/v1/logout          - Logout user
GET    /api/v1/me              - Get current user

GET    /api/v1/articles        - List articles
POST   /api/v1/articles        - Create article
GET    /api/v1/articles/{id}   - Get article
PUT    /api/v1/articles/{id}   - Update article
DELETE /api/v1/articles/{id}   - Delete article
GET    /api/v1/articles/search - Semantic search

GET    /api/v1/chat/sessions   - List chat sessions
POST   /api/v1/chat/sessions   - Create session
POST   /api/v1/chat/message    - Send chat message
```

### **HTML Routes**
```
GET / or /login     - Login page
GET /signup         - Signup page
GET /chat           - Chat interface
GET /articles       - Articles browser
```

---

## 👥 Credits & Technologies

**Built with:**
- FastAPI (backend framework)
- HTMX (frontend interactivity)
- Tailwind CSS (styling)
- SQLAlchemy (ORM)
- Azure OpenAI (embeddings & chat)
- ChromaDB (vector database)
- Railway (deployment)
- Docker (containerization)

**Developed:** November-December 2025  
**Developer:** tommy2k0  
**Learning Mode:** Challenge-first approach (70% doing, 20% guided, 10% theory)

---

## 📌 Notes for Future Sessions

1. **Remember to run from parent directory:** `uvicorn knowledge_base_app.main:app --reload`
2. **Timezone fix applied:** All `datetime.utcnow()` changed to `datetime.now(timezone.utc)`
3. **Railway auto-deploys on push to main**
4. **Tests use SQLite, production uses PostgreSQL**
5. **Azure OpenAI keys are in Railway environment variables**
6. **Docker build context is important:** Copy to subdirectory, run from parent

---

**Ready to pick up where you left off!** 🚀

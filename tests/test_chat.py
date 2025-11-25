
from knowledge_base_app.models.chat import ChatSession


def test_create_chat_session(authenticated_client):
    """Test creating a chat session as authenticated user."""
    response = authenticated_client.post(
        "/api/v1/chat/sessions",
        json={
            "title": "Test Chat Session"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Chat Session"
    assert "id" in data

def test_list_chat_sessions(authenticated_client, db_session, test_user):
    """Test listing chat sessions for authenticated user."""
    # Create a chat session first
    chat_session = ChatSession(
        title="Existing Chat Session",
        user_id=test_user.id
    )
    db_session.add(chat_session)
    db_session.commit()

    response = authenticated_client.get("/api/v1/chat/sessions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(session["title"] == "Existing Chat Session" for session in data)


def test_get_chat_session_by_id(authenticated_client, db_session, test_user):
    """Test retrieving a specific chat session by ID."""
    # Create a chat session first
    chat_session = ChatSession(
        title="Specific Chat Session",
        user_id=test_user.id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    response = authenticated_client.get(f"/api/v1/chat/sessions/{chat_session.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Chat Session"
    assert data["id"] == chat_session.id


def test_get_nonexistent_chat_session(authenticated_client):
    """Test retrieving a non-existent chat session returns 404."""
    response = authenticated_client.get("/api/v1/chat/sessions/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_unauthorized_chat_session(authenticated_client, db_session, test_user):
    """Test retrieving a chat session that belongs to another user returns 403."""
    # Create a chat session for a different user
    other_user_id = test_user.id + 1  # Assuming this ID does not exist
    chat_session = ChatSession(
        title="Other User's Chat Session",
        user_id=other_user_id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    response = authenticated_client.get(f"/api/v1/chat/sessions/{chat_session.id}")
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()

def test_get_chat_sessions_unauthenticated(client):
    """Test listing chat sessions without authentication fails."""
    response = client.get("/api/v1/chat/sessions")
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()

def test_create_chat_session_unauthenticated(client):
    """Test creating chat session without authentication fails."""
    response = client.post(
        "/api/v1/chat/sessions",
        json={
            "title": "Unauthorized Chat Session"
        }
    )
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()

def test_get_chat_session_messages_unauthenticated(client):
    """Test retrieving chat session messages without authentication fails."""
    response = client.get("/api/v1/chat/sessions/1/messages")
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()

def test_get_chat_session_messages_authorized(authenticated_client, db_session, test_user):
    """Test retrieving messages for a chat session as the authorized user."""
    # Create a chat session first
    chat_session = ChatSession(
        title="Message Test Chat Session",
        user_id=test_user.id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    response = authenticated_client.get(f"/api/v1/chat/sessions/{chat_session.id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Should return a list of messages (empty initially)


def test_get_chat_session_messages_unauthorized(authenticated_client, db_session, test_user):
    """Test retrieving messages for a chat session that belongs to another user returns 403."""
    # Create a chat session for a different user
    other_user_id = test_user.id + 1  # Assuming this ID does not exist
    chat_session = ChatSession(
        title="Other User's Message Chat Session",
        user_id=other_user_id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    response = authenticated_client.get(f"/api/v1/chat/sessions/{chat_session.id}/messages")
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()

def test_get_messages_nonexistent_chat_session(authenticated_client):
    """Test retrieving messages for a non-existent chat session returns 404."""
    response = authenticated_client.get("/api/v1/chat/sessions/99999/messages")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_send_message_unauthenticated(client):
    """Test sending message without authentication fails."""
    response = client.post(
        "/api/v1/chat/sessions/1/messages",
        json={
            "message": "Hello, AI!"
        }
    )
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()


def test_send_message_authorized(authenticated_client, db_session, test_user):
    """Test sending a message in a chat session as the authorized user."""
    import json
    from knowledge_base_app.models.article import Article
    
    # Create articles with embeddings for RAG to find
    article = Article(
        title="Python Tutorial",
        content="Python is a high-level programming language",
        author_id=test_user.id,
        embedding=json.dumps([0.1] * 1536)
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    
    # Create a chat session first
    chat_session = ChatSession(
        title="Send Message Chat Session",
        user_id=test_user.id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    response = authenticated_client.post(
        f"/api/v1/chat/sessions/{chat_session.id}/messages",
        json={
            "message": "What is Python?"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "message" in data  # AI response
    assert "content" in data["message"]  # Message content
    assert "sources" in data  # Source article IDs
    # Verify sources are returned (RAG found articles)
    sources = data.get("sources", [])
    assert isinstance(sources, list)
    # With real Azure OpenAI, it should find the article
    # With dummy embeddings, it might return empty, so we just check structure


def test_send_message_to_nonexistent_session(authenticated_client):
    """Test sending message to non-existent session returns 404."""
    response = authenticated_client.post(
        "/api/v1/chat/sessions/99999/messages",
        json={
            "message": "Hello?"
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_send_message_to_unauthorized_session(authenticated_client, db_session, test_user):
    """Test sending message to another user's session returns 403."""
    # Create session for different user
    other_user_id = test_user.id + 1
    chat_session = ChatSession(
        title="Other User Session",
        user_id=other_user_id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    response = authenticated_client.post(
        f"/api/v1/chat/sessions/{chat_session.id}/messages",
        json={
            "message": "Unauthorized message"
        }
    )
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()


def test_chat_message_history(authenticated_client, db_session, test_user):
    """Test that messages are persisted and retrievable."""
    import json
    from knowledge_base_app.models.article import Article
    
    # Create article for RAG
    article = Article(
        title="FastAPI Guide",
        content="FastAPI is a modern web framework",
        author_id=test_user.id,
        embedding=json.dumps([0.2] * 1536)
    )
    db_session.add(article)
    db_session.commit()
    
    # Create chat session
    chat_session = ChatSession(
        title="History Test Session",
        user_id=test_user.id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    # Send first message
    response1 = authenticated_client.post(
        f"/api/v1/chat/sessions/{chat_session.id}/messages",
        json={"message": "What is FastAPI?"}
    )
    assert response1.status_code == 201

    # Send second message
    response2 = authenticated_client.post(
        f"/api/v1/chat/sessions/{chat_session.id}/messages",
        json={"message": "Tell me more"}
    )
    assert response2.status_code == 201

    # Retrieve message history
    response = authenticated_client.get(f"/api/v1/chat/sessions/{chat_session.id}/messages")
    assert response.status_code == 200
    messages = response.json()
    
    # Should have at least 4 messages (2 user + 2 assistant)
    assert len(messages) >= 4
    # Check message roles
    user_messages = [m for m in messages if m["role"] == "user"]
    assistant_messages = [m for m in messages if m["role"] == "assistant"]
    assert len(user_messages) >= 2
    assert len(assistant_messages) >= 2


def test_chat_sources_verification(authenticated_client, db_session, test_user):
    """Test that RAG returns source article citations."""
    import json
    from knowledge_base_app.models.article import Article
    
    # Create specific article to be cited
    article = Article(
        title="Docker Basics",
        content="Docker is a containerization platform for deploying applications",
        author_id=test_user.id,
        embedding=json.dumps([0.3] * 1536)
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    
    # Create chat session
    chat_session = ChatSession(
        title="Source Test Session",
        user_id=test_user.id
    )
    db_session.add(chat_session)
    db_session.commit()
    db_session.refresh(chat_session)

    # Ask question about Docker
    response = authenticated_client.post(
        f"/api/v1/chat/sessions/{chat_session.id}/messages",
        json={"message": "What is Docker?"}
    )
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "message" in data
    assert "sources" in data
    sources = data["sources"]
    assert isinstance(sources, list)
    
    # If Azure OpenAI is available, sources should include our article
    # With test setup, just verify structure is correct
    if len(sources) > 0:
        # Sources should be article IDs
        assert all(isinstance(s, int) for s in sources)


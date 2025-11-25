from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas.comment import CommentCreate, CommentRead, CommentReplyCreate, CommentReplyRead
from ..repositories.comment import CommentRepository
from ..services.comment import CommentService
from ..models.user import User
from ..core.deps import require_role, get_current_user, get_comment_service

router = APIRouter()


@router.post("/comments", response_model=CommentRead)
def create_comment(comment: CommentCreate, service: CommentService = Depends(get_comment_service), current_user = Depends(get_current_user)):
    author_id = current_user.id
    return service.create_comment(comment, author_id)

@router.get("/comments/{comment_id}", response_model=CommentRead)
def get_comment(comment_id: int, service: CommentService = Depends(get_comment_service)):
    db_comment = service.get_comment(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.get("/articles/{article_id}/comments", response_model=list[CommentRead])
def list_comments(article_id: int, skip: int = 0, limit: int = 10, service: CommentService = Depends(get_comment_service)):
    return service.list_comments(article_id, skip=skip, limit=limit)

@router.put("/comments/{comment_id}", response_model=CommentRead)
def update_comment(comment_id: int, comment: CommentCreate, service: CommentService = Depends(get_comment_service), current_user = Depends(get_current_user)):
    db_comment = service.get_comment(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    updated_comment = service.update_comment(comment_id, comment.content)
    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return updated_comment

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, service: CommentService = Depends(get_comment_service), current_user = Depends(get_current_user)):
    db_comment = service.get_comment(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    success = service.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return None

@router.get("/comments/{comment_id}/replies", response_model=list[CommentReplyRead])
def list_comment_replies(comment_id: int, skip: int = 0, limit: int = 10,service: CommentService = Depends(get_comment_service)):
    db_comment = service.get_comment(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return service.list_replies(comment_id, skip=skip, limit=limit)

@router.post("/comments/{comment_id}/replies", response_model=CommentReplyRead)
def create_comment_reply(comment_id: int, reply: CommentReplyCreate, service: CommentService = Depends(get_comment_service), current_user = Depends(get_current_user)):
    db_comment = service.get_comment(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return service.create_reply(comment_id, reply, current_user.id)

@router.get("/comments/replies/{reply_id}", response_model=CommentReplyRead)
def get_comment_reply(reply_id: int, service: CommentService = Depends(get_comment_service)):
    db_reply = service.get_reply(reply_id)
    if not db_reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    return db_reply

@router.delete("/comments/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_reply(reply_id: int, service: CommentService = Depends(get_comment_service), current_user = Depends(get_current_user)):
    db_reply = service.get_reply(reply_id)
    if not db_reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    if db_reply.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this reply")
    success = service.delete_reply(reply_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reply not found")
    return None

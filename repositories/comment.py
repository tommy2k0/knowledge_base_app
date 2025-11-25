from sqlalchemy.orm import Session
from ..models.comment import Comment, CommentReply
from ..schemas.comment import CommentCreate, CommentReplyCreate


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, comment_id: int) -> Comment | None:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()
    
    def create(self, comment: CommentCreate, author_id: int) -> Comment:
        db_comment = Comment(
            content=comment.content,
            article_id=comment.article_id,
            author_id=author_id
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment

    def list_comments(self, article_id: int, skip: int = 0, limit: int = 10) -> list[Comment]:
        query = self.db.query(Comment).filter(Comment.article_id == article_id)
        return query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(self, comment_id: int, content: str) -> Comment | None:
        db_comment = self.get(comment_id)
        if not db_comment:
            return None
        db_comment.content = content
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def delete(self, comment_id: int) -> bool:
        db_comment = self.get(comment_id)
        if not db_comment:
            return False
        self.db.delete(db_comment)
        self.db.commit()
        return True

    def list_replies(self, comment_id: int, skip: int = 0, limit: int = 10) -> list[CommentReply]:
        db_comment = self.get(comment_id)
        if not db_comment:
            return []
        return db_comment.replies.order_by(CommentReply.created_at.asc()).offset(skip).limit(limit).all()

    def get_reply(self, reply_id: int) -> CommentReply | None:
        return self.db.query(CommentReply).filter(CommentReply.id == reply_id).first()
    
    def create_reply(self, comment_id: int, reply: CommentReplyCreate, author_id: int) -> CommentReply | None:
        db_comment = self.get(comment_id)
        if not db_comment:
            return None
        db_reply = CommentReply(
            content=reply.content,
            author_id=author_id,
            comment_id=db_comment.id
        )
        self.db.add(db_reply)
        self.db.commit()
        self.db.refresh(db_reply)
        return db_reply
    
    def delete_reply(self, reply_id: int) -> bool:
        db_reply = self.db.query(CommentReply).filter(CommentReply.id == reply_id).first()
        if not db_reply:
            return False
        self.db.delete(db_reply)
        self.db.commit()
        return True
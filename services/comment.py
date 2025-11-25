from ..repositories.comment import CommentRepository
from ..schemas.comment import CommentCreate
from ..models.comment import Comment, CommentReply

class CommentService:
    def __init__(self, repo: CommentRepository):
        self.repo = repo

    def create_comment(self, comment: CommentCreate, author_id: int) -> Comment:
        return self.repo.create(comment, author_id)

    def get_comment(self, comment_id: int) -> Comment | None:
        return self.repo.get(comment_id)

    def list_comments(self, article_id: int, skip: int = 0, limit: int = 10) -> list[Comment]:
        return self.repo.list_comments(article_id, skip, limit)

    def update_comment(self, comment_id: int, content: str) -> Comment | None:
        return self.repo.update(comment_id, content)

    def delete_comment(self, comment_id: int) -> bool:
        return self.repo.delete(comment_id)
    
    def list_replies(self, comment_id: int) -> list[CommentReply]:
        return self.repo.list_replies(comment_id)
    
    def create_reply(self, comment_id: int, content: str, author_id: int) -> CommentReply | None:
        return self.repo.create_reply(comment_id, content, author_id)
    
    def get_reply(self, reply_id: int) -> CommentReply | None:
        return self.repo.get_reply(reply_id)
    
    def update_reply(self, reply_id: int, content: str) -> CommentReply | None:
        return self.repo.update_reply(reply_id, content)

    def delete_reply(self, reply_id: int) -> bool:
        return self.repo.delete_reply(reply_id)
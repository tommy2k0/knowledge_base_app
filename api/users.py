from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, UserRead, UserRoleUpdate
from ..repositories.user import UserRepository
from ..services.user import UserService
from ..core.deps import get_user_service, require_role
from ..models.user import User

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 10, service: UserService = Depends(get_user_service)):
    return service.list_users(skip=skip, limit=limit)

@router.get("/admin/users", response_model=list[UserRead])
def admin_list_users(skip: int = 0, limit: int = 10, current_user: User = Depends(require_role("admin")), service: UserService = Depends(get_user_service)):
    return service.list_users(skip=skip, limit=limit)

@router.patch("/users/{user_id}/role", response_model=UserRead)
def update_user_role(user_id: int, role_update: UserRoleUpdate, current_user: User = Depends(require_role("admin")), service: UserService = Depends(get_user_service)):
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return service.update_user_role(user_id, role_update.role.value)
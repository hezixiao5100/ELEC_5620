"""
Admin API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
import json
import glob

from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.auth_service import AuthService, get_auth_service, get_current_active_user, require_admin
from app.models.user import User as UserModel
from app.models.stock import Stock
from app.models.alert import Alert
from app.models.portfolio import Portfolio

class UserStatusUpdate(BaseModel):
    """Schema for updating user status"""
    is_active: bool

router = APIRouter()

@router.get("/dashboard")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get admin dashboard statistics
    """
    try:
        # Count users by role
        total_users = db.query(UserModel).count()
        total_investors = db.query(UserModel).filter(UserModel.role == "INVESTOR").count()
        total_advisors = db.query(UserModel).filter(UserModel.role == "ADVISOR").count()
        total_admins = db.query(UserModel).filter(UserModel.role == "ADMIN").count()
        
        # Count stocks
        total_stocks = db.query(Stock).count()
        
        # Count alerts
        total_alerts = db.query(Alert).count()
        alerts_today = db.query(Alert).filter(
            Alert.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # Count portfolios
        total_portfolios = db.query(Portfolio).count()
        
        return {
            "total_users": total_users,
            "total_investors": total_investors,
            "total_advisors": total_advisors,
            "total_admins": total_admins,
            "total_stocks": total_stocks,
            "total_alerts": total_alerts,
            "alerts_today": alerts_today,
            "total_portfolios": total_portfolios,
            "system_health": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard data: {str(e)}")

@router.get("/users", response_model=List[User])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get all users (admin only)
    """
    try:
        users = db.query(UserModel).all()
        return [
            User(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                alert_threshold=user.alert_threshold,
                is_active=user.is_active == "Y",
                created_at=user.created_at,
                last_login=user.last_login
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Create a new user (admin only)
    """
    try:
        # Check if user already exists
        existing_user = db.query(UserModel).filter(
            (UserModel.username == user_data.username) | (UserModel.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Create new user
        hashed_password = auth_service.get_password_hash(user_data.password)
        new_user = UserModel(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
            alert_threshold=user_data.alert_threshold,
            is_active="Y"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return User(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            role=new_user.role,
            alert_threshold=new_user.alert_threshold,
            is_active=new_user.is_active == "Y",
            created_at=new_user.created_at,
            last_login=new_user.last_login
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Update user information (admin only)
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if user_data.username is not None:
            # Check if new username is taken
            existing = db.query(UserModel).filter(
                UserModel.username == user_data.username,
                UserModel.id != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = user_data.username
        
        if user_data.email is not None:
            # Check if new email is taken
            existing = db.query(UserModel).filter(
                UserModel.email == user_data.email,
                UserModel.id != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = user_data.email
        
        if user_data.alert_threshold is not None:
            user.alert_threshold = user_data.alert_threshold
        
        db.commit()
        db.refresh(user)
        
        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            alert_threshold=user.alert_threshold,
            is_active=user.is_active == "Y",
            created_at=user.created_at,
            last_login=user.last_login
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to update user: {str(e)}")

@router.put("/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Toggle user active status (admin only)
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        is_active = status_data.is_active
        
        # Prevent admin from deactivating themselves
        if user_id == current_user.id and not is_active:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate yourself"
            )
        
        user.is_active = "Y" if is_active else "N"
        db.commit()
        
        return {"message": f"User {'activated' if is_active else 'deactivated'} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to update user status: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Delete a user (admin only)
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent admin from deleting themselves
        if user_id == current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete yourself"
            )
        
        db.delete(user)
        db.commit()
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to delete user: {str(e)}")

@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get detailed system statistics
    """
    try:
        # User statistics
        total_users = db.query(UserModel).count()
        active_users = db.query(UserModel).filter(UserModel.is_active == "Y").count()
        users_by_role = {
            role.value: db.query(UserModel).filter(UserModel.role == role).count()
            for role in UserModel.role.property.columns[0].type.enum_class
        }
        
        # Stock statistics
        total_stocks = db.query(Stock).count()
        active_stocks = db.query(Stock).filter(Stock.is_active == "Y").count()
        
        # Alert statistics
        from app.models.alert import AlertStatus
        total_alerts = db.query(Alert).count()
        alerts_by_status = {}
        for status in [AlertStatus.PENDING, AlertStatus.TRIGGERED, AlertStatus.ACKNOWLEDGED, AlertStatus.EXPIRED]:
            alerts_by_status[status.value] = db.query(Alert).filter(
                Alert.status == status
            ).count()
        
        # Portfolio statistics
        total_portfolios = db.query(Portfolio).count()
        unique_portfolio_users = db.query(func.count(func.distinct(Portfolio.user_id))).scalar()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "by_role": users_by_role
            },
            "stocks": {
                "total": total_stocks,
                "active": active_stocks
            },
            "alerts": {
                "total": total_alerts,
                "by_status": alerts_by_status
            },
            "portfolios": {
                "total": total_portfolios,
                "unique_users": unique_portfolio_users
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

@router.get("/logs")
async def get_system_logs(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """
    Get system logs (admin only)
    """
    try:
        # Find log files
        log_dir = "logs"
        if not os.path.exists(log_dir):
            log_dir = "stock-analysis-system/logs"
        
        if not os.path.exists(log_dir):
            return {
                "total": 0,
                "limit": limit,
                "offset": offset,
                "logs": []
            }
        
        # Get all log files (current + rotated)
        log_files = sorted(glob.glob(os.path.join(log_dir, "*.log*")), reverse=True)
        
        logs = []
        
        # Read from log files (most recent first)
        for log_file in log_files:
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            # Try to parse as JSON (structured logging)
                            log_entry = json.loads(line)
                            log_level = log_entry.get("level", "").upper()
                            
                            # Apply filters
                            if level and log_level != level.upper():
                                continue
                            if search and search.lower() not in line.lower():
                                continue
                            
                            logs.append({
                                "timestamp": log_entry.get("timestamp", ""),
                                "level": log_entry.get("level", "INFO"),
                                "logger": log_entry.get("logger", ""),
                                "message": log_entry.get("message", ""),
                                "module": log_entry.get("module", ""),
                                "function": log_entry.get("function", ""),
                                "line": log_entry.get("line", 0),
                                "raw": line
                            })
                        except json.JSONDecodeError:
                            # Handle plain text logs
                            if search and search.lower() not in line.lower():
                                continue
                            logs.append({
                                "timestamp": datetime.utcnow().isoformat(),
                                "level": "INFO",
                                "logger": "system",
                                "message": line,
                                "module": "",
                                "function": "",
                                "line": 0,
                                "raw": line
                            })
            except Exception as e:
                continue
            
            # Stop if we have enough logs
            if len(logs) >= (offset + limit) * 2:  # Get extra for filtering
                break
        
        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply pagination
        total = len(logs)
        paginated_logs = logs[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": paginated_logs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")

@router.get("/tasks/list")
async def get_task_list(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get list of background tasks (admin only)
    """
    try:
        from app.celery_app import celery_app
        
        inspect = celery_app.control.inspect()
        
        # Get task information
        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}
        registered = inspect.registered() or {}
        
        # Get all worker names
        all_workers = set(active.keys()) | set(scheduled.keys()) | set(reserved.keys())
        
        tasks = []
        for worker in all_workers:
            worker_tasks = []
            
            # Active tasks
            for task in active.get(worker, []):
                worker_tasks.append({
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "state": "ACTIVE",
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {}),
                    "worker": worker,
                    "time_start": task.get("time_start")
                })
            
            # Scheduled tasks
            for task in scheduled.get(worker, []):
                worker_tasks.append({
                    "id": task.get("request", {}).get("id"),
                    "name": task.get("request", {}).get("task"),
                    "state": "SCHEDULED",
                    "args": task.get("request", {}).get("args", []),
                    "kwargs": task.get("request", {}).get("kwargs", {}),
                    "worker": worker,
                    "eta": task.get("eta")
                })
            
            # Reserved tasks
            for task in reserved.get(worker, []):
                worker_tasks.append({
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "state": "RESERVED",
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {}),
                    "worker": worker
                })
            
            tasks.extend(worker_tasks)
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "workers": list(all_workers),
            "registered_tasks": list(set(sum(registered.values(), []))) if registered else []
        }
    except Exception as e:
        # If Celery is not available, return empty result
        return {
            "tasks": [],
            "total": 0,
            "workers": [],
            "registered_tasks": [],
            "error": str(e)
        }

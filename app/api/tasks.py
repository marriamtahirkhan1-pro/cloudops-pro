from fastapi import APIRouter, HTTPException, Query

from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["Tasks"],
)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate):
    return task_service.create_task(data)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return task_service.get_tasks(limit, offset)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = task_service.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate):
    required_fields = ("title", "status", "priority")

    for field in required_fields:
        if field in data.model_fields_set:
            if getattr(data, field) is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"{field} cannot be null",
                )

    task = task_service.update_task(task_id, data)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    deleted = task_service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )


from app.db.connection import get_connection


def create_task(data):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, description, priority)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (data.title, data.description, data.priority.value),
            )
            return cur.fetchone()


def get_tasks(limit=20, offset=0):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM tasks
                ORDER BY created_at DESC, id DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            return cur.fetchall()


def get_task(task_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM tasks WHERE id = %s",
                (task_id,),
            )
            return cur.fetchone()


def update_task(task_id, data):
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        return get_task(task_id)

    allowed = {"title", "description", "status", "priority"}
    changes = {k: v for k, v in changes.items() if k in allowed}

    if not changes:
        return get_task(task_id)

    for key in ("status", "priority"):
        if key in changes and changes[key] is not None:
            changes[key] = changes[key].value

    from psycopg import sql

    assignments = [
        sql.SQL("{} = %s").format(sql.Identifier(key))
        for key in changes
    ]

    query = sql.SQL(
        "UPDATE tasks SET {}, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = %s RETURNING *"
    ).format(sql.SQL(", ").join(assignments))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, [*changes.values(), task_id])
            return cur.fetchone()


def delete_task(task_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id",
                (task_id,),
            )
            return cur.fetchone() is not None


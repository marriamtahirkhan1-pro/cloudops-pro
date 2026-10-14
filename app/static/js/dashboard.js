
"use strict";

const API_BASE = "/api/v1/tasks";

let editingTaskId = null;
let isSaving = false;

const $ = (id) => document.getElementById(id);

const taskForm = $("task-form");
const newTaskBtn = $("new-task-btn");
const cancelTaskBtn = $("cancel-task-btn");
const taskFormError = $("task-form-error");
const submitBtn = taskForm.querySelector('[type="submit"]');

function resetTaskForm() {
  editingTaskId = null;
  taskForm.reset();
  taskForm.hidden = true;
  $("task-status-group").hidden = true;
  taskFormError.textContent = "";
  submitBtn.textContent = "Save Task";
  newTaskBtn.disabled = false;
}

function openTaskForm(task = null) {
  taskForm.reset();
  taskFormError.textContent = "";
  editingTaskId = task ? task.id : null;

  $("task-status-group").hidden = !task;

  if (task) {
    $("task-title").value = task.title;
    $("task-description").value = task.description || "";
    $("task-priority").value = task.priority;
    $("task-status").value = task.status;
  }

  submitBtn.textContent = task ? "Update Task" : "Save Task";
  newTaskBtn.disabled = true;
  taskForm.hidden = false;
  $("task-title").focus();
}

async function loadDashboard() {
  const apiStatus = $("api-status");

  try {
    const response = await fetch("/health/live", {
      cache: "no-store",
    });

    if (!response.ok) throw new Error("Health check failed");

    apiStatus.textContent = "Online";
    apiStatus.className = "status-pill online";
  } catch {
    apiStatus.textContent = "Offline";
    apiStatus.className = "status-pill offline";
  }

  try {
    const counts = {
      total: 0,
      pending: 0,
      in_progress: 0,
      completed: 0,
    };

    let offset = 0;
    const limit = 100;

    while (true) {
      const response = await fetch(
        `${API_BASE}?limit=${limit}&offset=${offset}`,
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error("Statistics unavailable");
      }

      const tasks = await response.json();

      for (const task of tasks) {
        counts.total++;

        if (Object.hasOwn(counts, task.status)) {
          counts[task.status]++;
        }
      }

      if (tasks.length < limit) break;
      offset += limit;
    }

    $("total-tasks").textContent = counts.total;
    $("pending-tasks").textContent = counts.pending;
    $("active-tasks").textContent = counts.in_progress;
    $("completed-tasks").textContent = counts.completed;
  } catch (error) {
    console.error("Statistics error:", error);

    for (const id of [
      "total-tasks",
      "pending-tasks",
      "active-tasks",
      "completed-tasks",
    ]) {
      $(id).textContent = "—";
    }
  }
}

async function loadTaskList() {
  const container = $("task-list");
  container.replaceChildren();

  const loading = document.createElement("div");
  loading.className = "empty-state";
  loading.textContent = "Loading tasks...";
  container.append(loading);

  try {
    const response = await fetch(
      `${API_BASE}?limit=100&offset=0`,
      { cache: "no-store" }
    );

    if (!response.ok) {
      throw new Error("Unable to load tasks");
    }

    const tasks = await response.json();
    container.replaceChildren();

    if (tasks.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No tasks yet. Create your first task.";
      container.append(empty);
      return;
    }

    for (const task of tasks) {
      const card = document.createElement("article");
      card.className = "task-card";

      const title = document.createElement("strong");
      title.textContent = task.title;

      const description = document.createElement("p");
      description.textContent = task.description || "No description";

      const meta = document.createElement("small");
      meta.textContent =
        `Status: ${task.status.replaceAll("_", " ")} | Priority: ${task.priority}`;

      const actions = document.createElement("div");
      actions.className = "task-actions";

      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "secondary-btn";
      editBtn.textContent = "Edit";

      editBtn.addEventListener("click", () => {
        openTaskForm(task);
      });

      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "secondary-btn";
      deleteBtn.textContent = "Delete";

      deleteBtn.addEventListener("click", async () => {
        const confirmed = window.confirm(
          `Are you sure you want to delete "${task.title}"?`
        );

        if (!confirmed) return;

        deleteBtn.disabled = true;

        try {
          const response = await fetch(
            `${API_BASE}/${task.id}`,
            { method: "DELETE" }
          );

          if (!response.ok) {
            throw new Error(`Delete failed (${response.status})`);
          }

          if (editingTaskId === task.id) {
            resetTaskForm();
          }

          await Promise.all([
            loadDashboard(),
            loadTaskList(),
          ]);
        } catch (error) {
          window.alert(error.message);
          deleteBtn.disabled = false;
        }
      });

      actions.append(editBtn, deleteBtn);
      card.append(title, description, meta, actions);
      container.append(card);
    }
  } catch (error) {
    console.error("Task list error:", error);
    container.replaceChildren();

    const message = document.createElement("p");
    message.textContent = "Unable to load tasks.";

    const retry = document.createElement("button");
    retry.type = "button";
    retry.className = "secondary-btn";
    retry.textContent = "Retry";
    retry.addEventListener("click", loadTaskList);

    container.append(message, retry);
  }
}

newTaskBtn.disabled = false;

newTaskBtn.addEventListener("click", () => {
  openTaskForm();
});

cancelTaskBtn.addEventListener("click", () => {
  if (!isSaving) resetTaskForm();
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (isSaving) return;

  isSaving = true;
  submitBtn.disabled = true;
  cancelTaskBtn.disabled = true;
  taskFormError.textContent = "";

  const isEditing = editingTaskId !== null;

  const payload = {
    title: $("task-title").value.trim(),
    description: $("task-description").value.trim() || null,
    priority: $("task-priority").value,
  };

  if (isEditing) {
    payload.status = $("task-status").value;
  }

  try {
    const url = isEditing
      ? `${API_BASE}/${editingTaskId}`
      : API_BASE;

    const response = await fetch(url, {
      method: isEditing ? "PATCH" : "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let message = `Request failed (${response.status})`;

      if (response.status === 404) {
        message = "Task no longer exists. Refresh the list.";
      }

      throw new Error(message);
    }

    resetTaskForm();

    await Promise.all([
      loadDashboard(),
      loadTaskList(),
    ]);
  } catch (error) {
    taskFormError.textContent = error.message;
  } finally {
    isSaving = false;
    submitBtn.disabled = false;
    cancelTaskBtn.disabled = false;
  }
});

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  loadTaskList();
});

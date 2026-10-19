# Build a Simple Todo List App Using PostgreSQL

Build a small, simple todo list web app. Tasks are stored in PostgreSQL so they are still there after a restart. Keep everything minimal: one page, a basic backend, one database table. There is no login and no advanced features.

---

## 1. Features

The user can:
- Add a task by typing a title and pressing Enter or clicking "Add"
- See all tasks in a list, newest first
- Mark a task as done or not done with a checkbox
- Edit a task's title
- Delete a task

That's all. Don't add lists, tags, due dates, priorities, search or filters.

---

## 2. Tech Stack

- **Backend:** Python with FastAPI
- **Database:** PostgreSQL
- **Frontend:** A single HTML page with plain JavaScript and simple CSS, served by the FastAPI app

Keep dependencies to a minimum.

---

## 3. User Interface

One page with a title, an input box with an "Add" button, and the task list below it. Each task shows a checkbox, its title, and "Edit" and "Delete" buttons. Completed tasks appear crossed out. Deleting asks for a simple confirmation.

Keep the design clean and plain. It should work on both desktop and mobile.

---

## 4. Rules

- A task title can't be empty. Show "Task title cannot be empty." if the user tries.
- Keep titles to a reasonable length, such as 200 characters.
- If something fails, show a short, friendly error message instead of a technical one.

---

## 5. Backend

Keep the backend small. Provide a simple API to list, add, update and delete tasks, and a health check. A single table for tasks is enough. Creating the table automatically when the app starts is fine.

---

## 6. Configuration and Running

- Read the database connection string from an environment variable, and include an example `.env` file.
- The app must run locally without Docker.
- Starting the backend should also serve the web page, so the user only runs one command.

---



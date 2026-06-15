

import json
import os
import argparse 

# Try to import rich for pretty output, fallback to plain print if not installed
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# DATA FILE PATH


DATA_FILE = "data.json"


# CLASSES

class Person:
    """Base class with a name."""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
    
class User(Person):
    """A user of the system. Has an email and a list of projects."""

    # Class-level ID counter
    next_id = 1

    def __init__(self, name, email, user_id=None):
        super().__init__(name)
        self._email = email  
        self.user_id = user_id if user_id else User.next_id
        User.next_id = max(User.next_id, self.user_id) + 1
        self.projects = []  

    # Property to control access to email
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if "@" not in value:
            raise ValueError("Email must contain '@'")
        self._email = value

    def add_project(self, project):
        self.projects.append(project)

    def __str__(self):
        return f"[{self.user_id}] {self.name} <{self.email}> — {len(self.projects)} project(s)"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "projects": [p.to_dict() for p in self.projects]
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["name"], data["email"], data["user_id"])
        user.projects = [Project.from_dict(p) for p in data.get("projects", [])]
        return user
    
class Project:
    """A project belonging to a user. Has tasks."""

    next_id = 1

    def __init__(self, title, description, due_date, project_id=None):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.project_id = project_id if project_id else Project.next_id
        Project.next_id = max(Project.next_id, self.project_id) + 1
        self.tasks = []  

    def add_task(self, task):
        self.tasks.append(task)

    def __str__(self):
        return f"[{self.project_id}] {self.title} (Due: {self.due_date}) — {len(self.tasks)} task(s)"

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [t.to_dict() for t in self.tasks]
        }

    @classmethod
    def from_dict(cls, data):
        project = cls(data["title"], data["description"], data["due_date"], data["project_id"])
        project.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return project

class Task:
    """A task inside a project."""

    next_id = 1

    def __init__(self, title, assigned_to, task_id=None, status="pending"):
        self.title = title
        self.assigned_to = assigned_to  
        self.task_id = task_id if task_id else Task.next_id
        Task.next_id = max(Task.next_id, self.task_id) + 1
        self._status = status 

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        allowed = ["pending", "complete"]
        if value not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        self._status = value

    def mark_complete(self):
        self.status = "complete"

    def __str__(self):
        icon = "✅" if self.status == "complete" else "⏳"
        return f"  {icon} [{self.task_id}] {self.title} (assigned to: {self.assigned_to})"

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "assigned_to": self.assigned_to,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["title"], data["assigned_to"], data["task_id"], data["status"])

# FILE I/O 

def load_data():
    """Load all users (and their projects/tasks) from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            raw = json.load(f)
            return [User.from_dict(u) for u in raw]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Could not load data — {e}")
        return []


def save_data(users):
    """Save all users to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump([u.to_dict() for u in users], f, indent=2)

# LOOKUP HELPERS

def find_user(users, user_id):
    for u in users:
        if u.user_id == user_id:
            return u
    return None


def find_project(users, project_id):
    for u in users:
        for p in u.projects:
            if p.project_id == project_id:
                return p
    return None


def find_task(users, task_id):
    for u in users:
        for p in u.projects:
            for t in p.tasks:
                if t.task_id == task_id:
                    return t
    return None


# DISPLAY HELPERS


def print_users(users):
    if not users:
        print("No users found.")
        return

    if HAS_RICH:
        table = Table(title="Users")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Email")
        table.add_column("Projects")
        for u in users:
            table.add_row(str(u.user_id), u.name, u.email, str(len(u.projects)))
        console.print(table)
    else:
        print("\n--- Users ---")
        for u in users:
            print(u)
        print()


def print_projects(user):
    if not user.projects:
        print(f"No projects for {user.name}.")
        return

    if HAS_RICH:
        table = Table(title=f"Projects for {user.name}")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Description")
        table.add_column("Due Date")
        table.add_column("Tasks")
        for p in user.projects:
            table.add_row(str(p.project_id), p.title, p.description, p.due_date, str(len(p.tasks)))
        console.print(table)
    else:
        print(f"\n--- Projects for {user.name} ---")
        for p in user.projects:
            print(p)
        print()


def print_tasks(project):
    if not project.tasks:
        print(f"No tasks in project '{project.title}'.")
        return

    if HAS_RICH:
        table = Table(title=f"Tasks in '{project.title}'")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Assigned To")
        table.add_column("Status")
        for t in project.tasks:
            status_color = "green" if t.status == "complete" else "yellow"
            table.add_row(str(t.task_id), t.title, t.assigned_to, f"[{status_color}]{t.status}[/{status_color}]")
        console.print(table)
    else:
        print(f"\n--- Tasks in '{project.title}' ---")
        for t in project.tasks:
            print(t)
        print()

# COMMAND HANDLERS

def cmd_add_user(args):
    users = load_data()
    # Check for duplicate email
    for u in users:
        if u.email == args.email:
            print(f"Error: A user with email '{args.email}' already exists.")
            return
    user = User(args.name, args.email)
    users.append(user)
    save_data(users)
    print(f"✅ User '{args.name}' added with ID {user.user_id}.")


def cmd_list_users(args):
    users = load_data()
    print_users(users)


def cmd_add_project(args):
    users = load_data()
    user = find_user(users, args.user_id)
    if not user:
        print(f"Error: No user with ID {args.user_id}.")
        return
    project = Project(args.title, args.description, args.due_date)
    user.add_project(project)
    save_data(users)
    print(f"✅ Project '{args.title}' added to {user.name} (Project ID: {project.project_id}).")


def cmd_list_projects(args):
    users = load_data()
    user = find_user(users, args.user_id)
    if not user:
        print(f"Error: No user with ID {args.user_id}.")
        return
    print_projects(user)


def cmd_add_task(args):
    users = load_data()
    project = find_project(users, args.project_id)
    if not project:
        print(f"Error: No project with ID {args.project_id}.")
        return
    task = Task(args.title, args.assigned_to)
    project.add_task(task)
    save_data(users)
    print(f"✅ Task '{args.title}' added to project '{project.title}' (Task ID: {task.task_id}).")


def cmd_list_tasks(args):
    users = load_data()
    project = find_project(users, args.project_id)
    if not project:
        print(f"Error: No project with ID {args.project_id}.")
        return
    print_tasks(project)


def cmd_complete_task(args):
    users = load_data()
    task = find_task(users, args.task_id)
    if not task:
        print(f"Error: No task with ID {args.task_id}.")
        return
    task.mark_complete()
    save_data(users)
    print(f"✅ Task '{task.title}' marked as complete!")


def cmd_edit_project(args):
    users = load_data()
    project = find_project(users, args.project_id)
    if not project:
        print(f"Error: No project with ID {args.project_id}.")
        return
    if args.title:
        project.title = args.title
    if args.description:
        project.description = args.description
    if args.due_date:
        project.due_date = args.due_date
    save_data(users)
    print(f"✅ Project {args.project_id} updated.")

# CLI SETUP WITH ARGPARSE

def main():
    parser = argparse.ArgumentParser(
        description="📋 Project Management CLI Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add-user 
    p_add_user = subparsers.add_parser("add-user", help="Add a new user")
    p_add_user.add_argument("--name", required=True, help="User's full name")
    p_add_user.add_argument("--email", required=True, help="User's email address")
    p_add_user.set_defaults(func=cmd_add_user)

    # list-users 
    p_list_users = subparsers.add_parser("list-users", help="List all users")
    p_list_users.set_defaults(func=cmd_list_users)

    # add-project 
    p_add_project = subparsers.add_parser("add-project", help="Add a project to a user")
    p_add_project.add_argument("--user-id", required=True, type=int, help="ID of the user")
    p_add_project.add_argument("--title", required=True, help="Project title")
    p_add_project.add_argument("--description", required=True, help="Short project description")
    p_add_project.add_argument("--due-date", required=True, help="Due date (e.g. 2025-12-31)")
    p_add_project.set_defaults(func=cmd_add_project)

    # list-projects 
    p_list_projects = subparsers.add_parser("list-projects", help="List projects for a user")
    p_list_projects.add_argument("--user-id", required=True, type=int, help="ID of the user")
    p_list_projects.set_defaults(func=cmd_list_projects)

    # edit-project 
    p_edit_project = subparsers.add_parser("edit-project", help="Edit a project's details")
    p_edit_project.add_argument("--project-id", required=True, type=int, help="ID of the project")
    p_edit_project.add_argument("--title", help="New title")
    p_edit_project.add_argument("--description", help="New description")
    p_edit_project.add_argument("--due-date", help="New due date")
    p_edit_project.set_defaults(func=cmd_edit_project)

    # --- add-task ---
    p_add_task = subparsers.add_parser("add-task", help="Add a task to a project")
    p_add_task.add_argument("--project-id", required=True, type=int, help="ID of the project")
    p_add_task.add_argument("--title", required=True, help="Task title")
    p_add_task.add_argument("--assigned-to", required=True, help="Person responsible for this task")
    p_add_task.set_defaults(func=cmd_add_task)

    # --- list-tasks ---
    p_list_tasks = subparsers.add_parser("list-tasks", help="List tasks in a project")
    p_list_tasks.add_argument("--project-id", required=True, type=int, help="ID of the project")
    p_list_tasks.set_defaults(func=cmd_list_tasks)

    # --- complete-task ---
    p_complete_task = subparsers.add_parser("complete-task", help="Mark a task as complete")
    p_complete_task.add_argument("--task-id", required=True, type=int, help="ID of the task")
    p_complete_task.set_defaults(func=cmd_complete_task)

    # Parse and run
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
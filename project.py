

import json
import os
import argparse
from datetime import datetime

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

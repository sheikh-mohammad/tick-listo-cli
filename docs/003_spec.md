/sp.specify ## **Advanced Level (Intelligent Features)**

1. Recurring Tasks – Auto-reschedule repeating tasks (e.g., "weekly meeting")
2. Due Dates & Time Reminders – Set deadlines with date/time pickers; browser notifications

Add these to make the app feel polished and practical:

1. Recurring Tasks – Auto-reschedule repeating tasks (e.g., "weekly meeting")
2. Due Dates & Time Reminders – Set deadlines with date/time pickers; browser notifications
3. **Required Recurring Tasks agreetion, due date, time** – Task creation MUST require Recurring Tasks agreetion as optional. Users can assign due date and time.

Also update README.md with these new features

this is feature 003

## **Requirements**

* All existing Basic Level features (Add, Delete, Update, View, Mark Complete) are implemented do not change them, add new code
* All existing Intermediate Level features (Priorities & Tags/Categories, Search & Filter, Sort Tasks, All Commands) are implemented do not change them, add new code
* Enhance the CLI interface with Rich library for comprehensive beautification
* Maintain backward compatibility with existing functionality
* Follow clean code principles and proper Python project structure

## **Technology Stack**

- UV for package management
- UV for dependency management
- Python 3.13+ for console application development
- Rich for beautiful CLI interfaces and terminal formatting
- GitHub for deployment
- Git for Version Control System
- JSON file storage (ticklisto_data.json) for task persistence

### Infrastructure & Deployment
- Console-based user interface for Phase I with enhanced Rich formatting
- Local development environment

## **Deliverables**

* /src folder with Python source code existing + new
* README.md with setup instructions existing + new
* Working console application demonstrating:
* Adding tasks with title and description
* Listing all tasks with status indicators using styled tables
* Updating task details
* Deleting tasks by ID
* Marking tasks as complete/incomplete
* Enhanced visual interface with all Rich features implemented
* Priorities & Tags/Categories – Assign levels (high/medium/low) or labels (work/home)
* Search & Filter – Search by keyword; filter by status, priority, or date
* Sort Tasks – Reorder by due date, priority, or alphabetically
* Recurring Tasks – Auto-reschedule repeating tasks (e.g., "weekly meeting")
* Due Dates & Time Reminders – Set deadlines with date/time pickers; browser notifications
* **Required Recurring Tasks agreetion, due date, time** – Task creation MUST require Recurring Tasks agreetion as optional. Users can assign due date and time.

> All Remainders will sent using gmail api python library to sent it on gmail to haji08307@gmail.com

and use these libraries "google
    "google-api-python-client
    "google-auth
    "google-auth-oauthlib
And all credentials are added

like token.json and credentials.json

Branch name: `003-advance-ticklisto-enhancements
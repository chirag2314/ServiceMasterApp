# ServiceMasterApp
## About

ServiceMasterApp is a multi-user household services application developed as part of Modern Application Development 1 course, made using Flask framework and SQLite Database. This app let's customers search, book service and professionals. The admin create/edit/deletes services, approves professionals.

## Features

1. 3 Types of users: Admin, Customer, Professional
2. RBAC for authentication and authorization
3. Ability to search services based on name

## Functionalities
### Customer
1. Can search for services based on name
2. Can book a Service Request for Professional of their choice
3. Can close a Service Request with Review and Rating
4. Modiy personal details and password
5. (WIP) Summary Page with service request history

### Professionals
1. Can choose to accept/decline service requests
2. (WIP) Summary Page with service history

### Admin
1. Can create/edit/delete various services
2. Can Block/Approve a Professional
3. Can see summary of all service requests
4. (WIP) Summary Page with professionals and Service Requests history

## Tech Stack
### Backend:
**Flask** - Lightweight web framework
**SQLAlchemy** - ORM for database operations
**SQLite** - Database

### Frontend:
**HTML/CSS** - Frontend Markup and styling
**Bootstrap** - Responsive UI Components

## Setup:

1. 1. **Clone the Repository**
   ```bash
   git clone https://github.com/chirag2314/ServiceMasterApp.git
   cd ServiceMasterApp
   ```

2. **Create a Virtual Environment & Install Requirements**
   ```bash
   python3 -m venv venv
   . venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Start the Flask Application**
   ```bash
   flask run
   ```

## Contact
Created by [Chirag](https://www.linkedin.com/in/chirag2301/) 
Feel free to make issues/PRs to improve the project and reach out for feedback!

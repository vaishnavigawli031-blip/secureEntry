# secureEntry

A College Gate Entry Management System built using Python and Flask.

This project aims to simplify college gate entry management by providing separate interfaces for administrators, security guards, and visitors.

## Project Status

Currently under development.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- Git and GitHub

## Features

- Admin login with environment-based credentials.
- Protected admin dashboard using Flask sessions.
- Admin logout functionality.
- Guard registration.
- Secure password hashing for guard accounts.
- Duplicate Guard ID prevention.
- Separate pages for administrators, guards, and visitors.

## Future Improvements

- Complete guard login authentication.
- Save and manage visitor entry records.
- Improve form validation and application security.
- Enhance the user interface.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vaishnavigawli031-blip/secureEntry.git
```

### 2. Navigate to the Project Folder

```bash
cd secureEntry
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment (Windows)

```cmd
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install Flask
```

### 6. Configure Environment Variables

Open Windows Command Prompt and set your admin username:

```cmd
set ADMIN_USERNAME=admin
```

Set your own strong admin password:

```cmd
set "ADMIN_PASSWORD=your-own-strong-password"
```

Generate a Flask secret key:

```cmd
for /f "delims=" %i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set "SECRET_KEY=%i"
```

Keep these credentials private.

### 7. Run the Application

```bash
python app.py
```

### 8. Open in Browser

Visit:

http://127.0.0.1:5000

## Author

Vaishnavi Gavali

B.Sc. Computer Science Student

GitHub: [vaishnavigawli031-blip](https://github.com/vaishnavigawli031-blip)
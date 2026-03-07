# ☁️ CloudVault

A modern file storage platform built with Django. Store files, organize with folders, and share publicly with others.

## Features
- 🔐 Email/password authentication (signup & login)
- 📁 Create folders and subfolders
- ⬆️ Upload files (drag & drop supported)
- 🔒 Public/private folder visibility controls
- ✏️ Rename folders and files
- 🗑️ Delete folders and files
- 🔍 Search and explore other users' public vaults
- 👤 Profile page with avatar, bio, and stats
- 🌙 Dark/light mode toggle
- 📱 Fully responsive mobile design

## Quick Start

### Requirements
- Python 3.8+
- pip

### Run the app

```bash
# Option 1: Auto setup script
python setup_and_run.py

# Option 2: Manual setup
pip install django pillow
python manage.py migrate
python manage.py runserver
```

Then open **http://127.0.0.1:8000** in your browser.

### Create admin user (optional)
```bash
python manage.py createsuperuser
# Visit http://127.0.0.1:8000/admin/
```

## Project Structure
```
cloudvault/
├── manage.py
├── setup_and_run.py
├── cloudvault/          # Project settings
│   ├── settings.py
│   └── urls.py
├── core/                # Main app
│   ├── models.py        # User, Folder, File models
│   ├── views.py         # All views & API endpoints
│   ├── urls.py          # URL routing
│   ├── forms.py         # Django forms
│   └── templates/core/
│       ├── auth.html    # Login/Signup
│       ├── base.html    # Layout shell
│       ├── home.html    # File manager
│       ├── explore.html # Search users
│       ├── user_public.html  # Public profile view
│       └── profile.html # Own profile & settings
└── media/               # Uploaded files (auto-created)
```

## Usage Guide

### Home (File Manager)
- Click **New Folder** to create a folder
- **Double-click** a folder to open it
- **Right-click** or click `⋯` for options (rename, visibility, delete)
- Inside a folder: upload files via button or drag & drop
- Set folders to **Public** so others can discover them

### Explore
- Search users by name or email
- Click a user card to view their public vault
- Browse and download files from public folders

### Profile
- Upload a profile picture
- Edit your username and bio
- Toggle dark/light mode
- Delete your account from the Danger Zone

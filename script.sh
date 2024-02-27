#!/bin/bash

# Directory path
DIR="/Users/oriokie/Msamaria"

# Change directory
cd "$DIR" || exit

# Create directories
mkdir -p app
mkdir -p app/templates
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p app/static/images
mkdir -p app/storage/uploads
mkdir -p tests

# Create files
touch app/__init__.py
touch app/routes.py
touch app/models.py
touch app/controllers.py
touch app/templates/index.html
touch app/templates/login.html
touch app/static/css/style.css
touch app/static/js/script.js
touch config.py
touch run.py
touch tests/__init__.py
touch tests/test_routes.py
touch tests/test_models.py
touch tests/test_controllers.py

# Optionally, create and initialize the database file
touch app/storage/database.db

echo "Directory structure and files created successfully in $DIR!"


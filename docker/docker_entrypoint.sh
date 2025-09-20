#!/bin/bash
# HSEG Docker Entry Point Script
# Handles database initialization and model setup

set -e

echo "🚀 Starting HSEG AI System..."

# Function to wait for database to be ready
wait_for_db() {
    echo "📊 Waiting for database to be ready..."
    python -c "
import time
import sqlite3
from pathlib import Path

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        # Try to connect to SQLite database
        conn = sqlite3.connect('hseg_database.db', timeout=10)
        conn.execute('SELECT 1')
        conn.close()
        print('Database is ready!')
        break
    except Exception as e:
        print(f'Database not ready (attempt {attempt + 1}/{max_attempts}): {e}')
        time.sleep(2)
        attempt += 1
else:
    print('Database failed to become ready')
    exit(1)
"
}

# Function to initialize database
init_database() {
    echo "🗄️ Initializing database..."
    python -c "
from database_config import create_database, optimize_database
try:
    create_database()
    optimize_database()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
    exit(1)
"
}

# Function to check/download models
setup_models() {
    echo "🤖 Setting up ML models..."
    
    # Create models directory if it doesn't exist
    mkdir -p /app/models
    
    # Check if models exist, if not, they will be trained on first startup
    python -c "
from pathlib import Path
import os

model_files = [
    'models/individual_risk_model.pkl',
    'models/text_risk_classifier.pt', 
    'models/organizational_risk_model.pkl'
]

missing_models = [f for f in model_files if not Path(f).exists()]

if missing_models:
    print(f'Missing models: {missing_models}')
    print('Models will be trained on first API startup')
else:
    print('All models are available')
"
}

# Function to run database migrations (if using Alembic)
run_migrations() {
    echo "🔄 Running database migrations..."
    # Uncomment if using Alembic migrations
    # alembic upgrade head
    echo "No migrations to run (using SQLAlchemy create_all)"
}

# Function to validate environment
validate_environment() {
    echo "✅ Validating environment..."
    
    # Check required environment variables
    python -c "
import os
import sys

required_vars = []  # Add any required env vars here
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f'Missing required environment variables: {missing_vars}')
    sys.exit(1)
else:
    print('Environment validation passed')
"
}

# Function to test API startup
test_startup() {
    echo "🧪 Testing API startup..."
    
    # Quick test to ensure imports work
    python -c "
try:
    from main import app
    from ml_pipeline import pipeline
    from database_config import engine
    print('All imports successful')
except Exception as e:
    print(f'Import error: {e}')
    exit(1)
"
}

# Main startup sequence
main() {
    echo "🎯 HSEG AI System Container Starting..."
    
    # Environment validation
    validate_environment
    
    # Database setup
    wait_for_db
    init_database
    run_migrations
    
    # Model setup
    setup_models
    
    # Startup test
    test_startup
    
    echo "✨ HSEG initialization complete!"
    echo "🌐 Starting web server..."
    
    # Execute the main command
    exec "$@"
}

# Handle different commands
case "$1" in
    "uvicorn")
        main "$@"
        ;;
    "bash"|"sh")
        exec "$@"
        ;;
    "python")
        exec "$@"
        ;;
    "test")
        echo "🧪 Running test mode..."
        validate_environment
        test_startup
        echo "✅ Test completed successfully"
        ;;
    "init-db")
        echo "🗄️ Database initialization only..."
        wait_for_db
        init_database
        echo "✅ Database initialization completed"
        ;;
    "train-models")
        echo "🤖 Training models..."
        validate_environment
        wait_for_db
        init_database
        python -c "
import asyncio
from ml_pipeline import initialize_ml_pipeline

async def train():
    success = await initialize_ml_pipeline(train_if_missing=True)
    if success:
        print('✅ Model training completed successfully')
    else:
        print('❌ Model training failed')
        exit(1)

asyncio.run(train())
"
        ;;
    "health-check")
        echo "🏥 Running health check..."
        python -c "
import requests
import sys
import time

# Wait a moment for server to be ready
time.sleep(2)

try:
    response = requests.get('http://localhost:8000/health', timeout=10)
    if response.status_code == 200:
        print('✅ Health check passed')
        print(response.json())
    else:
        print(f'❌ Health check failed: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Health check error: {e}')
    sys.exit(1)
"
        ;;
    *)
        echo "🤔 Unknown command: $1"
        echo "Available commands:"
        echo "  uvicorn main:app --host 0.0.0.0 --port 8000  # Start web server (default)"
        echo "  test                                          # Run tests"
        echo "  init-db                                       # Initialize database only"
        echo "  train-models                                  # Train ML models"
        echo "  health-check                                  # Check system health"
        echo "  bash                                          # Interactive shell"
        exec "$@"
        ;;
esac
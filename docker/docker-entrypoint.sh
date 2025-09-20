#!/bin/bash
set -e

# HSEG AI System Docker Entrypoint Script

echo "Starting HSEG AI System..."

# Initialize SQLite database
echo "Initializing SQLite database..."
cd /app
python -c "
try:
    from app.models import database_models
    from app.config.database_config import create_database
    create_database()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
    # Continue anyway - app can create database on startup
"

# Check if models exist, if not create basic ones
echo "Checking trained models..."
if [ ! -f "/app/app/models/trained/individual_risk_model.pkl" ]; then
    echo "Training individual model..."
    python train_individual_model.py || echo "Individual model training failed"
fi

if [ ! -f "/app/app/models/trained/organizational_risk_model.pkl" ]; then
    echo "Training organizational model..."
    python train_organizational_model.py || echo "Organizational model training failed"
fi

if [ ! -f "/app/app/models/trained/text_risk_classifier.pkl" ]; then
    echo "Training text classifier..."
    python train_text_classifier.py || echo "Text classifier training failed"
fi

echo "Models check complete!"

# Execute the main command
echo "Starting application with command: $@"
exec "$@"
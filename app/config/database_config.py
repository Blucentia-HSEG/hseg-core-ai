"""
HSEG Database Configuration - Serverless SQLite with SQLAlchemy
Optimized for fast, serverless deployment with built-in connection pooling
"""

import os
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
import aiosqlite
from contextlib import asynccontextmanager

# Database Configuration (default to ./database/hseg_database.db)
DEFAULT_DB_DIR = Path("database")
DEFAULT_DB_DIR.mkdir(exist_ok=True)
DATABASE_FILE = str(DEFAULT_DB_DIR / "hseg_database.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_FILE}")

# SQLAlchemy Configuration for Serverless
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 20,
        "isolation_level": None,
    },
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Async Database Manager for High Performance
class AsyncDatabaseManager:
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self._connection = None
    
    @asynccontextmanager
    async def get_connection(self):
        """Async context manager for database connections"""
        async with aiosqlite.connect(self.db_file) as conn:
            # Enable WAL mode for better concurrent performance
            await conn.execute("PRAGMA journal_mode=WAL;")
            await conn.execute("PRAGMA synchronous=NORMAL;")
            await conn.execute("PRAGMA cache_size=10000;")
            await conn.execute("PRAGMA temp_store=memory;")
            yield conn
    
    async def execute_query(self, query: str, params: tuple = None):
        """Execute a single query"""
        async with self.get_connection() as conn:
            if params:
                cursor = await conn.execute(query, params)
            else:
                cursor = await conn.execute(query)
            await conn.commit()
            return await cursor.fetchall()
    
    async def execute_many(self, query: str, params_list: list):
        """Execute multiple queries efficiently"""
        async with self.get_connection() as conn:
            await conn.executemany(query, params_list)
            await conn.commit()

# Synchronous Database Dependency for FastAPI
def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize async manager
async_db = AsyncDatabaseManager()

# Database Initialization
def create_database():
    """Create all tables and initial data"""
    Base.metadata.create_all(bind=engine)
    
    # Initialize HSEG Categories
    with SessionLocal() as db:
        try:
            # Check if categories already exist
            result = db.execute(text("SELECT COUNT(*) FROM hseg_categories")).scalar()
            if result == 0:
                # Insert HSEG Categories
                categories_sql = """
                INSERT INTO hseg_categories 
                (category_id, category_name, category_weight, priority_level, description, psychological_focus) 
                VALUES 
                (1, 'Power_Abuse_Suppression', 3.0, 'Critical', 'Authority misuse and retaliation', 'Psychological safety in power dynamics'),
                (2, 'Discrimination_Exclusion', 2.5, 'Severe', 'Bias and belonging barriers', 'Identity-based psychological safety'),
                (3, 'Manipulative_Work_Culture', 2.0, 'Moderate', 'Emotional manipulation and boundary violations', 'Authentic expression safety'),
                (4, 'Failure_Of_Accountability', 3.0, 'Critical', 'System integrity and justice failures', 'Trust in institutional fairness'),
                (5, 'Mental_Health_Harm', 2.5, 'Severe', 'Psychological wellbeing damage', 'Work-related mental health impact'),
                (6, 'Erosion_Voice_Autonomy', 2.0, 'Moderate', 'Disempowerment and voice suppression', 'Agency and influence safety');
                """
                db.execute(text(categories_sql))
                db.commit()
                print("HSEG Categories initialized successfully")
                
                # Insert Survey Questions
                questions_sql = """
                INSERT INTO survey_questions 
                (question_id, category_id, question_code, question_text, question_type, response_scale, is_reverse_scored) 
                VALUES 
                (1, 1, 'Q1', 'I feel safe speaking up when I experience or witness something wrong at my workplace', 'Likert_4', '{"1": "Strongly Disagree", "2": "Disagree", "3": "Agree", "4": "Strongly Agree"}', false),
                (2, 1, 'Q2', 'Leadership uses their position to silence criticism rather than address concerns', 'Likert_4', '{"1": "Strongly Disagree", "2": "Disagree", "3": "Agree", "4": "Strongly Agree"}', true),
                (3, 1, 'Q3', 'People here avoid speaking up because they fear negative consequences', 'Likert_4', '{"1": "Strongly Disagree", "2": "Disagree", "3": "Agree", "4": "Strongly Agree"}', true),
                (4, 2, 'Q5', 'People are treated fairly regardless of their race, gender, age, or background', 'Likert_4', '{"1": "Strongly Disagree", "2": "Disagree", "3": "Agree", "4": "Strongly Agree"}', false),
                (5, 2, 'Q6', 'Everyone has equal access to opportunities and resources here', 'Likert_4', '{"1": "Strongly Disagree", "2": "Disagree", "3": "Agree", "4": "Strongly Agree"}', false),
                (6, 2, 'Q7', 'In the past 30 days, how many times have you witnessed comments or behaviors that exclude or diminish others?', 'Frequency_Count', '{"1": "Never (0 times)", "2": "Rarely (1-2 times)", "3": "Sometimes (3-5 times)", "4": "Often (6+ times)"}', true),
                (7, 5, 'Q15', 'During the past 30 days, how often did work make you feel nervous or anxious?', 'Frequency_Count', '{"1": "None of the time (0 days)", "2": "A little of the time (1-7 days)", "3": "Some of the time (8-14 days)", "4": "Most/All of the time (15+ days)"}', true),
                (8, 5, 'Q16', 'During the past 30 days, how many days did work make you feel hopeless or depressed?', 'Frequency_Count', '{"1": "None of the time (0 days)", "2": "A little of the time (1-7 days)", "3": "Some of the time (8-14 days)", "4": "Most/All of the time (15+ days)"}', true);
                """
                db.execute(text(questions_sql))
                db.commit()
                print("Survey Questions initialized successfully")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.rollback()

# Performance Optimization Functions
def optimize_database():
    """Apply performance optimizations to SQLite database"""
    with SessionLocal() as db:
        optimizations = [
            "PRAGMA journal_mode=WAL;",
            "PRAGMA synchronous=NORMAL;",
            "PRAGMA cache_size=10000;",
            "PRAGMA temp_store=memory;",
            "PRAGMA mmap_size=268435456;",  # 256MB
            "PRAGMA optimize;",
        ]
        
        for pragma in optimizations:
            try:
                db.execute(text(pragma))
                db.commit()
            except Exception as e:
                print(f"Warning: Could not apply optimization {pragma}: {e}")

# Database Health Check
def health_check():
    """Check database connectivity and performance"""
    try:
        with SessionLocal() as db:
            result = db.execute(text("SELECT 1")).scalar()
            if result == 1:
                return {"status": "healthy", "database": "connected"}
            else:
                return {"status": "error", "database": "query_failed"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

# Connection Pool Management
class ConnectionManager:
    """Manages database connections efficiently"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
    
    def get_session(self):
        """Get a database session"""
        return self.session_factory()
    
    def close_all_connections(self):
        """Close all database connections"""
        self.engine.dispose()
    
    def get_connection_info(self):
        """Get connection pool information"""
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalidated": pool.invalidated()
        }

# Global connection manager
connection_manager = ConnectionManager()

# Startup and Shutdown Events
async def startup_database():
    """Initialize database on startup"""
    create_database()
    optimize_database()
    print("Database initialized and optimized")

async def shutdown_database():
    """Cleanup database connections on shutdown"""
    connection_manager.close_all_connections()
    print("Database connections closed")

# Export main components
__all__ = [
    'engine',
    'SessionLocal', 
    'Base',
    'get_db',
    'async_db',
    'create_database',
    'optimize_database',
    'health_check',
    'connection_manager',
    'startup_database',
    'shutdown_database'
]

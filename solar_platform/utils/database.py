"""
Database models and management using SQLAlchemy
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import json

from config import get_config

config = get_config()

# Create engine
engine = create_engine(config.database.database_url, echo=config.app.debug)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Project(Base):
    """Solar project model"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(200))
    timezone = Column(String(50))

    # Project details
    system_capacity_kw = Column(Float)
    project_type = Column(String(50))  # fixed-tilt, tracking, agripv
    status = Column(String(50))  # design, construction, operations

    # Dates
    planned_start_date = Column(DateTime)
    planned_completion_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    commercial_operation_date = Column(DateTime)

    # Configuration (stored as JSON)
    module_config = Column(JSON)
    system_config = Column(JSON)
    financial_config = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))


class SimulationResult(Base):
    """Simulation results model"""
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), index=True, nullable=False)
    simulation_id = Column(String(100), unique=True, nullable=False)
    simulation_type = Column(String(50))  # fixed-tilt, tracking, optimization

    # Results
    front_irradiance = Column(Float)
    rear_irradiance = Column(Float)
    bifacial_gain = Column(Float)
    annual_production_kwh = Column(Float)
    capacity_factor = Column(Float)

    # Configuration used
    simulation_config = Column(JSON)
    detailed_results = Column(JSON)  # Store full results as JSON

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    simulation_date = Column(DateTime, default=datetime.utcnow)


class WeatherData(Base):
    """Weather data cache"""
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    location_key = Column(String(100), index=True)  # lat_lon_date combination
    data_type = Column(String(50))  # tmy, historical, forecast
    data_source = Column(String(50))  # nsrdb, visual_crossing, openweather

    # Data
    weather_data = Column(JSON)

    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)


class ConstructionLog(Base):
    """Construction progress and delay tracking"""
    __tablename__ = "construction_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), index=True, nullable=False)
    log_date = Column(DateTime, nullable=False)

    # Daily status
    workable_day = Column(Boolean)
    work_performed = Column(Boolean)
    percent_complete = Column(Float)

    # Weather conditions
    temperature = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    conditions = Column(String(100))

    # Issues/Notes
    delay_reason = Column(String(200))
    notes = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))


class PerformanceData(Base):
    """Operational performance data"""
    __tablename__ = "performance_data"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), index=True, nullable=False)
    measurement_date = Column(DateTime, nullable=False)

    # Production data
    actual_production_kwh = Column(Float)
    expected_production_kwh = Column(Float)
    performance_ratio = Column(Float)

    # Weather conditions
    ghi = Column(Float)
    dni = Column(Float)
    temperature = Column(Float)

    # System status
    availability = Column(Float)
    inverter_efficiency = Column(Float)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    data_source = Column(String(50))


# Database functions

def get_db() -> Session:
    """
    Get database session

    Usage:
        db = get_db()
        try:
            # do database operations
            db.commit()
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables - use with caution!"""
    Base.metadata.drop_all(bind=engine)


# CRUD operations

def create_project(db: Session, project_data: dict) -> Project:
    """Create a new project"""
    project = Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: str) -> Optional[Project]:
    """Get project by ID"""
    return db.query(Project).filter(Project.project_id == project_id).first()


def get_all_projects(db: Session, status: Optional[str] = None) -> list:
    """Get all projects, optionally filtered by status"""
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    return query.all()


def update_project(db: Session, project_id: str, update_data: dict) -> Optional[Project]:
    """Update project"""
    project = get_project(db, project_id)
    if project:
        for key, value in update_data.items():
            setattr(project, key, value)
        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
    return project


def delete_project(db: Session, project_id: str) -> bool:
    """Delete project"""
    project = get_project(db, project_id)
    if project:
        db.delete(project)
        db.commit()
        return True
    return False


def save_simulation_result(db: Session, result_data: dict) -> SimulationResult:
    """Save simulation result"""
    result = SimulationResult(**result_data)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_project_simulations(db: Session, project_id: str) -> list:
    """Get all simulations for a project"""
    return db.query(SimulationResult).filter(
        SimulationResult.project_id == project_id
    ).all()


def log_construction_day(db: Session, log_data: dict) -> ConstructionLog:
    """Log construction day"""
    log = ConstructionLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_construction_logs(db: Session, project_id: str, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> list:
    """Get construction logs for a project"""
    query = db.query(ConstructionLog).filter(ConstructionLog.project_id == project_id)

    if start_date:
        query = query.filter(ConstructionLog.log_date >= start_date)
    if end_date:
        query = query.filter(ConstructionLog.log_date <= end_date)

    return query.order_by(ConstructionLog.log_date).all()


def save_performance_data(db: Session, perf_data: dict) -> PerformanceData:
    """Save performance data"""
    perf = PerformanceData(**perf_data)
    db.add(perf)
    db.commit()
    db.refresh(perf)
    return perf


def get_performance_data(db: Session, project_id: str, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> list:
    """Get performance data for a project"""
    query = db.query(PerformanceData).filter(PerformanceData.project_id == project_id)

    if start_date:
        query = query.filter(PerformanceData.measurement_date >= start_date)
    if end_date:
        query = query.filter(PerformanceData.measurement_date <= end_date)

    return query.order_by(PerformanceData.measurement_date).all()


if __name__ == "__main__":
    # Initialize database if run directly
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")

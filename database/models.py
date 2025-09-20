from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    current_hp = Column(Float, nullable=False, default=100.0)
    max_hp = Column(Float, nullable=False, default=100.0)
    current_stam = Column(Float, nullable=False, default=100.0)
    max_stam = Column(Float, nullable=False, default=100.0)
    name = Column(String(128), nullable=False)
    title = Column(String(128))
    sin = Column(String(15))
    virtue = Column(String(15))
    general_feeling = Column(String(15))
    skill_name = Column(String(128))
    skill_description = Column(Text)
    passive_name = Column(String(128))
    passive_description = Column(Text)
    starter_background = Column(String(15))
    age = Column(Integer)
    gender = Column(String(15))
    temperature = Column(Integer)
    saturation = Column(Integer)
    biology = Column(String(20))
    main_style = Column(String(128))
    ritual = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dice_rolls = relationship("DiceRoll", back_populates="player")

class Enemy(Base):
    __tablename__ = 'enemies'
    
    id = Column(Integer, primary_key=True)
    current_hp = Column(Float, nullable=False, default=100.0)
    max_hp = Column(Float, nullable=False, default=100.0)
    current_stam = Column(Float, nullable=False, default=100.0)
    max_stam = Column(Float, nullable=False, default=100.0)
    name = Column(String(128), nullable=False)
    title = Column(String(128))
    sin = Column(String(15))
    virtue = Column(String(15))
    general_feeling = Column(String(15))
    skill_name = Column(String(128))
    skill_description = Column(Text)
    passive_name = Column(String(128))
    passive_description = Column(Text)
    starter_background = Column(String(15))
    age = Column(Integer)
    gender = Column(String(15))
    temperature = Column(Integer)
    saturation = Column(Integer)
    biology = Column(String(20))
    main_style = Column(String(128))
    ritual = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NPC(Base):
    __tablename__ = 'npcs'
    
    id = Column(Integer, primary_key=True)
    current_hp = Column(Float, nullable=False, default=100.0)
    max_hp = Column(Float, nullable=False, default=100.0)
    current_stam = Column(Float, nullable=False, default=100.0)
    max_stam = Column(Float, nullable=False, default=100.0)
    name = Column(String(128), nullable=False)
    title = Column(String(128))
    sin = Column(String(15))
    virtue = Column(String(15))
    general_feeling = Column(String(15))
    skill_name = Column(String(128))
    skill_description = Column(Text)
    passive_name = Column(String(128))
    passive_description = Column(Text)
    starter_background = Column(String(15))
    age = Column(Integer)
    gender = Column(String(15))
    temperature = Column(Integer)
    saturation = Column(Integer)
    biology = Column(String(20))
    main_style = Column(String(128))
    ritual = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GameSession(Base):
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    session_name = Column(String(128), nullable=False)
    host_name = Column(String(128), nullable=False)
    session_code = Column(String(10), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dice_rolls = relationship("DiceRoll", back_populates="session")
    messages = relationship("Message", back_populates="session")

class DiceRoll(Base):
    __tablename__ = 'dice_rolls'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    session_id = Column(Integer, ForeignKey('game_sessions.id'))
    dice_type = Column(String(10), nullable=False)  # d4, d6, d8, d10, d12, d20, d100
    num_dice = Column(Integer, default=1)
    modifier = Column(Integer, default=0)
    result = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)  # result + modifier
    roll_reason = Column(String(128))  # "Attack", "Damage", "Skill Check", etc.
    rolled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="dice_rolls")
    session = relationship("GameSession", back_populates="dice_rolls")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('game_sessions.id'))
    sender_name = Column(String(128), nullable=False)
    sender_type = Column(String(10), nullable=False)  # 'host', 'player'
    message_content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="messages")

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("All D&D tables created successfully!")
    print("Tables: players, enemies, npcs, game_sessions, dice_rolls, messages")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
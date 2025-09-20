from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
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
    general_feeling = Column(String(15), nullable=False, default="Good")
    skill_name = Column(String(128))
    skill_description = Column(Text)
    passive_name = Column(String(128))
    passive_description = Column(Text)
    starter_background = Column(String(15))
    age = Column(Integer, nullable=False, default=16)
    gender = Column(String(15), nullable=False, default="Male")
    temperature = Column(Integer)
    saturation = Column(String(15), nullable=False, default="Full")
    biology = Column(String(20), nullable=False, default="Human")
    main_style = Column(String(128))
    ritual = Column(String(128), nullable=False, default="0% Human")
    last_d5_roll = Column(Integer)
    last_d10_roll = Column(Integer)
    last_d20_roll = Column(Integer)
    last_d100_roll = Column(Integer)

    # Relationship to stats
    stats = relationship("PlayerStats", back_populates="player", uselist=False)

class PlayerStats(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, unique=True)
    str_stat = Column(Integer, nullable=False, default=10)  # Strength
    stm_stat = Column(Integer, nullable=False, default=10)  # Stamina  
    spd_stat = Column(Integer, nullable=False, default=10)  # Speed
    luk_stat = Column(Integer, nullable=False, default=10)  # Luck
    mny_stat = Column(Float, nullable=False, default=1.0)   # Money multiplier
    
    # Relationship back to player
    player = relationship("Player", back_populates="stats")

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
    skill_name = Column(String(128))
    skill_description = Column(Text)
    age = Column(Integer)
    gender = Column(String(15), nullable=False, default="Male")
    biology = Column(String(20), nullable=False, default="Human")
    main_style = Column(String(128))
    ritual = Column(String(128), nullable=False, default="0% Human")
    last_d5_roll = Column(Integer)
    last_d10_roll = Column(Integer)
    last_d20_roll = Column(Integer)
    last_d100_roll = Column(Integer)

    # Relationship to stats
    stats = relationship("EnemyStats", back_populates="enemy", uselist=False)

class EnemyStats(Base):
    __tablename__ = 'enemy_stats'
    
    id = Column(Integer, primary_key=True)
    enemy_id = Column(Integer, ForeignKey('enemies.id'), nullable=False, unique=True)
    str_stat = Column(Integer, nullable=False, default=10)  # Strength
    stm_stat = Column(Integer, nullable=False, default=10)  # Stamina  
    spd_stat = Column(Integer, nullable=False, default=10)  # Speed
    luk_stat = Column(Integer, nullable=False, default=10)  # Luck
    mny_stat = Column(Float, nullable=False, default=1.0)   # Money multiplier
    
    # Relationship back to player
    enemy = relationship("Enemy", back_populates="stats")

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
    skill_name = Column(String(128))
    skill_description = Column(Text)
    age = Column(Integer)
    gender = Column(String(15), nullable=False, default="Male")
    biology = Column(String(20), nullable=False, default="Human")
    main_style = Column(String(128))
    ritual = Column(String(128), nullable=False, default="0% Human")
    last_d5_roll = Column(Integer)
    last_d10_roll = Column(Integer)
    last_d20_roll = Column(Integer)
    last_d100_roll = Column(Integer)

    # Relationship to stats
    stats = relationship("NpcStats", back_populates="npc", uselist=False)

class NpcStats(Base):
    __tablename__ = 'npc_stats'
    
    id = Column(Integer, primary_key=True)
    npc_id = Column(Integer, ForeignKey('npcs.id'), nullable=False, unique=True)
    str_stat = Column(Integer, nullable=False, default=10)  # Strength
    stm_stat = Column(Integer, nullable=False, default=10)  # Stamina  
    spd_stat = Column(Integer, nullable=False, default=10)  # Speed
    luk_stat = Column(Integer, nullable=False, default=10)  # Luck
    mny_stat = Column(Float, nullable=False, default=1.0)   # Money multiplier
    
    # Relationship back to player
    npc = relationship("NPC", back_populates="stats")

class GameSession(Base):
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    session_name = Column(String(128), nullable=False)
    host_name = Column(String(128), nullable=False)
    session_code = Column(String(10), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('game_sessions.id'))
    sender_name = Column(String(128), nullable=False)
    sender_type = Column(String(10), nullable=False)  # 'host', 'player'
    message_content = Column(Text, nullable=False)
    
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
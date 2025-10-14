# backend/app/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    position = Column(String) # 세분화된 포지션 (e.g., LCB, AM, RW)
    dominant_foot = Column(String) # 주발 (Right, Left, Both)

    # --- 공통/공격 능력치 ---
    stamina = Column(Integer, default=0)
    speed = Column(Integer, default=0)
    shooting_accuracy = Column(Integer, default=0)
    dribbling = Column(Integer, default=0)
    passing = Column(Integer, default=0)
    
    # --- 공격수/윙어 능력치 ---
    finishing = Column(Integer, default=0)
    crossing = Column(Integer, default=0)

    # --- 미드필더 능력치 ---
    vision = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)

    # --- 수비수 능력치 ---
    tackling = Column(Integer, default=0)
    heading = Column(Integer, default=0)

    # --- 골키퍼 능력치 ---
    saving = Column(Integer, default=0)
    defense_coordination = Column(Integer, default=0)
    catching = Column(Integer, default=0)
    
class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    opponent_team = Column(String, nullable=False)
    game_date = Column(DateTime, nullable=False)
    our_score = Column(Integer, default=0)
    opponent_score = Column(Integer, default=0)
    result = Column(String) # "WIN", "LOSE", "DRAW"

    # Game과 GameEvent의 관계 설정
    events = relationship("GameEvent", back_populates="game", cascade="all, delete-orphan")

class GameEvent(Base):
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    event_type = Column(String, nullable=False) # "GOAL" 또는 "ASSIST"

    game = relationship("Game", back_populates="events")
    player = relationship("Player")

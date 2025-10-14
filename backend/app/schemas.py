# backend/app/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Player 관련 스키마
class PlayerBase(BaseModel):
    name: str
    position: Optional[str] = None
    dominant_foot: Optional[str] = None

    # 공통/공격
    stamina: Optional[int] = 0
    speed: Optional[int] = 0
    shooting_accuracy: Optional[int] = 0
    dribbling: Optional[int] = 0
    passing: Optional[int] = 0

    # 공격수/윙어
    finishing: Optional[int] = 0
    crossing: Optional[int] = 0

    # 미드필더
    vision: Optional[int] = 0
    interceptions: Optional[int] = 0

    # 수비수
    tackling: Optional[int] = 0
    heading: Optional[int] = 0

    # 골키퍼
    saving: Optional[int] = 0
    defense_coordination: Optional[int] = 0
    catching: Optional[int] = 0

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int

    class Config:
        orm_mode = True

# Game 관련 스키마
class GameBase(BaseModel):
    opponent_team: str
    game_date: datetime
    our_score: int
    opponent_score: int

# --- 추가된 부분 ---
class PlayerInEvent(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# --- 추가된 부분 ---
class GameEventBase(BaseModel):
    player_id: int
    event_type: str # "GOAL" or "ASSIST"

class GameEventCreate(GameEventBase):
    pass

class GameEvent(BaseModel):
    id: int
    game_id: int
    event_type: str
    player: PlayerInEvent

    class Config:
        orm_mode = True
# --- 추가된 부분 끝 ---
    
class GameCreate(GameBase):
    scorers: list[int] = [] # 득점 선수 ID 리스트
    assisters: list[int] = [] # 도움 선수 ID 리스트

class GameUpdate(GameBase):
    pass

class Game(GameBase):
    id: int
    result: str
    events: list[GameEvent] = [] # 경기 상세 정보 포함

    class Config:
        orm_mode = True

# Gemini 분석 관련 스키마
class AnalysisRequest(BaseModel):
    prompt: str

class AnalysisResponse(BaseModel):
    report: str

# --- 수정된 부분 ---
class FormationRequest(BaseModel):
    opponent_team: str
    opponent_style: Optional[str] = None # opponent_style 필드 추가

# 통계 관련 스키마
class OpponentStats(BaseModel):
    opponent_team: str
    wins: int
    losses: int
    draws: int
    total_games: int

# --- 리더보드 스키마 추가 ---
class PlayerStats(BaseModel):
    player_id: int
    name: str
    goals: int
    assists: int
    points: int # 공격 포인트 (득점 + 도움)
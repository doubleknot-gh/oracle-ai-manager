from sqlalchemy.orm import Session
from sqlalchemy import func, case
from . import models, schemas

# Player CRUD
def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()

def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player(db: Session, player_id: int, player: schemas.PlayerUpdate):
    db_player = get_player(db, player_id)
    if db_player:
        update_data = player.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_player, key, value)
        db.commit()
        db.refresh(db_player)
    return db_player

def delete_player(db: Session, player_id: int):
    db_player = get_player(db, player_id)
    if db_player:
        db.delete(db_player)
        db.commit()
    return db_player

# Game CRUD
def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Game).offset(skip).limit(limit).all()

def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.id == game_id).first()

def create_game(db: Session, game: schemas.GameCreate):
    result = "DRAW"
    if game.our_score > game.opponent_score:
        result = "WIN"
    elif game.our_score < game.opponent_score:
        result = "LOSE"
        
    # game.dict()에서 scorers와 assisters를 제외하고 Game 객체 생성
    game_data = game.dict(exclude={"scorers", "assisters"})
    db_game = models.Game(**game_data, result=result)
    
    db.add(db_game)
    db.flush() # db_game.id를 할당받기 위해 flush

    # 득점(GOAL) 이벤트 생성
    for player_id in game.scorers:
        db.add(models.GameEvent(game_id=db_game.id, player_id=player_id, event_type="GOAL"))
    # 도움(ASSIST) 이벤트 생성
    for player_id in game.assisters:
        db.add(models.GameEvent(game_id=db_game.id, player_id=player_id, event_type="ASSIST"))

    db.commit()
    db.refresh(db_game)
    return db_game

def update_game(db: Session, game_id: int, game: schemas.GameUpdate):
    db_game = get_game(db, game_id)
    if db_game:
        update_data = game.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_game, key, value)
        
        # 점수가 변경되었을 수 있으므로 결과 재계산
        if db_game.our_score > db_game.opponent_score:
            db_game.result = "WIN"
        elif db_game.our_score < db_game.opponent_score:
            db_game.result = "LOSE"
        else:
            db_game.result = "DRAW"
            
        db.commit()
        db.refresh(db_game)
    return db_game

def delete_game(db: Session, game_id: int):
    db_game = get_game(db, game_id)
    if db_game:
        db.delete(db_game)
        db.commit()
    return db_game

# Stats CRUD
def get_stats_by_opponent(db: Session):
    stats = db.query(
        models.Game.opponent_team,
        func.count(models.Game.id).label("total_games"),
        func.sum(case((models.Game.result == 'WIN', 1), else_=0)).label("wins"),
        func.sum(case((models.Game.result == 'LOSE', 1), else_=0)).label("losses"),
        func.sum(case((models.Game.result == 'DRAW', 1), else_=0)).label("draws")
    ).group_by(models.Game.opponent_team).all()
    
    return stats

# --- 추가된 부분 ---
def get_leaderboard_stats(db: Session):
    """선수별 득점, 도움, 공격 포인트를 집계하여 반환합니다."""
    stats = db.query(
        models.Player.id.label("player_id"),
        models.Player.name,
        func.sum(case((models.GameEvent.event_type == 'GOAL', 1), else_=0)).label("goals"),
        func.sum(case((models.GameEvent.event_type == 'ASSIST', 1), else_=0)).label("assists")
    ).outerjoin(models.GameEvent, models.Player.id == models.GameEvent.player_id)\
     .group_by(models.Player.id, models.Player.name)\
     .all()
    
    return stats

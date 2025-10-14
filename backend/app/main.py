import os
from dotenv import load_dotenv

# .env 파일로부터 환경 변수 로드
# backend/ 폴더에 있는 .env 파일을 명시적으로 지정합니다.
# 다른 모듈이 로드되기 전에 가장 먼저 실행되어야 합니다.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, services
from .database import SessionLocal, engine

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Oracle AI Manager & Coach API")

# DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Oracle AI Manager & Coach API에 오신 것을 환영합니다!"}

# --- 선수(Player) API ---
@app.post("/players/", response_model=schemas.Player)
def create_player_api(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    # 중복된 이름이 있는지 확인
    db_player = db.query(models.Player).filter(models.Player.name == player.name).first()
    if db_player:
        raise HTTPException(status_code=400, detail="이미 등록된 선수 이름입니다.")
    
    return crud.create_player(db=db, player=player)

@app.get("/players/", response_model=List[schemas.Player])
def read_players_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = crud.get_players(db, skip=skip, limit=limit)
    return players

@app.put("/players/{player_id}", response_model=schemas.Player)
def update_player_api(player_id: int, player: schemas.PlayerUpdate, db: Session = Depends(get_db)):
    db_player = crud.update_player(db, player_id=player_id, player=player)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

@app.delete("/players/{player_id}", response_model=schemas.Player)
def delete_player_api(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.delete_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# --- 경기(Game) API ---
@app.post("/games/", response_model=schemas.Game)
def create_game_api(game: schemas.GameCreate, db: Session = Depends(get_db)):
    return crud.create_game(db=db, game=game)

@app.get("/games/", response_model=List[schemas.Game])
def read_games_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # events 관계를 함께 로드하기 위해 options 추가
    from sqlalchemy.orm import joinedload, selectinload
    games = db.query(models.Game).options(selectinload(models.Game.events).joinedload(models.GameEvent.player)).order_by(models.Game.game_date.desc()).offset(skip).limit(limit).all()
    return games

@app.put("/games/{game_id}", response_model=schemas.Game)
def update_game_api(game_id: int, game: schemas.GameUpdate, db: Session = Depends(get_db)):
    db_game = crud.update_game(db, game_id=game_id, game=game)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game

@app.delete("/games/{game_id}", response_model=schemas.Game)
def delete_game_api(game_id: int, db: Session = Depends(get_db)):
    db_game = crud.delete_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game

# --- 통계(Stats) API ---
@app.get("/stats/opponents", response_model=List[schemas.OpponentStats])
def read_opponent_stats(db: Session = Depends(get_db)):
    stats = crud.get_stats_by_opponent(db=db)
    return stats

@app.get("/stats/leaderboard", response_model=List[schemas.PlayerStats])
def read_leaderboard_stats(db: Session = Depends(get_db)):
    """선수별 득점, 도움, 공격 포인트 순위를 반환합니다."""
    raw_stats = crud.get_leaderboard_stats(db=db)
    leaderboard = []
    for stat in raw_stats:
        goals = stat.goals or 0
        assists = stat.assists or 0
        leaderboard.append(schemas.PlayerStats(
            player_id=stat.player_id,
            name=stat.name,
            goals=goals,
            assists=assists,
            points=goals + assists
        ))
    return sorted(leaderboard, key=lambda x: x.points, reverse=True)

# --- Gemini AI 분석 API ---
@app.post("/analysis/report", response_model=schemas.AnalysisResponse)
def generate_generic_analysis_report(request: schemas.AnalysisRequest):
    """범용 프롬프트를 사용하여 Gemini 분석을 요청합니다."""
    try:
        report_text = services.generate_text_from_gemini(request.prompt)
        return {"report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API 호출 중 오류 발생: {str(e)}")

@app.post("/games/{game_id}/report", response_model=schemas.AnalysisResponse)
def generate_game_report_api(game_id: int, db: Session = Depends(get_db)):
    """특정 경기 결과를 바탕으로 Gemini 경기 요약 리포트를 생성합니다."""
    db_game = crud.get_game(db, game_id=game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Gemini에게 전달할 프롬프트를 동적으로 생성
    prompt = f"""
    당신은 전문 축구 경기 분석가입니다. 아래 경기 결과를 바탕으로, 우리 팀 'Oracle'의 입장에서 흥미로운 뉴스 기사 스타일의 경기 요약 리포트를 작성해주세요.

    - 경기 날짜: {db_game.game_date.strftime('%Y년 %m월 %d일')}
    - 상대 팀: {db_game.opponent_team}
    - 우리 팀 (Oracle) 득점: {db_game.our_score}
    - 상대 팀 득점: {db_game.opponent_score}
    - 경기 결과: {'승리' if db_game.result == 'WIN' else '패배' if db_game.result == 'LOSE' else '무승부'}

    리포트에는 경기의 전반적인 흐름, 승패의 결정적인 요인, 그리고 마지막에 SNS 공유를 위한 재치있는 해시태그를 3개 이상 포함해주세요.
    """

    try:
        report_text = services.generate_text_from_gemini(prompt)
        return {"report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API 호출 중 오류 발생: {str(e)}")

def _get_player_stats_string(player: models.Player) -> str:
    """선수 객체로부터 유효한 모든 능력치 정보를 문자열로 만듭니다."""
    stats_map = {
        "체력": player.stamina, "속도": player.speed, "슈팅 정확도": player.shooting_accuracy,
        "드리블": player.dribbling, "패스": player.passing, "골 결정력": player.finishing,
        "크로스": player.crossing, "시야": player.vision, "가로채기": player.interceptions,
        "태클": player.tackling, "헤딩": player.heading, "선방 능력": player.saving,
        "수비 조율": player.defense_coordination, "캐칭": player.catching
    }
    
    # 값이 있는 (None이 아닌) 능력치만 필터링하여 문자열로 만듭니다.
    valid_stats = [f"- {name}: {value} / 100" for name, value in stats_map.items() if value is not None]
    
    if not valid_stats:
        return "입력된 능력치 정보가 없습니다."
        
    return "\n".join(valid_stats)

@app.post("/players/{player_id}/analysis", response_model=schemas.AnalysisResponse)
def generate_player_analysis_api(player_id: int, db: Session = Depends(get_db)):
    """특정 선수의 스탯을 기반으로 Gemini 강점/약점 분석 리포트를 생성합니다."""
    db_player = crud.get_player(db, player_id=player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    stats_info = _get_player_stats_string(db_player)

    # Gemini에게 전달할 프롬프트를 동적으로 생성
    prompt = f"""
    당신은 경험 많은 축구 코치입니다. 아래 선수의 능력치를 바탕으로, 이 선수의 강점과 약점을 분석하고, 개선을 위한 구체적인 훈련 방법을 추천해주세요.
    분석 내용은 선수가 직접 읽는다고 생각하고, 친근하고 동기부여가 되는 말투로 작성해주세요.

    - 선수 이름: {db_player.name}
    - 포지션: {db_player.position}
    - 주발: {db_player.dominant_foot}
    {stats_info}

    결과는 '강점', '약점', '추천 훈련법' 세 가지 항목으로 명확하게 구분해서 설명해줘.
    """

    try:
        report_text = services.generate_text_from_gemini(prompt)
        return {"report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API 호출 중 오류 발생: {str(e)}")

@app.post("/analysis/formation", response_model=schemas.AnalysisResponse)
def generate_formation_recommendation_api(request: schemas.FormationRequest, db: Session = Depends(get_db)):
    """상대팀과 우리팀 선수 명단을 기반으로 최적 포메이션을 추천합니다."""
    
    # 1. 우리 팀 전체 선수 정보 가져오기
    all_players = crud.get_players(db, limit=100)
    if not all_players:
        raise HTTPException(status_code=404, detail="등록된 선수가 없습니다.")

    player_list_str = "\n".join([f"### {p.name}\n- 포지션: {p.position}\n{_get_player_stats_string(p)}\n" for p in all_players])

    # 2. 상대팀 정보 가져오기 (간단한 전적)
    opponent_stats_list = crud.get_stats_by_opponent(db)
    opponent_stat = next((s for s in opponent_stats_list if s.opponent_team == request.opponent_team), None)
    
    opponent_info_str = f"상대팀 '{request.opponent_team}'은(는) 우리와 총 {opponent_stat.total_games}번 붙어서 {opponent_stat.wins}승 {opponent_stat.draws}무 {opponent_stat.losses}패를 기록했습니다." if opponent_stat else f"상대팀 '{request.opponent_team}'과(와)는 첫 경기입니다."

    # 사용자가 입력한 상대팀 전술 스타일 정보 추가
    opponent_style_info = ""
    if request.opponent_style:
        opponent_style_info = f"3. **상대팀 예상 전술 스타일**: {request.opponent_style}"

    # 3. Gemini에게 전달할 프롬프트 생성
    prompt = f"""
    당신은 펩 과르디올라와 같은 세계적인 축구 전술가입니다. 아마추어 축구팀 'Oracle'의 다음 경기를 위해 최적의 포메이션과 선발 라인업을 추천해주세요.

    ## 분석 정보
    1. **상대팀 정보**: {opponent_info_str}
    {opponent_style_info}
    2. **우리팀 선수 명단 및 능력치**:
    {player_list_str}

    ## 요청 사항
    위 정보를 바탕으로, 다음 항목들을 추천해주세요.
    1. **추천 포메이션**: (예: 4-3-3) 그 이유를 간단히 설명해주세요.
    2. **선발 라인업**: 추천 포메이션에 맞춰 각 포지션에 어떤 선수를 배치할지 이름과 이유를 설명해주세요.
    3. **핵심 전술**: 이 경기에서 우리 팀이 집중해야 할 핵심 전술 포인트를 2~3가지 짚어주세요.
    """

    try:
        recommendation = services.generate_text_from_gemini(prompt)
        return {"report": recommendation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API 호출 중 오류 발생: {str(e)}")

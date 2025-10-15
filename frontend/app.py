import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 백엔드 API 주소
BACKEND_URL = "https://oracle-ai-manager.onrender.com"

st.set_page_config(page_title="Oracle AI Manager", layout="wide")

# --- 디자인 커스텀 CSS ---
def set_custom_style():
    st.markdown("""
        <style>
        /* 전체 배경: 분홍색-하늘색 그라데이션 */
        .stApp {
            background-image: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
            background-attachment: fixed;
            background-size: cover;
            color: #2c3e50; /* 기본 텍스트 색상을 어두운 회색으로 변경 */
        }

        /* 메인 타이틀 스타일 */
        h1 {
            color: #34495e; /* 어두운 남색 계열로 변경 */
            text-shadow: 1px 1px 2px rgba(255,255,255,0.7);
        }

        /* 헤더, 서브헤더 색상 */
        h2, h3 {
            color: #34495e; /* 타이틀과 동일한 색상으로 통일 */
        }
        
        /* 사이드바 스타일 (밝은 테마에 맞게 수정) */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.5); /* 반투명 흰색 배경 */
            backdrop-filter: blur(10px); /* 블러 효과 강화 */
            border-right: 1px solid rgba(44, 62, 80, 0.1); /* 어두운 테두리 선 */
        }
        </style>
    """, unsafe_allow_html=True)

set_custom_style()

st.title("⚽ Oracle AI Manager & Coach")

# --- 사이드바 ---
st.sidebar.header("메뉴")
menu = st.sidebar.radio("페이지 선택", ["선수 관리", "경기 기록", "팀 분석", "리더보드"])

# --- 선수 관리 페이지 ---
if menu == "선수 관리":
    st.header("👨‍👩‍👧‍👦 선수 관리")
    
    # 선수 등록 폼
    with st.form("player_form"):
        st.subheader("📝 신규 선수 등록")
        name = st.text_input("이름")
        
        # 세분화된 포지션 목록
        detailed_positions = [
            "GK", "LCB", "RCB", "LB", "RB", # 수비
            "DM", "CM", "AM", # 미드필더
            "LW", "RW", "CF"  # 공격수
        ]
        position = st.selectbox("세부 포지션", detailed_positions)
        dominant_foot = st.selectbox("주발", ["오른발", "왼발", "양발"])

        player_data = {"name": name, "position": position, "dominant_foot": dominant_foot}

        st.write("**포지션별 주요 능력치**")
        # 포지션별로 다른 능력치 슬라이더 표시
        if position == "GK":
            player_data["saving"] = st.slider("선방 능력", 1, 100, 50)
            player_data["defense_coordination"] = st.slider("수비 조율", 1, 100, 50)
            player_data["catching"] = st.slider("캐칭", 1, 100, 50)
        elif "CB" in position:
            player_data["tackling"] = st.slider("태클", 1, 100, 50)
            player_data["heading"] = st.slider("헤딩", 1, 100, 50)
            player_data["speed"] = st.slider("속도", 1, 100, 50)
        elif "LB" in position or "RB" in position:
            player_data["stamina"] = st.slider("체력", 1, 100, 50)
            player_data["speed"] = st.slider("속도", 1, 100, 50)
            player_data["crossing"] = st.slider("크로스", 1, 100, 50)
        elif "DM" in position:
            player_data["interceptions"] = st.slider("가로채기", 1, 100, 50)
            player_data["passing"] = st.slider("패스", 1, 100, 50)
            player_data["stamina"] = st.slider("체력", 1, 100, 50)
        elif "CM" in position:
            player_data["passing"] = st.slider("패스", 1, 100, 50)
            player_data["vision"] = st.slider("시야", 1, 100, 50)
            player_data["dribbling"] = st.slider("드리블", 1, 100, 50)
        elif "AM" in position:
            player_data["vision"] = st.slider("시야", 1, 100, 50)
            player_data["shooting_accuracy"] = st.slider("슈팅 정확도", 1, 100, 50)
            player_data["dribbling"] = st.slider("드리블", 1, 100, 50)
        elif "W" in position: # LW, RW
            player_data["speed"] = st.slider("속도", 1, 100, 50)
            player_data["dribbling"] = st.slider("드리블", 1, 100, 50)
            player_data["crossing"] = st.slider("크로스", 1, 100, 50)
        elif "CF" in position:
            player_data["finishing"] = st.slider("골 결정력", 1, 100, 50)
            player_data["heading"] = st.slider("헤딩", 1, 100, 50)
            player_data["shooting_accuracy"] = st.slider("슈팅 정확도", 1, 100, 50)
        else:
            player_data["stamina"] = st.slider("체력", 1, 100, 50)
            player_data["speed"] = st.slider("속도", 1, 100, 50)
            player_data["shooting_accuracy"] = st.slider("슈팅 정확도", 1, 100, 50)
        
        submitted = st.form_submit_button("등록")
        if submitted:
            response = requests.post(f"{BACKEND_URL}/players/", json=player_data)
            if response.status_code == 200:
                st.success("선수가 성공적으로 등록되었습니다!")
            else:
                st.error(f"선수 등록 실패: {response.text}")

    st.divider()

    # 선수 목록 및 수정/삭제 (UI는 간단하게 모든 스탯을 보여주도록 유지)
    st.subheader("📋 선수 목록 및 관리")
    try:
        response = requests.get(f"{BACKEND_URL}/players/")
        if response.status_code == 200:
            players = response.json()
            if players:
                df_players = pd.DataFrame(players)
                # 모든 스탯 컬럼을 포함하여 표시
                display_cols = ['id', 'name', 'position', 'dominant_foot', 'stamina', 'speed', 
                                'shooting_accuracy', 'dribbling', 'passing', 'finishing', 
                                'crossing', 'vision', 'interceptions', 'tackling', 'heading',
                                'saving', 'defense_coordination', 'catching']
                # 데이터프레임에 존재하지 않는 컬럼이 있을 경우를 대비하여 안전하게 필터링
                existing_cols = [col for col in display_cols if col in df_players.columns]
                st.dataframe(df_players[existing_cols], use_container_width=True)

                # ID와 이름을 조합하여 고유한 선택 옵션 생성
                player_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in players}
                selected_player_key = st.selectbox("수정 또는 삭제할 선수를 선택하세요", player_options.keys())

                if selected_player_key:
                    player_id = player_options[selected_player_key]
                    selected_player = next((p for p in players if p['id'] == player_id), None)
                    
                    with st.form(f"edit_player_{player_id}"):
                        st.subheader(f"'{selected_player['name']}' 선수 정보 수정")
                        
                        # --- 수정된 부분 시작 ---
                        
                        # 기본 정보 수정
                        edit_name = st.text_input("이름", value=selected_player.get('name', ''))
                        
                        detailed_positions = [
                            "GK", "LCB", "RCB", "LB", "RB", "DM", "CM", "AM", "LW", "RW", "CF"
                        ]
                        current_pos_index = detailed_positions.index(selected_player['position']) if selected_player.get('position') in detailed_positions else 0
                        edit_position = st.selectbox("포지션", detailed_positions, index=current_pos_index, key=f"pos_{player_id}")
                        
                        foot_options = ["오른발", "왼발", "양발"]
                        current_foot_index = foot_options.index(selected_player['dominant_foot']) if selected_player.get('dominant_foot') in foot_options else 0
                        edit_dominant_foot = st.selectbox("주발", foot_options, index=current_foot_index, key=f"foot_{player_id}")

                        st.write("**능력치 수정**")
                        # 모든 능력치 슬라이더를 표시하여 수정 가능하도록 변경
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_stamina = st.slider("체력", 1, 100, selected_player.get('stamina', 50))
                            edit_speed = st.slider("속도", 1, 100, selected_player.get('speed', 50))
                            edit_shooting_accuracy = st.slider("슈팅 정확도", 1, 100, selected_player.get('shooting_accuracy', 50))
                            edit_dribbling = st.slider("드리블", 1, 100, selected_player.get('dribbling', 50))
                            edit_passing = st.slider("패스", 1, 100, selected_player.get('passing', 50))
                            edit_finishing = st.slider("골 결정력", 1, 100, selected_player.get('finishing', 50))
                            edit_crossing = st.slider("크로스", 1, 100, selected_player.get('crossing', 50))
                            edit_vision = st.slider("시야", 1, 100, selected_player.get('vision', 50))
                        with col2:
                            edit_interceptions = st.slider("가로채기", 1, 100, selected_player.get('interceptions', 50))
                            edit_tackling = st.slider("태클", 1, 100, selected_player.get('tackling', 50))
                            edit_heading = st.slider("헤딩", 1, 100, selected_player.get('heading', 50))
                            edit_saving = st.slider("선방 능력 (GK)", 1, 100, selected_player.get('saving', 50))
                            edit_defense_coordination = st.slider("수비 조율 (GK)", 1, 100, selected_player.get('defense_coordination', 50))
                            edit_catching = st.slider("캐칭 (GK)", 1, 100, selected_player.get('catching', 50))

                        update_submitted = st.form_submit_button("정보 수정하기")
                        if update_submitted:
                            # 수정된 모든 정보를 포함하는 payload 생성
                            update_data = {
                                "name": edit_name,
                                "position": edit_position,
                                "dominant_foot": edit_dominant_foot,
                                "stamina": edit_stamina,
                                "speed": edit_speed,
                                "shooting_accuracy": edit_shooting_accuracy,
                                "dribbling": edit_dribbling,
                                "passing": edit_passing,
                                "finishing": edit_finishing,
                                "crossing": edit_crossing,
                                "vision": edit_vision,
                                "interceptions": edit_interceptions,
                                "tackling": edit_tackling,
                                "heading": edit_heading,
                                "saving": edit_saving,
                                "defense_coordination": edit_defense_coordination,
                                "catching": edit_catching
                            }
                            res = requests.put(f"{BACKEND_URL}/players/{player_id}", json=update_data)
                            if res.status_code == 200:
                                st.success("선수 정보가 성공적으로 수정되었습니다. 페이지를 새로고침하면 반영됩니다.")
                                st.rerun() # 수정 후 바로 새로고침
                            else:
                                st.error(f"수정 실패: {res.text}")
                        
                        # --- 수정된 부분 끝 ---
                
                st.divider()
                st.subheader("🤖 AI 선수 분석 리포트")

                # 분석을 위한 선수 선택
                analysis_player_key = st.selectbox("분석할 선수를 선택하세요", player_options.keys(), key="analysis_select")

                if st.button("분석 리포트 생성하기"):
                    if analysis_player_key:
                        player_id_for_analysis = player_options[analysis_player_key]
                        analysis_player_name = analysis_player_key.split(" (ID:")[0]
                        with st.spinner(f"{analysis_player_name} 선수의 데이터를 AI가 분석 중입니다..."):
                            res = requests.post(f"{BACKEND_URL}/players/{player_id_for_analysis}/analysis")
                            if res.status_code == 200:
                                report_data = res.json()
                                st.success("분석이 완료되었습니다!")
                                st.markdown("---")
                                st.markdown(report_data['report'])
                            else:
                                st.error(f"분석 실패: {res.text}")
            else:
                st.info("등록된 선수가 없습니다.")
        else:
            st.error("선수 목록을 불러오는 데 실패했습니다.")
    except requests.exceptions.ConnectionError:
        st.error("백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")


# --- 경기 기록 페이지 ---
elif menu == "경기 기록":
    st.header("📊 경기 기록")

    # 선수 목록을 가져와서 선택지에 사용
    players = []
    player_options = {}
    try:
        player_res = requests.get(f"{BACKEND_URL}/players/")
        if player_res.status_code == 200:
            players = player_res.json()
            player_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in players}
    except requests.exceptions.ConnectionError:
        st.warning("선수 목록을 불러올 수 없습니다. 백엔드 연결을 확인하세요.")

    # 경기 결과 입력 폼
    with st.form("game_form"):
        st.subheader("📝 경기 결과 입력")
        opponent_team = st.text_input("상대 팀 이름")
        game_date = st.date_input("경기 날짜")
        our_score = st.number_input("우리 팀 득점", min_value=0, step=1)
        opponent_score = st.number_input("상대 팀 득점", min_value=0, step=1)
        
        scorers = st.multiselect("득점 선수", options=player_options.keys())
        assisters = st.multiselect("도움 선수", options=player_options.keys())

        submitted = st.form_submit_button("기록")
        if submitted:
            game_data = {
                "opponent_team": opponent_team,
                "game_date": game_date.isoformat() + "T00:00:00", # 시간 정보 추가
                "our_score": our_score,
                "opponent_score": opponent_score,
                "scorers": [player_options[name] for name in scorers],
                "assisters": [player_options[name] for name in assisters]
            }
            response = requests.post(f"{BACKEND_URL}/games/", json=game_data)
            if response.status_code == 200:
                st.success("경기 결과가 성공적으로 기록되었습니다!")
            else:
                st.error(f"경기 기록 실패: {response.text}")

    st.divider()

    # 최근 경기 전적 및 수정/삭제
    st.subheader("📈 최근 경기 전적 및 관리")
    try:
        response = requests.get(f"{BACKEND_URL}/games/")
        if response.status_code == 200:
            games = response.json()
            if games:
                df_games = pd.DataFrame(games)

                # 득점 및 도움 선수 정보 처리
                scorers_list = []
                assisters_list = []
                for game in games:
                    scorers = [event['player']['name'] for event in game['events'] if event['event_type'] == 'GOAL']
                    assisters = [event['player']['name'] for event in game['events'] if event['event_type'] == 'ASSIST']
                    scorers_list.append(", ".join(scorers))
                    assisters_list.append(", ".join(assisters))
                
                df_games['득점'] = scorers_list
                df_games['도움'] = assisters_list
                df_games['game_date_only'] = pd.to_datetime(df_games['game_date']).dt.date
                st.dataframe(df_games[['id', 'game_date_only', 'opponent_team', 'our_score', 'opponent_score', 'result', '득점', '도움']], use_container_width=True)

                game_options = {f"{pd.to_datetime(g['game_date']).date()} vs {g['opponent_team']} (ID: {g['id']})": g['id'] for g in games}
                selected_game_key = st.selectbox("수정 또는 삭제할 경기를 선택하세요", game_options.keys())

                if selected_game_key:
                    game_id = game_options[selected_game_key]
                    selected_game = next((g for g in games if g['id'] == game_id), None)

                    with st.form(f"edit_game_{game_id}"):
                        st.subheader(f"'{selected_game_key}' 경기 정보 수정")
                        edit_opponent = st.text_input("상대 팀", value=selected_game['opponent_team'])
                        edit_date = st.date_input("경기 날짜", value=pd.to_datetime(selected_game['game_date']).date())
                        edit_our_score = st.number_input("우리 팀 득점", min_value=0, step=1, value=selected_game['our_score'])
                        edit_opponent_score = st.number_input("상대 팀 득점", min_value=0, step=1, value=selected_game['opponent_score'])

                        col1, col2 = st.columns(2)
                        with col1:
                            update_submitted = st.form_submit_button("수정하기")
                        with col2:
                            delete_submitted = st.form_submit_button("삭제하기", type="primary")

                        if update_submitted:
                            updated_data = {
                                "opponent_team": edit_opponent, "game_date": edit_date.isoformat() + "T00:00:00",
                                "our_score": edit_our_score, "opponent_score": edit_opponent_score
                            }
                            res = requests.put(f"{BACKEND_URL}/games/{game_id}", json=updated_data)
                            if res.status_code == 200:
                                st.success("경기 정보가 수정되었습니다. 페이지를 새로고침하세요.")
                            else:
                                st.error("수정 실패!")
                        
                        if delete_submitted:
                            res = requests.delete(f"{BACKEND_URL}/games/{game_id}")
                            if res.status_code == 200:
                                st.success("경기 정보가 삭제되었습니다. 페이지를 새로고침하세요.")
                            else:
                                st.error("삭제 실패!")
                
                st.divider()
                st.subheader("🤖 AI 경기 리포트 생성")
                
                # 리포트 생성을 위한 경기 선택
                report_game_key = st.selectbox("리포트를 생성할 경기를 선택하세요", game_options.keys(), key="report_select")
                
                if st.button("리포트 생성하기"):
                    if report_game_key:
                        game_id_for_report = game_options[report_game_key]
                        with st.spinner("Gemini AI가 경기 리포트를 생성 중입니다... 잠시만 기다려주세요."):
                            report_res = requests.post(f"{BACKEND_URL}/games/{game_id_for_report}/report")
                            if report_res.status_code == 200:
                                report_data = report_res.json()
                                st.success("리포트 생성이 완료되었습니다!")
                                st.markdown("---")
                                st.markdown(report_data['report'])
                            else:
                                st.error(f"리포트 생성 실패: {report_res.text}")
            else:
                st.info("기록된 경기가 없습니다.")
        else:
            st.error("경기 기록을 불러오는 데 실패했습니다.")
    except requests.exceptions.ConnectionError:
        st.error("백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")

# --- 팀 분석 페이지 ---
elif menu == "팀 분석":
    st.header("🔍 팀 분석")

    st.subheader("🆚 상대별 전적")
    try:
        response = requests.get(f"{BACKEND_URL}/stats/opponents")
        if response.status_code == 200:
            stats = response.json()
            if stats:
                df_stats = pd.DataFrame(stats)
                df_stats.rename(columns={
                    'opponent_team': '상대 팀',
                    'total_games': '총 경기',
                    'wins': '승',
                    'losses': '패',
                    'draws': '무'
                }, inplace=True)
                st.dataframe(df_stats[['상대 팀', '총 경기', '승', '패', '무']])
            else:
                st.info("분석할 경기 기록이 없습니다.")
        else:
            st.error("상대별 전적을 불러오는 데 실패했습니다.")
    except requests.exceptions.ConnectionError:
        st.error("백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")

    st.divider()
    st.subheader("🎯 AI 전술 추천")

    col1, col2 = st.columns(2)
    with col1:
        opponent_team_for_tactic = st.text_input("상대 팀 이름")
    with col2:
        opponent_style_for_tactic = st.text_area("상대 팀 전술 스타일 (선택 사항)", placeholder="예: 빠른 역습 위주, 4-4-2 포메이션 사용, 측면 공격이 강함")

    if st.button("최적 포메이션 추천받기"):
        if opponent_team_for_tactic:
            with st.spinner(f"'{opponent_team_for_tactic}' 팀을 상대로 한 최적의 전술을 AI가 분석 중입니다..."):
                req_data = {"opponent_team": opponent_team_for_tactic, "opponent_style": opponent_style_for_tactic}
                res = requests.post(f"{BACKEND_URL}/analysis/formation", json=req_data)
                if res.status_code == 200:
                    tactic_data = res.json()
                    st.success("전술 분석이 완료되었습니다!")
                    st.markdown("---")
                    st.markdown(tactic_data['report'])
                else:
                    st.error(f"전술 추천 실패: {res.text}")
        else:
            st.warning("상대 팀 이름을 입력해주세요.")

# --- 리더보드 페이지 ---
elif menu == "리더보드":
    st.header("🏆 팀 내 개인 순위")

    try:
        response = requests.get(f"{BACKEND_URL}/stats/leaderboard")
        if response.status_code == 200:
            leaderboard_data = response.json()
            if leaderboard_data:
                df_leaderboard = pd.DataFrame(leaderboard_data)
                df_leaderboard.rename(columns={
                    'name': '선수명',
                    'goals': '득점',
                    'assists': '도움',
                    'points': '공격 포인트'
                }, inplace=True)

                st.subheader("🎯 공격 포인트 순위 (득점 + 도움)")
                st.dataframe(
                    df_leaderboard[['선수명', '공격 포인트', '득점', '도움']].sort_values(by="공격 포인트", ascending=False).reset_index(drop=True),
                    use_container_width=True
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("⚽ 득점 순위")
                    st.dataframe(df_leaderboard[['선수명', '득점']].sort_values(by="득점", ascending=False).reset_index(drop=True), use_container_width=True)
                with col2:
                    st.subheader("🤝 도움 순위")
                    st.dataframe(df_leaderboard[['선수명', '도움']].sort_values(by="도움", ascending=False).reset_index(drop=True), use_container_width=True)

            else:
                st.info("아직 득점 또는 도움 기록이 없습니다.")
        else:
            st.error("리더보드 데이터를 불러오는 데 실패했습니다.")
    except requests.exceptions.ConnectionError:
        st.error("백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
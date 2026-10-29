import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import re

# 페이지 기본 설정
st.set_page_config(
    page_title="유튜브 인기 댓글 찾기",
    page_icon="💬",
    layout="centered"
)

# 화면 상단 디자인
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #DC2626;'>💬 유튜브 인기 댓글 찾기</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280;'>영상 링크를 넣으면 좋아요가 많은 댓글을 찾아줘요.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 입력 폼 박스 생성
with st.container():
    st.markdown("---")
    video_url = st.text_input("유튜브 영상 링크", placeholder="https://www.youtube.com/watch?v=...")
    api_key = st.text_input("YouTube Data API 키", type="password", placeholder="API 키를 입력하세요")
    max_comments = st.slider("확인할 댓글 수", min_value=10, max_value=200, value=100, step=10)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 실행 버튼
    search_button = st.button("🔍 인기 댓글 찾기", type="primary", use_container_width=True)

def extract_video_id(url):
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else None

if search_button:
    if not video_url or not api_key:
        st.warning("⚠️ 유튜브 영상 링크와 API 키를 모두 입력해 주세요!")
    else:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("❌ 올바른 유튜브 영상 링크가 아닙니다. 다시 확인해 주세요.")
        else:
            try:
                with st.spinner("🔄 유튜브에서 댓글을 불러오는 중입니다..."):
                    youtube = build('youtube', 'v3', developerKey=api_key)
                    
                    response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=max_comments,
                        order='relevance',
                        textFormat='plainText'
                    ).execute()
                    
                    comments_data = []
                    for item in response.get('items', []):
                        snippet = item['snippet']['topLevelComment']['snippet']
                        comments_data.append({
                            '작성자': snippet['authorDisplayName'],
                            '댓글 내용': snippet['textDisplay'],
                            '좋아요 수': snippet['likeCount']
                        })
                    
                    df = pd.DataFrame(comments_data)
                    df = df.sort_values(by='좋아요 수', ascending=False).reset_index(drop=True)
                
                st.success("✨ 인기 댓글 분석 완료!")
                st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ 에러가 발생했습니다. API 키나 링크를 확인해 주세요.\n세부 에러: {e}")

st.markdown("---")

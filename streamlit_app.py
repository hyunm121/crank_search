import streamlit as st
import re
import html
from collections import Counter
from selenium_blog_scraper import fetch_blog_posts_with_selenium

# 불용어 리스트 (한국어)
STOPWORDS = {
    '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '그래서',
    '때문에', '위해', '통해', '대해', '관련', '이런', '저런', '그런', '이러한',
    '저러한', '그러한', '이런', '저런', '그런', '이것', '저것', '그것', '이런',
    '저런', '그런', '이런', '저런', '그런', '이런', '저런', '그런'
}

# ✅ 기본 설정
st.set_page_config(page_title="유입 게시물 리스트", layout="centered")
st.title("🔍 이 검색어로 유입된 게시물")

# ▶ 세션 상태 초기화
if "results" not in st.session_state:
    st.session_state.results = []
if "keywords_split" not in st.session_state:
    st.session_state.keywords_split = []
if "selected_keywords" not in st.session_state:
    st.session_state.selected_keywords = []
if "recommended_keywords" not in st.session_state:
    st.session_state.recommended_keywords = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "error_message" not in st.session_state:
    st.session_state.error_message = None

def clean_text(text):
    """텍스트 정제 함수"""
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 특수문자 제거 (한글, 영문, 숫자만 남김)
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_recommended_keywords(titles, search_keywords, top_n=2):
    # 모든 제목을 하나의 텍스트로 합치기
    combined_text = ' '.join(clean_text(title) for title in titles)
    
    # 단어 분리 (2글자 이상만 추출)
    words = re.findall(r'[가-힣a-zA-Z0-9]{2,}', combined_text)
    
    # 검색 키워드와 불용어 제외
    filtered_words = []
    for word in words:
        # 이 단어가 검색 키워드의 부분 문자열이거나 불용어인지 확인
        is_excluded = False
        for search_kw in search_keywords:
            if word in search_kw or search_kw in word:
                is_excluded = True
                break
        if not is_excluded and word not in STOPWORDS:
            filtered_words.append(word)
    
    # 가장 많이 등장한 단어 추출
    word_counts = Counter(filtered_words)
    top_keywords = word_counts.most_common(top_n)
    
    return [word for word, _ in top_keywords]

# ▶ 검색 실행 함수
def do_search(search_keyword):
    if not search_keyword.strip():
        st.session_state.error_message = "검색어를 입력해주세요."
        return
        
    try:
        with st.spinner("스크래핑 중..."):
            results = fetch_blog_posts_with_selenium(search_keyword, count=10)
            if not results:
                st.session_state.error_message = "검색 결과가 없습니다."
                return
                
            st.session_state.results = results
            st.session_state.keywords_split = [k.strip() for k in search_keyword.split() if k.strip()]
            st.session_state.selected_keywords = []
            st.session_state.error_message = None
            
            # 상위 5개 게시물에서 추천 키워드 추출
            top_5_titles = [post['title'] for post in results[:5]]
            st.session_state.recommended_keywords = extract_recommended_keywords(
                top_5_titles, 
                st.session_state.keywords_split
            )
            
            # 검색 히스토리에 추가
            if search_keyword not in st.session_state.search_history:
                st.session_state.search_history.insert(0, search_keyword)
                if len(st.session_state.search_history) > 10:
                    st.session_state.search_history.pop()
    except Exception as e:
        st.session_state.error_message = f"검색 중 오류가 발생했습니다: {str(e)}"

# ▶ 검색어 입력
col1, col2 = st.columns([6, 1])
with col1:
    keyword = st.text_input(
        "검색어를 입력하세요",
        key="search_input",
        label_visibility="collapsed",
        placeholder="검색어를 입력하세요..."
    )
with col2:
    search_button = st.button("검색", use_container_width=True)

# 오류 메시지 표시
if st.session_state.error_message:
    st.error(st.session_state.error_message)

# 검색 실행 (엔터키 또는 검색 버튼)
if search_button or keyword:
    if keyword != st.session_state.get('last_search', ''):
        st.session_state.last_search = keyword
        do_search(keyword)

# ▶ 키워드 강조 함수 (배경색 + 글자색)
def highlight_keywords(title, search_keywords_with_colors, recommend_keywords_with_colors):
    title = html.escape(title)
    
    # 검색 키워드 (배경색)
    for word, color in search_keywords_with_colors:
        title = re.sub(
            f"({re.escape(word)})",
            rf"<span style='background-color:{color};'>\1</span>",
            title,
            flags=re.IGNORECASE
        )
    
    # 추천 키워드 (글자색 + 볼드)
    for word, color in recommend_keywords_with_colors:
        title = re.sub(
            f"({re.escape(word)})",
            rf"<span style='color:{color}; font-weight:bold;'>\1</span>",
            title,
            flags=re.IGNORECASE
        )
    
    return title

# ▶ 결과 + 키워드 강조 UI
if st.session_state.results:
    # 컬러맵 정의
    search_color_map = {
        0: "#FFA500",  # 주황
        1: "#FFFF00",  # 노랑
        2: "#00FF00",  # 초록
        3: "#FF69B4",  # 분홍
    }
    recommend_color_map = {
        0: "#FF0000",  # 빨간색
        1: "#0000FF",  # 파란색
    }

    # 검색 키워드 체크박스 UI (사이드바)
    st.sidebar.markdown("### 검색 키워드")
    search_selected = []
    for k in st.session_state.keywords_split:
        if st.sidebar.checkbox(k, key=f"search_kw_{k}"):
            search_selected.append(k)

    # 추천 키워드 체크박스 UI (사이드바)
    if st.session_state.recommended_keywords:
        st.sidebar.markdown("### 추천 키워드")
        recommend_selected = []
        for k in st.session_state.recommended_keywords:
            if st.sidebar.checkbox(k, key=f"recommend_kw_{k}"):
                recommend_selected.append(k)
    else:
        recommend_selected = []

    # 선택된 키워드들 저장
    st.session_state.selected_keywords = search_selected + recommend_selected

    # 출력 리스트
    st.markdown("### [상위 블로그 게시물]")
    for post in st.session_state.results:
        title = post["title"]
        if st.session_state.selected_keywords:
            # 검색 키워드와 색상 매핑 (배경색)
            search_keywords_with_colors = [
                (k, search_color_map.get(idx, "#FFA500"))
                for idx, k in enumerate(search_selected)
            ]
            
            # 추천 키워드와 색상 매핑 (글자색)
            recommend_keywords_with_colors = [
                (k, recommend_color_map.get(idx, "#FF0000"))
                for idx, k in enumerate(recommend_selected)
            ]
            
            title = highlight_keywords(
                title, 
                search_keywords_with_colors,
                recommend_keywords_with_colors
            )

        # 링크: 검정색 + 밑줄 제거
        st.markdown(
            f"<a href='{post['link']}' target='_blank' style='text-decoration:none; color:black;'>{post['rank']}. {title}</a>",
            unsafe_allow_html=True
        )

# ▶ 검색 히스토리 표시 (사이드바 하단)
if st.session_state.search_history:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 최근 검색어")
    for hist_keyword in st.session_state.search_history:
        if st.sidebar.button(f"🔍 {hist_keyword}", key=f"history_{hist_keyword}"):
            st.session_state.search_input = hist_keyword
            st.session_state.last_search = hist_keyword
            do_search(hist_keyword)

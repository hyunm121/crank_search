# 📰 자동 기사 크롤링 & 분석 도구

🚀 **Live Demo**: [여기서 바로 사용해보기](https://hyunm121-crank-search.streamlit.app)

이 도구는 네이버 뉴스, 뉴시스, 연합뉴스 등 주요 포털에서
기사 링크를 입력하면 자동으로 제목과 본문을 추출하고,
깨끗하게 정리된 `.txt` 파일로 저장해줍니다.

# 네이버 블로그 검색 및 분석 도구

이 프로젝트는 네이버에 키워드를 검색하고, 상단에 노출된 블로그 제목을 분석하는 도구입니다. Selenium을 사용하여 웹 스크래핑을 수행하고, Streamlit을 통해 사용자 친화적인 인터페이스를 제공합니다.

## 기능

- 네이버 블로그 검색 결과 스크래핑
- 검색 결과 제목 분석 및 추천 키워드 추출
- 사용자 친화적인 웹 인터페이스 제공

## 설치 방법

1. 저장소를 클론합니다.

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. 필요한 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```

## 사용 방법

1. Streamlit 앱을 실행합니다.

   ```bash
   streamlit run streamlit_blog_ui.py
   ```

2. 웹 브라우저에서 제공되는 URL(보통 http://localhost:8501/)을 열어 앱을 사용합니다.

3. 검색어를 입력하고 검색 버튼을 클릭하여 결과를 확인합니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

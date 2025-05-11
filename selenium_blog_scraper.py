from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_blog_posts_with_selenium(keyword, count=20):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 10)  # 최대 10초 대기

        search_url = (
            "https://search.naver.com/search.naver"
            f"?query={keyword}"
            "&ssc=tab.blog.all"
            "&sm=tab_jum"
            "&where=post"
        )
        
        driver.get(search_url)
        
        # 명시적 대기로 요소가 로드될 때까지 기다림
        item_selector = (
            "#main_pack > section.sc_new.sp_nblog._fe_view_root._prs_blg._sp_nblog "
            "> div.api_subject_bx > ul > li > div > div.detail_box "
            "> div.title_area > a"
        )
        
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, item_selector)))
        except TimeoutException:
            logger.warning("검색 결과를 찾을 수 없습니다.")
            return []

        elems = driver.find_elements(By.CSS_SELECTOR, item_selector)
        posts = []
        for idx, elem in enumerate(elems, start=1):
            if idx > count:
                break
            try:
                title = elem.text
                link = elem.get_attribute("href")
                if title and link:  # 제목과 링크가 모두 있는 경우만 추가
                    posts.append({"rank": idx, "title": title, "link": link})
            except Exception as e:
                logger.error(f"게시물 정보 추출 중 오류 발생: {str(e)}")
                continue

        return posts

    except WebDriverException as e:
        logger.error(f"웹드라이버 오류 발생: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {str(e)}")
        return []
    finally:
        try:
            driver.quit()
        except:
            pass

# 직접 실행 시 테스트
if __name__ == "__main__":
    try:
        kw = input("검색어를 입력하세요: ")
        if not kw.strip():
            print("검색어를 입력해주세요.")
        else:
            results = fetch_blog_posts_with_selenium(kw, count=10)
            if results:
                print("\n[상위 블로그 게시물]")
                for p in results:
                    print(f"{p['rank']:>2}. {p['title']} → {p['link']}")
            else:
                print("검색 결과가 없습니다.")
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

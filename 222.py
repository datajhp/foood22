import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import json
from pathlib import Path
import streamlit.components.v1 as components
import datetime
import random
import pytz

st.set_page_config(page_title="오늘의 메뉴's",page_icon="🍴")

kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst)
today_date = now_kst.date()

st.title("🍽️오늘의 메뉴's🍽️")
st.subheader(f"{today_date}")


# 카카오톡 채널 URL 2개
url1 = "https://pf.kakao.com/_CiVis/posts"
url2 = "https://pf.kakao.com/_vKxgdn/posts"
url3 = "https://blog.naver.com/PostList.nhn?blogId=jusik1606&from=postList&categoryNo=6"
url4 = "https://blog.naver.com/dawafood-qubi"


# 2개의 열로 나누기
col1, col2 = st.columns(2)

# 첫 번째 열에 URL1 임베딩
with col1:
    st.subheader("📌 슈마우스만찬")
    components.iframe(url1, height=600, width=1000)
# 두 번째 열에 URL2 임베딩
with col2:
    st.subheader("     📌 정담식당")
    components.iframe(url2, height=600, width=1000)

col3, col4 = st.columns(2)
with col3:
    st.subheader("📌 만나")
    st.markdown(
        f"""
     <div style="width: 650px; height: 700px; overflow: hidden;">
         <iframe src="{url3}" width="800" height="1500" 
                 style="transform: scale(0.44); transform-origin: 0 0;">
         </iframe>
     </div>
     """,
     unsafe_allow_html=True
    )  
with col4:
    st.subheader("     📌 다와푸드 큐비")
    st.markdown(
            f"""
     <div style="width: 650px; height: 700px; overflow: hidden;">
         <iframe src="{url4}" width="800" height="1500" 
                 style="transform: scale(0.44); transform-origin: 0 0;">
         </iframe>
     </div>
     """,
     unsafe_allow_html=True
    )
    
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False    
# 랜덤 식당 추천
if st.button("준형인턴's 오늘의 메뉴 추천", disabled=st.session_state.button_clicked):
    st.session_state.button_clicked = True
    restaurants = ["🍽️슈마우스만찬🍽️","🍽️슈마우스만찬🍽️","🍽️슈마우스만찬🍽️","🍽️슈마우스만찬🍽️","🍽️슈마우스만찬🍽️","🍽️정담식당🍽️", "🍽️정담식당🍽️","🍽️정담식당🍽️","🍽️정담식당🍽️","굶기"]
    random_restaurant = random.choice(restaurants)
# 랜덤 추천 식당 표시
    st.subheader(f"결정이 힘든 당신..")
    st.subheader(f"오늘은 {random_restaurant} 입니다 맛점하세용‼️")


st.subheader("\n")
# 저장 파일 경로
SAVE_FILE = "saved_urls.json"

# 저장 함수
def save_urls(url1, url2):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump({"url1": url1, "url2": url2}, f)

# 불러오기 함수
def load_urls():
    if Path(SAVE_FILE).exists():
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("url1", ""), data.get("url2", "")
    return "", ""

# og:image 추출 함수
def get_og_image(url):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://pf.kakao.com/'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_tag = soup.find("meta", property="og:image")
        if meta_tag:
            return meta_tag.get("content")
        return None
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return None

# 이미지 로딩 함수
def load_image_from_url(img_url):
    try:
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        return None

# 불러온 값 또는 기본값
default_url1, default_url2 = load_urls()
if default_url1 == "":
    default_url1 = "https://pf.kakao.com/_CiVis/108791568"
if default_url2 == "":
    default_url2 = "https://pf.kakao.com/_vKxgdn/108791400"


from supabase import create_client, Client

# Supabase 연결 정보
SUPABASE_URL = "https://lpwmmlgrlojvsydkxqdw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxwd21tbGdybG9qdnN5ZGt4cWR3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMwNTQ4ODUsImV4cCI6MjA1ODYzMDg4NX0.kaqAtyzgA255blPsiyFqDXlVpBv7FvL9M_bogDUiYds"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.markdown("<h1 style='text-align:center; color:#4A90E2;'>📋 커뮤니티 게시판</h1>", unsafe_allow_html=True)
st.markdown("---")

RESTAURANT_LIST = [
    "슈마우스",
    "정담식당",
    "Others"
]

res = supabase.table("posts").select("*").order("id", desc=True).execute()
posts = res.data if res.data else []  # 📌 게시글이 없을 경우 빈 리스트

# 📌 게시글이 있을 때만 목록 표시
if posts:
    post_titles = [f"{p['restaurant']}리뷰 - 작성자: {p['title']} ({p['created_at'][:10]})" for p in posts]
    post_map = {title: p for title, p in zip(post_titles, posts)}

    st.markdown("### 📄 리뷰 게시글 목록")
    selected_title = st.selectbox("게시글을 선택하세요:", post_titles)

    # ✅ 선택한 게시글 데이터 가져오기
    selected_post = post_map.get(selected_title)

if selected_post:
    current_likes = selected_post.get("likes", 0)
    
    # 좋아요 버튼이 포함된 HTML 생성
    post_html = f"""
    <div style='
        border:1px solid #444;
        border-radius:10px;
        padding:20px;
        margin-bottom:20px;
        background-color:#2c2c2a;
        box-shadow:2px 2px 5px rgba(0,0,0,0.1);
        color: #f5f5f5;
        '>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <h4 style='margin:0;'>🍽️ {selected_post['restaurant']}</h4>
            <p style='margin:0;'><strong>작성자:</strong> {selected_post['title']}</p>
            <button style='
                padding: 8px 16px;
                background-color: #ff6f61;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                ' 
                onclick="window.location.reload();">
                ❤️ {current_likes}
            </button>
        </div>
        <p style='white-space: pre-wrap; margin-top:10px;'>{selected_post['content']}</p>
    </div>
    """
    
    # 마크다운으로 출력
    st.markdown(post_html, unsafe_allow_html=True)

    

if st.button(f"❤️ {current_likes}", key=f"like_{selected_post['id']}"):
        update_response = supabase.table("posts").update({
            "likes": current_likes + 1
        }).eq("id", selected_post["id"]).execute()

        if update_response.status_code == 200:
            st.success("좋아요가 추가되었습니다!")
            st.rerun()
        else:
            st.error("좋아요 업데이트에 실패했습니다. 다시 시도해 주세요.")
else:
    st.warning("현재 게시글이 없습니다. 새로운 게시글을 작성해 주세요!"


col_1, col_2 = st.columns([3,7])
with col_1:
# 댓글 목록 표시
    st.markdown("### 📚 댓글 목록")
    
with col_2:
    st.markdown("---")
    
comment_res = supabase.table("comments").select("*") \
    .eq("post_id", selected_post["id"]).order("id", desc=False).execute()

for c in comment_res.data:
    st.markdown(f"""
    <div style='
        border:1px solid #444;
        border-radius:10px;
        padding:10px;
        margin:5px 0;
        background-color:#2c2c2a;
            order-radius:6px;
    '>
        <p style='margin-bottom:2px;'>{c['content']}</p>
        <div style='font-size:11px; color:#888;'>작성일: {c['created_at'][:19].replace('T', ' ')}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# 댓글 입력창
st.markdown("### 💬 댓글 달기")
comment_input = st.text_input("댓글 내용", key="comment_input")
if st.button("댓글 작성"):
    if comment_input.strip():
        supabase.table("comments").insert({
            "post_id": selected_post["id"],
            "content": comment_input.strip()
        }).execute()
        st.success("댓글이 등록되었습니다.")
        st.rerun()

st.markdown("---")
# 게시글 작성
st.subheader("✍️ 리뷰 게시글 작성")
col1, col2 = st.columns([3, 7])
with col1:
    title = st.text_input("작성자")
    restaurant = st.selectbox("식당 선택", RESTAURANT_LIST)
with col2:
    content = st.text_area("내용", height=100)
if st.button("📤 글 등록하기"):
    if title and content:
        supabase.table("posts").insert({"title": title, "content": content, "restaurant": restaurant}).execute()
        st.success("✅ 게시글이 등록되었습니다!")
        st.rerun()
    else:
        st.warning("작성자, 식당, 내용을 모두 입력해주세요.")
st.markdown("---")
# UI 구성
st.subheader("<메뉴 이미지만 불러오기>")

# 입력창 2개
col_input1, col_input2 = st.columns(2)

with col_input1:
    url1 = st.text_input("슈마우스", value=default_url1)
with col_input2:
    url2 = st.text_input("정담", value=default_url2)

# 버튼 클릭 시 동작
if st.button("저장하고 이미지 가져오기"):
    # URL 저장
    save_urls(url1, url2)

    col_img1, col_img2 = st.columns(2)

    # URL 1 처리
    with st.spinner("URL 1 처리 중..."):
        img_url1 = get_og_image(url1)
        with col_img1:
            st.subheader("URL 1")
            if img_url1:
                img1 = load_image_from_url(img_url1)
                if img1:
                    st.image(img1, caption="🍽️슈마우스", width=350)
                    st.caption(f"[{img_url1}]({img_url1})")
                else:
                    st.warning("아직 메뉴가 공지되지 않았습니다.")
            else:
                st.warning("아직 메뉴가 공지되지 않았습니다.")

    # URL 2 처리
    with st.spinner("URL 2 처리 중..."):
        img_url2 = get_og_image(url2)
        with col_img2:
            st.subheader("URL 2")
            if img_url2:
                img2 = load_image_from_url(img_url2)
                if img2:
                    st.image(img2, caption="🍽️정담식당", width=300)
                    st.caption(f"[{img_url2}]({img_url2})")
                else:
                    st.warning("🍽️아직 메뉴가 공지되지 않았습니다.")
            else:
                st.warning("🍽️아직 메뉴가 공지되지 않았습니다.")

st.write("\n")
st.write("\n")

st.markdown(
    """
    <div style="background-color: #f2f2f2; color: #000; padding: 20px; text-align: center; font-size: 18px; 
                border-radius: 10px; border: 2px solid #ccc; margin-bottom: 20px; width: 100%; font-weight: bold;">
        🚀 **광고 배너** 🚀 <br>
        이 자리는 광고 공간입니다. **광고를 게재하려면 여기를 클릭**하세요!<br>
        문의사항과 가치있는 개발 아이디어도 보내주세요! 
        <br>
        <a href="https://open.kakao.com/o/sTv70Umh" target="_blank" style="color: #4CAF50; text-decoration: none;">광고 및 문의하기</a>
    </div>
    """,
    unsafe_allow_html=True
)


# 하단 정보 영역
st.markdown(
   """
    <div style="position: fixed; bottom: 10px; right: 10px; background-color: #000000; color: #FFFFFF; 
                padding: 10px 20px; border-radius: 5px; font-size: 12px; z-index: 1000;">
        <p style="margin: 0;">© 2025 by 데이터에듀 신사업본</p>
        <p style="margin: 0;">Contact us: jhp24228064@gmail.com</p>
    </div>
    """,
    unsafe_allow_html=True
)


# 페이지 내용
st.write("🏠퇴근도 환영합니다🏠📞모든 광고문의를 환영합니다📞☕커피 환영합니다☕")


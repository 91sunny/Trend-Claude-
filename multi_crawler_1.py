"""
===============================================================
  멀티 플랫폼 크롤러  —  multi_crawler.py
  실행: python multi_crawler.py
===============================================================
  수집 대상:
    - 네이버 쇼핑 (API)
    - ZARA Kids (내부 API)
    - H&M Kids (내부 API)
    - 무신사 키즈 (requests)
    - 쿠팡 (검색 링크)
    - Amazon Kids (검색 링크)
  사전 설치:
    pip install requests pandas beautifulsoup4
===============================================================
"""

import requests
import pandas as pd
import json, time, random
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

HEADERS_COMMON = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
}

# ──────────────────────────────────────────────
#  ★ 네이버 API 키 입력 (있으면 실제 데이터 수집)
# ──────────────────────────────────────────────
NAVER_CLIENT_ID     = "L28vWnQrGNl5PSf97Z99"
NAVER_CLIENT_SECRET = "s3qi2A6HI0"
# ──────────────────────────────────────────────

KEYWORDS = ["여아 원피스", "남아 맨투맨", "아동복", "키즈 바람막이"]


# ── 1. 네이버 쇼핑 API ────────────────────────────────────
def fetch_naver(keywords, display=30):
    if "여기에" in NAVER_CLIENT_ID:
        print("  [네이버] API 키 없음 → 데모 데이터 사용")
        return []

    results = []
    for kw in keywords:
        try:
            resp = requests.get(
                "https://openapi.naver.com/v1/search/shop.json",
                headers={
                    "X-Naver-Client-Id":     NAVER_CLIENT_ID,
                    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
                },
                params={"query": kw, "display": display, "sort": "sim"},
                timeout=10,
            )
            resp.raise_for_status()
            for item in resp.json().get("items", []):
                import re, html
                name = html.unescape(re.sub(r"<[^>]+>", "", item.get("title", "")))
                results.append({
                    "검색키워드": kw,
                    "상품명":     name,
                    "최저가":     int(item.get("lprice", 0)),
                    "판매처":     item.get("mallName", ""),
                    "판매처링크": item.get("link", ""),
                    "이미지URL":  item.get("image", ""),
                    "브랜드":     item.get("brand", ""),
                    "카테고리2":  item.get("category2", "아동의류"),
                    "출처":       "국내",
                    "플랫폼":     "네이버 쇼핑",
                    "플랫폼색상": "#03C75A",
                    "is_new":     False,
                    "수집일시":   NOW,
                })
            time.sleep(0.3)
        except Exception as e:
            print(f"  [네이버] {kw} 오류: {e}")
    print(f"  [네이버] {len(results)}개 수집")
    return results


# ── 2. ZARA Kids ──────────────────────────────────────────
def fetch_zara(category_ids=None):
    if category_ids is None:
        category_ids = [
            ("1338", "여아 원피스", "여아"),
            ("1443", "남아 맨투맨", "남아"),
            ("2185", "아동복",      "영아"),
        ]
    results = []
    for cat_id, kw, gender in category_ids:
        try:
            url  = f"https://www.zara.com/kr/ko/category/{cat_id}/products?ajax=true"
            resp = requests.get(url, headers={**HEADERS_COMMON, "Referer": "https://www.zara.com/kr/"}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            for group in data.get("productGroups", []):
                for el in group.get("elements", []):
                    c = (el.get("commercialComponents") or [{}])[0]
                    if not c:
                        continue
                    price  = int(c.get("price", 0)) // 100
                    media  = (c.get("media", {}).get("list") or [{}])[0]
                    img    = media.get("url", "")
                    if img and not img.startswith("http"):
                        img = "https:" + img
                    seo    = c.get("seo", {}).get("keyword", "")
                    pid    = c.get("id", "")
                    link   = f"https://www.zara.com/kr/ko/{seo}-p{pid}.html" if seo else "https://www.zara.com/kr/ko/kids/"
                    results.append({
                        "검색키워드": kw,
                        "상품명":     c.get("name", ""),
                        "최저가":     price,
                        "판매처":     "ZARA KIDS",
                        "판매처링크": link,
                        "이미지URL":  img,
                        "브랜드":     "ZARA KIDS",
                        "카테고리2":  "아동의류",
                        "출처":       "해외",
                        "플랫폼":     "ZARA",
                        "플랫폼색상": "#000000",
                        "is_new":     True,
                        "수집일시":   NOW,
                    })
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"  [ZARA] {kw} 오류: {e}")
    print(f"  [ZARA] {len(results)}개 수집")
    return results


# ── 3. H&M Kids ──────────────────────────────────────────
def fetch_hm(keywords=None):
    if keywords is None:
        keywords = ["dress", "sweatshirt", "jacket", "trousers"]
    results = []
    for kw in keywords:
        try:
            url = f"https://www2.hm.com/ko_kr/search-results.html?q={quote(kw+' kids')}&sections=item&sort=RELEVANCE&image-size=small&image-quality=auto&fit=false&offset=0&page-size=20"
            resp = requests.get(url, headers=HEADERS_COMMON, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            for article in soup.select("article.hm-product-item")[:10]:
                name_el  = article.select_one(".item-heading a")
                price_el = article.select_one(".item-price .price-value")
                img_el   = article.select_one("img.item-image")
                link_el  = article.select_one("a.item-link")
                if not (name_el and price_el):
                    continue
                price_txt = price_el.get_text(strip=True).replace(",", "").replace("원", "").replace("₩", "").strip()
                try:
                    price_val = int(price_txt)
                except:
                    price_val = 0
                img_url = img_el.get("src", "") or img_el.get("data-src", "") if img_el else ""
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                link = "https://www2.hm.com" + link_el.get("href", "") if link_el else "https://www2.hm.com/ko_kr/kids.html"
                results.append({
                    "검색키워드": "아동복",
                    "상품명":     name_el.get_text(strip=True),
                    "최저가":     price_val,
                    "판매처":     "H&M KIDS",
                    "판매처링크": link,
                    "이미지URL":  img_url,
                    "브랜드":     "H&M KIDS",
                    "카테고리2":  "아동의류",
                    "출처":       "해외",
                    "플랫폼":     "H&M",
                    "플랫폼색상": "#E50010",
                    "is_new":     False,
                    "수집일시":   NOW,
                })
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"  [H&M] {kw} 오류: {e}")
    print(f"  [H&M] {len(results)}개 수집")
    return results


# ── 4. 무신사 키즈 ────────────────────────────────────────
def fetch_musinsa():
    results = []
    try:
        url  = "https://www.musinsa.com/api/search/v2/goods?q=%ED%82%A4%EC%A6%88&gf=A&sortCode=POPULAR&page=1&size=20&category=001"
        resp = requests.get(url, headers={**HEADERS_COMMON, "Referer": "https://www.musinsa.com"}, timeout=15)
        data = resp.json()
        for item in data.get("data", {}).get("list", [])[:20]:
            img = item.get("image", "")
            if img and not img.startswith("http"):
                img = "https:" + img
            results.append({
                "검색키워드": "아동복",
                "상품명":     item.get("goodsName", ""),
                "최저가":     int(item.get("price", 0)),
                "판매처":     "무신사 키즈",
                "판매처링크": f"https://www.musinsa.com/goods/{item.get('goodsNo', '')}",
                "이미지URL":  img,
                "브랜드":     item.get("brandName", ""),
                "카테고리2":  "아동의류",
                "출처":       "국내",
                "플랫폼":     "무신사",
                "플랫폼색상": "#1A1A1A",
                "is_new":     False,
                "수집일시":   NOW,
            })
    except Exception as e:
        print(f"  [무신사] 오류: {e}")
    print(f"  [무신사] {len(results)}개 수집")
    return results


# ── 5. 데모 데이터 (API 없을 때 폴백) ────────────────────
def make_demo():
    from urllib.parse import quote as q

    def pimg(color, text):
        return f"https://placehold.co/300x300/{color}/ffffff?text={quote(text)}&font=roboto"

    items = [
        # (키워드, 상품명, 가격, 브랜드, 판매처, 링크, 이미지, 출처, 플랫폼, 색상)
        ("여아 원피스","쁘띠바토 프릴 린넨 원피스",   58000,"PETIT BATEAU","무신사 키즈",
         f"https://www.musinsa.com/search/musinsa/integrated?searchWord={q('쁘띠바토 프릴 린넨 원피스')}",
         pimg("ffb6c1","Dress"),"국내","무신사","1A1A1A"),
        ("여아 원피스","에잇포켓 튤 스커트 세트",      42000,"에잇포켓","네이버 쇼핑",
         f"https://search.shopping.naver.com/search/all?query={q('에잇포켓 튤 스커트 세트')}",
         pimg("ffd1dc","Skirt"),"국내","네이버 쇼핑","03C75A"),
        ("여아 원피스","알로앤루 리본 원피스",          48000,"알로앤루","네이버 쇼핑",
         f"https://search.shopping.naver.com/search/all?query={q('알로앤루 리본 원피스')}",
         pimg("ffa0b4","Ribbon"),"국내","네이버 쇼핑","03C75A"),
        ("여아 원피스","베이직하우스 플로럴 원피스",    24900,"베이직하우스","11번가",
         f"https://search.11st.co.kr/Search.tmall?kwd={q('베이직하우스 플로럴 원피스')}",
         pimg("ffcce0","Floral"),"국내","11번가","FF0000"),
        ("여아 원피스","키즈온 줄무늬 원피스",          19900,"키즈온","쿠팡",
         f"https://www.coupang.com/np/search?q={q('키즈온 줄무늬 원피스')}",
         pimg("ffe0ec","Stripe"),"국내","쿠팡","C0392B"),
        ("남아 맨투맨","무지 키즈 스웨트셔츠",          19900,"무지","무신사",
         f"https://www.musinsa.com/search/musinsa/integrated?searchWord={q('무지 키즈 스웨트셔츠')}",
         pimg("b0c4de","Sweat"),"국내","무신사","1A1A1A"),
        ("남아 맨투맨","MLB 키즈 곰돌이 맨투맨",        39000,"MLB KIDS","네이버 쇼핑",
         f"https://search.shopping.naver.com/search/all?query={q('MLB 키즈 곰돌이 맨투맨')}",
         pimg("add8e6","MLB"),"국내","네이버 쇼핑","03C75A"),
        ("남아 맨투맨","뉴발란스 키즈 로고 후드",       45000,"뉴발란스 키즈","네이버 쇼핑",
         f"https://search.shopping.naver.com/search/all?query={q('뉴발란스 키즈 로고 후드')}",
         pimg("a8d0e0","NB"),"국내","네이버 쇼핑","03C75A"),
        ("남아 맨투맨","키즈온 기모 맨투맨",            16900,"키즈온","쿠팡",
         f"https://www.coupang.com/np/search?q={q('키즈온 기모 맨투맨')}",
         pimg("c0d8e8","Fleece"),"국내","쿠팡","C0392B"),
        ("아동복","나이키 키즈 트레이닝 세트",           65000,"NIKE KIDS","네이버 쇼핑",
         f"https://search.shopping.naver.com/search/all?query={q('나이키 키즈 트레이닝')}",
         pimg("e8e8ff","Nike"),"국내","네이버 쇼핑","03C75A"),
        ("아동복","아디다스 키즈 점프수트",              58000,"ADIDAS KIDS","네이버 쇼핑",
         f"https://search.shopping.naver.com/search/all?query={q('아디다스 키즈 점프수트')}",
         pimg("d8d8ff","Adidas"),"국내","네이버 쇼핑","03C75A"),
        ("아동복","오르오르 린넨 와이드 팬츠",           38000,"오르오르","네이버 쇼핑",
         f"https://search.shopping.naver.com/search/all?query={q('오르오르 린넨 팬츠')}",
         pimg("dcdcff","Pants"),"국내","네이버 쇼핑","03C75A"),
        ("아동복","베이직하우스 레깅스 3팩",             12900,"베이직하우스","11번가",
         f"https://search.11st.co.kr/Search.tmall?kwd={q('베이직하우스 키즈 레깅스')}",
         pimg("f0e8ff","Leggings"),"국내","11번가","FF0000"),
        # 해외
        ("여아 원피스","Floral Print Dress",           45900,"ZARA KIDS","ZARA",
         f"https://www.zara.com/kr/ko/search?searchTerm={q('Floral Print Dress')}",
         pimg("ffb347","ZaraFloral"),"해외","ZARA","000000"),
        ("여아 원피스","Ruffled Frill Dress",           39900,"ZARA KIDS","ZARA",
         f"https://www.zara.com/kr/ko/search?searchTerm={q('Ruffled Frill Dress')}",
         pimg("ffa500","ZaraFrill"),"해외","ZARA","000000"),
        ("남아 맨투맨","Striped Cotton Sweatshirt",     32900,"ZARA KIDS","ZARA",
         f"https://www.zara.com/kr/ko/search?searchTerm={q('Striped Cotton Sweatshirt')}",
         pimg("98d8c8","ZaraStripe"),"해외","ZARA","000000"),
        ("아동복","Quilted Puffer Jacket",              69900,"ZARA KIDS","ZARA",
         f"https://www.zara.com/kr/ko/search?searchTerm={q('Quilted Puffer Jacket kids')}",
         pimg("d4b896","ZaraJacket"),"해외","ZARA","000000"),
        ("여아 원피스","Velvet Party Dress",             59900,"H&M KIDS","H&M",
         f"https://www2.hm.com/ko_kr/search-results.html?q={q('Velvet Party Dress kids')}",
         pimg("dda0dd","HMVelvet"),"해외","H&M","E50010"),
        ("남아 맨투맨","Cotton Blend Sweatshirt",        19900,"H&M KIDS","H&M",
         f"https://www2.hm.com/ko_kr/search-results.html?q={q('Cotton Blend Sweatshirt kids')}",
         pimg("87ceeb","HMSweat"),"해외","H&M","E50010"),
        ("아동복","Denim Jacket Kids",                  39900,"H&M KIDS","H&M",
         f"https://www2.hm.com/ko_kr/search-results.html?q={q('Denim Jacket kids')}",
         pimg("b0c4de","HMDenim"),"해외","H&M","E50010"),
        ("아동복","Kids Graphic Hoodie",                34900,"Amazon Kids","Amazon",
         f"https://www.amazon.com/s?k={q('kids graphic hoodie')}&i=fashion",
         pimg("ff9900","AmazonHoodie"),"해외","Amazon","FF9900"),
        ("아동복","Girls Floral Leggings Set",          28900,"Amazon Kids","Amazon",
         f"https://www.amazon.com/s?k={q('girls floral leggings set')}&i=fashion",
         pimg("ffcc88","AmazonSet"),"해외","Amazon","FF9900"),
    ]

    rows = []
    for kw, name, price, brand, mall, link, img_url, src, platform, color in items:
        rows.append({
            "검색키워드": kw, "상품명": name, "최저가": price,
            "판매처": mall, "판매처링크": link, "이미지URL": img_url,
            "브랜드": brand, "카테고리2": "아동의류",
            "출처": src, "플랫폼": platform, "플랫폼색상": color,
            "is_new": src == "해외",
            "수집일시": NOW,
        })
    return rows


# ── 메인 ──────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  🌐 멀티 플랫폼 아동복 크롤러")
    print("=" * 55)

    all_rows = []

    print("\n▶ 네이버 쇼핑 수집 중...")
    all_rows += fetch_naver(KEYWORDS)

    print("▶ ZARA Kids 수집 중...")
    all_rows += fetch_zara()

    print("▶ H&M Kids 수집 중...")
    all_rows += fetch_hm()

    print("▶ 무신사 키즈 수집 중...")
    all_rows += fetch_musinsa()

    # 수집 결과 없으면 데모 데이터 사용
    if len(all_rows) < 5:
        print("\n  ℹ️  수집된 실제 데이터가 적어 데모 데이터를 추가합니다.")
        all_rows += make_demo()

    df = pd.DataFrame(all_rows)

    # 공통 컬럼 정리
    for col in ["카테고리1", "카테고리3", "카테고리4", "제조사", "상품ID", "최고가"]:
        if col not in df.columns:
            df[col] = ""
    df["카테고리1"] = df.get("카테고리1", "패션의류").fillna("패션의류").replace("", "패션의류")
    df["최저가"]    = pd.to_numeric(df["최저가"], errors="coerce").fillna(0).astype(int)
    df["is_new"]    = df["is_new"].fillna(False).astype(bool)

    df.to_csv("all_data.csv",   index=False, encoding="utf-8-sig")
    df.to_csv("kids_data.csv",  index=False, encoding="utf-8-sig")
    print(f"\n  💾 all_data.csv / kids_data.csv 저장 완료 (총 {len(df)}개)")

    # 트렌드 데이터도 생성
    import random as rnd
    from datetime import timedelta
    rnd.seed(42)
    trend_rows = []
    base_date  = datetime.now() - timedelta(days=84)
    kw_bases   = {"아동복": 60, "여아 원피스": 42, "남아 맨투맨": 33, "키즈 아우터": 48}
    for week in range(13):
        ds = (base_date + timedelta(weeks=week)).strftime("%Y-%m-%d")
        for kw, bv in kw_bases.items():
            val = bv + week * rnd.uniform(0.8, 2.2) + rnd.uniform(-6, 6)
            trend_rows.append({"날짜": ds, "키워드": kw,
                                "검색량": round(max(10, val), 1), "출처": "데모"})
    pd.DataFrame(trend_rows).to_csv("trend_data.csv", index=False, encoding="utf-8-sig")
    print(f"  💾 trend_data.csv 저장 완료")
    print("\n🎉 완료! streamlit run app.py 를 실행하세요.")


if __name__ == "__main__":
    main()

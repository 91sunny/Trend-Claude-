"""
플랫폼 트렌드 수집기 v2 — platform_crawler.py
실행: python platform_crawler.py
"""
import asyncio, os, re, time, requests
import pandas as pd
from datetime import datetime
from urllib.parse import quote

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

NAVER_CLIENT_ID     = "7osKrkK7ta0h97fmWvfb"
NAVER_CLIENT_SECRET = "rpG_hXnDJA"  # 

INSTAGRAM_ID = ""   # : "kjs9435@nate.com"
INSTAGRAM_PW = ""   # : "sun8691200*"

NAVER_CATEGORIES = [
    {"name": "유아동 브랜드 패션", "keyword": "유아동 브랜드 패션"},
    {"name": "유아동 의류",        "keyword": "유아동 의류"},
    {"name": "유아동 신발/가방",   "keyword": "유아동 신발 가방"},
    {"name": "유아 언더웨어/잠옷", "keyword": "유아 언더웨어 잠옷"},
    {"name": "유아패션잡화",       "keyword": "유아 패션잡화"},
]
INSTAGRAM_TAGS   = ["등원룩","자매룩","남매룩","여아원피스","남아패션","여아패션"]
PINTEREST_QUERIES= ["kids fashion 2025","toddler fashion","girls fashion outfit","boys fashion outfit"]

UA   = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
ARGS = ["--no-sandbox","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled"]

async def make_page(ctx):
    p = await ctx.new_page()
    await p.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
    return p

# ── 쿠팡 ──────────────────────────────────────
async def crawl_coupang(pw, n=40):
    print("\n🛒 쿠팡 수집 중...")
    results=[]
    browser=await pw.chromium.launch(headless=False,args=ARGS,slow_mo=50)
    ctx=await browser.new_context(viewport={"width":1440,"height":900},user_agent=UA,locale="ko-KR")
    for label,url in [
        ("유아동패션 베스트","https://www.coupang.com/np/categories/115573?listSize=72&sorter=bestSeller"),
        ("유아동패션 신상",  "https://www.coupang.com/np/categories/115573?listSize=72&sorter=newestProducts"),
    ]:
        page=await make_page(ctx)
        try:
            await page.goto(url,wait_until="domcontentloaded",timeout=40000)
            await asyncio.sleep(5)
            for _ in range(6):
                await page.evaluate("window.scrollBy(0,window.innerHeight)")
                await asyncio.sleep(0.7)
            await asyncio.sleep(2)
            cards=[]
            for sel in ["li.baby-product","li[class*='baby-product']","li.search-product",
                        "li[class*='search-product']","div[data-product-id]","[class*='ProductCard']"]:
                cards=await page.query_selector_all(sel)
                if cards:
                    print(f"  [{label}] 셀렉터'{sel}' {len(cards)}개")
                    break
            if not cards:
                await page.screenshot(path=f"debug_coupang_{label[:4]}.png")
                print(f"  [{label}] 카드 없음→스크린샷 저장")
            for card in cards[:n]:
                try:
                    name=""
                    for ns in [".name","[class*='product-name']","strong","h3"]:
                        el=await card.query_selector(ns)
                        if el:
                            name=(await el.inner_text()).strip()
                            if name: break
                    if not name: continue
                    price=0
                    for ps in [".price-value","[class*='price']","em[class*='price']"]:
                        el=await card.query_selector(ps)
                        if el:
                            t=re.sub(r"[^\d]","",(await el.inner_text()).strip())
                            if t: price=int(t); break
                    img_url=""
                    img_el=await card.query_selector("img")
                    if img_el:
                        for a in ["src","data-src","data-original"]:
                            v=await img_el.get_attribute(a)
                            if v and v.startswith("http"): img_url=v; break
                    link=""
                    le=await card.query_selector("a")
                    if le:
                        h=await le.get_attribute("href") or ""
                        link="https://www.coupang.com"+h if h.startswith("/") else h
                    rv=""
                    for rs in [".rating-total-count","[class*='rating']"]:
                        el=await card.query_selector(rs)
                        if el: rv=(await el.inner_text()).strip(); break
                    results.append({"플랫폼":"쿠팡","플랫폼색상":"C0392B","분류":label,
                        "검색키워드":"유아동패션","상품명":name,"최저가":price,
                        "판매처":"쿠팡","판매처링크":link,"이미지URL":img_url,
                        "브랜드":"","리뷰정보":rv,"출처":"국내",
                        "is_new":"신상" in label,"수집일시":NOW})
                except: continue
            print(f"  [{label}] {len([r for r in results if r['분류']==label])}개")
        except Exception as e: print(f"  [{label}] 오류:{e}")
        finally: await page.close()
    await ctx.close(); await browser.close()
    print(f"  ✅ 쿠팡 {len(results)}개")
    return results

# ── 네이버 API ────────────────────────────────
def crawl_naver_api():
    print("\n🔍 네이버 API 수집 중...")
    try:
        test=requests.get("https://openapi.naver.com/v1/search/shop.json",
            headers={"X-Naver-Client-Id":NAVER_CLIENT_ID,"X-Naver-Client-Secret":NAVER_CLIENT_SECRET},
            params={"query":"아동복","display":1},timeout=10)
        if test.status_code==401:
            print("  ❌ 401 인증 실패 → developers.naver.com 에서 Client Secret 재발급 필요")
            return []
    except Exception as e:
        print(f"  ❌ 연결 오류: {e}"); return []
    results=[]; hdrs={"X-Naver-Client-Id":NAVER_CLIENT_ID,"X-Naver-Client-Secret":NAVER_CLIENT_SECRET}
    import html as hm
    for cat in NAVER_CATEGORIES:
        for sort,label in [("sim","인기순"),("date","최신순")]:
            try:
                r=requests.get("https://openapi.naver.com/v1/search/shop.json",headers=hdrs,
                    params={"query":cat["keyword"],"display":30,"sort":sort},timeout=10)
                r.raise_for_status()
                for item in r.json().get("items",[]):
                    name=hm.unescape(re.sub(r"<[^>]+>","",item.get("title","")))
                    results.append({"플랫폼":"네이버 쇼핑","플랫폼색상":"03C75A",
                        "분류":f"{cat['name']} ({label})","검색키워드":cat["name"],
                        "상품명":name,"최저가":int(item.get("lprice",0)),
                        "판매처":item.get("mallName",""),"판매처링크":item.get("link",""),
                        "이미지URL":item.get("image",""),"브랜드":item.get("brand",""),
                        "리뷰정보":"","출처":"국내","is_new":sort=="date","수집일시":NOW})
                print(f"  [{cat['name']}] {label} {len(r.json().get('items',[]))}개")
                time.sleep(0.3)
            except Exception as e: print(f"  [{cat['name']}] {label} 오류:{e}")
    print(f"  ✅ 네이버 API {len(results)}개"); return results

# ── 네이버 직접 스크래핑 (API 실패 폴백) ──────
async def crawl_naver_direct(pw):
    print("\n🔍 네이버 직접 스크래핑...")
    results=[]; browser=await pw.chromium.launch(headless=True,args=ARGS)
    ctx=await browser.new_context(viewport={"width":1440,"height":900},user_agent=UA,locale="ko-KR")
    for label,kw in [("유아동 의류","유아동 의류"),("유아동 신발","유아동 신발"),
                     ("유아 잠옷","유아 잠옷"),("유아패션잡화","유아 패션잡화"),("유아동 브랜드","유아동 브랜드")]:
        page=await make_page(ctx)
        url=f"https://search.shopping.naver.com/search/all?query={quote(kw)}&sort=rel"
        try:
            await page.goto(url,wait_until="domcontentloaded",timeout=30000)
            await asyncio.sleep(3)
            for _ in range(4): await page.evaluate("window.scrollBy(0,window.innerHeight)"); await asyncio.sleep(0.8)
            cards=[]
            for sel in ["li.product_item__MDl4T","li[class*='product_item']","li[class*='Product']","div[class*='product_item']"]:
                cards=await page.query_selector_all(sel)
                if cards: break
            cnt=0
            for card in cards[:25]:
                try:
                    name_el=await card.query_selector("strong[class*='name'],[class*='product_title'],[class*='title']")
                    price_el=await card.query_selector("[class*='price_num'],[class*='price']")
                    img_el=await card.query_selector("img")
                    link_el=await card.query_selector("a")
                    name=(await name_el.inner_text()).strip() if name_el else ""
                    ptxt=(await price_el.inner_text()).strip() if price_el else ""
                    price=int(re.sub(r"[^\d]","",ptxt) or 0)
                    img=await img_el.get_attribute("src") or "" if img_el else ""
                    if img.startswith("//"): img="https:"+img
                    href=await link_el.get_attribute("href") or "" if link_el else ""
                    link=href if href.startswith("http") else "https://shopping.naver.com"
                    if not name: continue
                    results.append({"플랫폼":"네이버 쇼핑","플랫폼색상":"03C75A",
                        "분류":f"{label} 인기순","검색키워드":label,
                        "상품명":name,"최저가":price,"판매처":"네이버 쇼핑",
                        "판매처링크":link,"이미지URL":img,"브랜드":"",
                        "리뷰정보":"","출처":"국내","is_new":False,"수집일시":NOW})
                    cnt+=1
                except: continue
            print(f"  [{label}] {cnt}개")
        except Exception as e: print(f"  [{label}] 오류:{e}")
        finally: await page.close()
    await ctx.close(); await browser.close()
    print(f"  ✅ 네이버 직접 {len(results)}개"); return results

# ── 인스타그램 ────────────────────────────────
async def crawl_instagram(pw, n=12):
    print("\n📸 인스타그램 수집 중...")
    results=[]; browser=await pw.chromium.launch(headless=False,args=ARGS,slow_mo=30)
    ctx=await browser.new_context(
        viewport={"width":390,"height":844},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
        locale="ko-KR")
    page=await make_page(ctx)
    if INSTAGRAM_ID and INSTAGRAM_PW:
        try:
            await page.goto("https://www.instagram.com/accounts/login/",timeout=30000)
            await asyncio.sleep(3)
            await page.fill("input[name='username']",INSTAGRAM_ID)
            await asyncio.sleep(0.5)
            await page.fill("input[name='password']",INSTAGRAM_PW)
            await asyncio.sleep(0.5)
            await page.click("button[type='submit']")
            await asyncio.sleep(5)
            print(f"  로그인 {'성공' if 'login' not in page.url else '실패'}")
        except Exception as e: print(f"  로그인 오류:{e}")
    else:
        print("  ℹ️  로그인 정보 없음 → 공개 게시물만")
    for tag in INSTAGRAM_TAGS:
        try:
            await page.goto(f"https://www.instagram.com/explore/tags/{quote(tag)}/",wait_until="domcontentloaded",timeout=30000)
            await asyncio.sleep(4)
            for btn_sel in ["[aria-label='닫기']","button[class*='close']"]:
                try:
                    btn=await page.query_selector(btn_sel)
                    if btn: await btn.click(); await asyncio.sleep(1); break
                except: pass
            for _ in range(3): await page.evaluate("window.scrollBy(0,window.innerHeight)"); await asyncio.sleep(1)
            imgs=await page.query_selector_all("article img, main img, div[role='main'] img")
            cnt=0; seen=set()
            for img_el in imgs:
                try:
                    src=await img_el.get_attribute("src") or ""
                    if not src or src in seen or "static" in src or len(src)<20: continue
                    seen.add(src)
                    alt=await img_el.get_attribute("alt") or f"#{tag} 패션"
                    link=await img_el.evaluate("el=>el.closest('a')?el.closest('a').href:''")
                    if not link: link=f"https://www.instagram.com/explore/tags/{quote(tag)}/"
                    results.append({"플랫폼":"Instagram","플랫폼색상":"E1306C",
                        "분류":f"#{tag}","검색키워드":f"#{tag}",
                        "상품명":alt[:80],"최저가":0,"판매처":"Instagram",
                        "판매처링크":link,"이미지URL":src,"브랜드":"",
                        "리뷰정보":f"#{tag}","출처":"SNS","is_new":True,"수집일시":NOW})
                    cnt+=1
                    if cnt>=n: break
                except: continue
            print(f"  [#{tag}] {cnt}개")
        except Exception as e: print(f"  [#{tag}] 오류:{e}")
        await asyncio.sleep(2)
    await page.close(); await ctx.close(); await browser.close()
    print(f"  ✅ 인스타그램 {len(results)}개"); return results

# ── 핀터레스트 ────────────────────────────────
async def crawl_pinterest(pw, n=15):
    print("\n📌 핀터레스트 수집 중...")
    results=[]; browser=await pw.chromium.launch(headless=True,args=ARGS)
    ctx=await browser.new_context(viewport={"width":1440,"height":900},user_agent=UA,locale="ko-KR")
    for query in PINTEREST_QUERIES:
        page=await make_page(ctx)
        try:
            await page.goto(f"https://kr.pinterest.com/search/pins/?q={quote(query)}&rs=typed",wait_until="domcontentloaded",timeout=30000)
            await asyncio.sleep(5)
            try: await page.keyboard.press("Escape")
            except: pass
            for _ in range(4): await page.evaluate("window.scrollBy(0,window.innerHeight*2)"); await asyncio.sleep(1.5)
            imgs=await page.query_selector_all("img[srcset],img[src*='pinimg']")
            cnt=0; seen=set()
            for img_el in imgs:
                try:
                    srcset=await img_el.get_attribute("srcset") or ""
                    src=await img_el.get_attribute("src") or ""
                    best=src
                    if srcset:
                        parts=[p.strip() for p in srcset.split(",")]
                        uw=[]
                        for p in parts:
                            sp=p.strip().split(" ")
                            if len(sp)>=1 and "pinimg" in sp[0]:
                                w=int(sp[1].replace("w","")) if len(sp)>1 and sp[1].endswith("w") else 0
                                uw.append((w,sp[0]))
                        if uw: best=sorted(uw,reverse=True)[0][1]
                    if not best or best in seen or "pinimg" not in best: continue
                    if any(x in best for x in ["/30x","/60x","/75x"]): continue
                    best=re.sub(r'/\d+x\d*/','/736x/',best)
                    seen.add(best)
                    alt=await img_el.get_attribute("alt") or query
                    link=await img_el.evaluate("el=>el.closest('a')?el.closest('a').href:''")
                    if link and not link.startswith("http"): link="https://kr.pinterest.com"+link
                    if not link: link=f"https://kr.pinterest.com/search/pins/?q={quote(query)}"
                    results.append({"플랫폼":"Pinterest","플랫폼색상":"E60023",
                        "분류":query,"검색키워드":query,
                        "상품명":alt[:80],"최저가":0,"판매처":"Pinterest",
                        "판매처링크":link,"이미지URL":best,"브랜드":"",
                        "리뷰정보":query,"출처":"SNS","is_new":True,"수집일시":NOW})
                    cnt+=1
                    if cnt>=n: break
                except: continue
            print(f"  [{query}] {cnt}개")
        except Exception as e: print(f"  [{query}] 오류:{e}")
        finally: await page.close()
        await asyncio.sleep(2)
    await ctx.close(); await browser.close()
    print(f"  ✅ 핀터레스트 {len(results)}개"); return results

# ── 저장 ──────────────────────────────────────
def save(rows):
    df=pd.DataFrame(rows)
    for col in ["이미지URL","판매처링크","리뷰정보","브랜드"]:
        if col not in df.columns: df[col]=""
    df["최저가"]=pd.to_numeric(df.get("최저가",0),errors="coerce").fillna(0).astype(int)
    df["is_new"]=df.get("is_new",False).fillna(False).astype(bool)
    if os.path.exists("all_data.csv"):
        old=pd.read_csv("all_data.csv",encoding="utf-8-sig")
        old.columns=old.columns.str.strip()
        df=pd.concat([df,old],ignore_index=True).drop_duplicates(subset=["상품명","판매처링크"],keep="first")
    df.to_csv("all_data.csv",index=False,encoding="utf-8-sig")
    df.to_csv("kids_data.csv",index=False,encoding="utf-8-sig")
    print(f"\n{'='*55}\n  💾 총 {len(df)}개 저장")
    for pf,cnt in df.groupby("플랫폼").size().items():
        ic=(df[df["플랫폼"]==pf]["이미지URL"]!="").sum()
        print(f"  {pf:<16}{cnt:>4}개  이미지:{ic}개")

async def main_async():
    from playwright.async_api import async_playwright
    print("="*55); print(f"  🌐 아동복 트렌드 수집기 v2\n  {NOW}"); print("="*55)
    rows=[]
    async with async_playwright() as pw:
        try: rows+=await crawl_coupang(pw)
        except Exception as e: print(f"쿠팡:{e}")
        naver=crawl_naver_api()
        if not naver:
            try: naver=await crawl_naver_direct(pw)
            except Exception as e: print(f"네이버:{e}")
        rows+=naver
        try: rows+=await crawl_instagram(pw)
        except Exception as e: print(f"인스타:{e}")
        try: rows+=await crawl_pinterest(pw)
        except Exception as e: print(f"핀터:{e}")
    if not rows: print("  수집 실패"); return
    save(rows)
    print("\n🎉 streamlit run app_4.py")

if __name__=="__main__":
    try: asyncio.run(main_async())
    except ImportError: print("pip install playwright && playwright install chromium")

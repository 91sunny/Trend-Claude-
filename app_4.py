"""
아동복 트렌드 대시보드 v4 — app_4.py
실행: streamlit run app_4.py
"""
import os, streamlit as st, pandas as pd, plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="아동복 트렌드 대시보드", page_icon="👗",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html,body,[class*="css"]{font-family:'Apple SD Gothic Neo','Pretendard',sans-serif}
.dash-title{font-size:1.6rem;font-weight:700;color:#111;margin:0}
.dash-sub{font-size:.82rem;color:#aaa;margin:.1rem 0 1rem}
.platform-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-bottom:16px}
.ptile{border-radius:12px;padding:10px 12px;display:flex;align-items:center;gap:9px;
       text-decoration:none;border:0.5px solid rgba(0,0,0,.08);transition:opacity .15s}
.ptile:hover{opacity:.82}
.ptile-icon{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;
            justify-content:center;font-size:15px;flex-shrink:0;color:#fff}
.ptile-name{font-size:.8rem;font-weight:600;color:#111}
.ptile-sub{font-size:.68rem;color:#888;margin-top:1px}
.kpi-wrap{background:#fff;border:1px solid #eee;border-radius:12px;padding:.85rem 1rem;text-align:center}
.kpi-l{font-size:.68rem;color:#bbb;text-transform:uppercase;letter-spacing:.05em}
.kpi-v{font-size:1.5rem;font-weight:700;color:#111;line-height:1.2}
.kpi-s{font-size:.68rem;color:#ccc;margin-top:.1rem}
.b-hot{background:#ff3b57;color:#fff;font-size:9px;font-weight:800;padding:1px 5px;border-radius:3px}
.b-new{background:#3346cc;color:#fff;font-size:9px;font-weight:800;padding:1px 5px;border-radius:3px}
.b-sns{background:#E1306C;color:#fff;font-size:9px;font-weight:800;padding:1px 5px;border-radius:3px}
.pcard{background:#fff;border:1px solid #eee;border-radius:14px;overflow:hidden;transition:box-shadow .18s,transform .18s}
.pcard:hover{box-shadow:0 6px 20px rgba(0,0,0,.08);transform:translateY(-2px)}
.pimg-wrap{width:100%;aspect-ratio:1/1;overflow:hidden;background:#f5f5f5;
           display:flex;align-items:center;justify-content:center;position:relative}
.pimg-wrap img{width:100%;height:100%;object-fit:cover}
.pbadges{position:absolute;top:6px;left:6px;display:flex;flex-wrap:wrap;gap:2px}
.psrc-pill{position:absolute;bottom:6px;right:6px;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:700;color:#fff}
.pinfo{padding:.65rem .8rem .8rem}
.ptag{display:inline-block;font-size:9px;font-weight:600;padding:1px 5px;border-radius:20px;margin-bottom:3px}
.pname{font-size:.8rem;font-weight:600;color:#111;line-height:1.35;margin-bottom:2px;
       display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pbrand{font-size:.72rem;color:#aaa;margin-bottom:2px}
.pprice{font-size:1rem;font-weight:700;color:#e8384f}
.pmall{font-size:.68rem;color:#ccc;margin-top:1px}
.phashtag{font-size:.72rem;color:#3346cc;margin-top:2px}
.noimg{width:100%;aspect-ratio:1/1;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:2rem;color:#ccc}
.sec-head{font-size:.95rem;font-weight:700;color:#111;margin:1.2rem 0 .6rem}
hr.div{border:none;border-top:1px solid #f0f0f0;margin:1rem 0}
[data-testid="stSidebar"]{background:#fafafa;border-right:1px solid #f0f0f0}
.sb-lbl{font-size:.67rem;font-weight:700;color:#bbb;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.35rem}
/* SNS 갤러리 핀터레스트 스타일 */
.sns-grid{columns:3;gap:8px}
.sns-pin{break-inside:avoid;margin-bottom:8px;border-radius:12px;overflow:hidden;background:#f5f5f5}
.sns-pin img{width:100%;display:block}
.sns-pin-info{padding:6px 8px 8px;background:#fff;border:1px solid #eee;border-top:none;border-radius:0 0 12px 12px}
</style>
""", unsafe_allow_html=True)

PLATFORMS = [
    {"name":"쿠팡 키즈",   "sub":"유아동패션 베스트",  "url":"https://www.coupang.com/np/categories/115573","color":"C0392B","icon":"🛒"},
    {"name":"네이버 쇼핑", "sub":"유아동 카테고리",    "url":"https://search.shopping.naver.com/search/all?query=%EC%9C%A0%EC%95%84%EB%8F%99%ED%8C%A8%EC%85%98","color":"03C75A","icon":"🔍"},
    {"name":"무신사 키즈", "sub":"키즈 컬렉션",        "url":"https://www.musinsa.com/main/kids/recommend?gf=F","color":"1A1A1A","icon":"👟"},
    {"name":"Instagram",   "sub":"#등원룩 #자매룩",    "url":"https://www.instagram.com/explore/tags/%EB%93%B1%EC%9B%90%EB%A3%A8%ED%81%AC/","color":"E1306C","icon":"📸"},
    {"name":"Pinterest",   "sub":"Kids Fashion",       "url":"https://kr.pinterest.com/search/pins/?q=kids+fashion","color":"E60023","icon":"📌"},
    {"name":"Amazon",      "sub":"Kids Fashion",       "url":"https://www.amazon.com/s?k=kids+fashion","color":"FF9900","icon":"📦"},
    {"name":"H&M Kids",    "sub":"신상품",             "url":"https://www2.hm.com/ko_kr/kids.html","color":"E50010","icon":"🇸🇪"},
    {"name":"ZARA Kids",   "sub":"신상품",             "url":"https://www.zara.com/kr/ko/kids-l1037.html","color":"111111","icon":"✦"},
]

@st.cache_data
def load_data():
    for fname in ["all_data.csv","kids_data.csv"]:
        if not os.path.exists(fname): continue
        df = pd.read_csv(fname, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        df["최저가"]     = pd.to_numeric(df.get("최저가",0), errors="coerce").fillna(0).astype(int)
        df["브랜드"]     = df.get("브랜드","").fillna("").replace("","브랜드 없음")
        df["판매처"]     = df.get("판매처","").fillna("판매처 미상")
        df["이미지URL"]  = df.get("이미지URL","").fillna("")
        df["판매처링크"] = df.get("판매처링크","").fillna("")
        df["출처"]       = df.get("출처","국내").fillna("국내")
        df["플랫폼"]     = df.get("플랫폼","기타").fillna("기타")
        df["플랫폼색상"] = df.get("플랫폼색상","888888").fillna("888888")
        df["분류"]       = df.get("분류", df.get("검색키워드","")).fillna("기타")
        df["리뷰정보"]   = df.get("리뷰정보","").fillna("")
        df["is_new"]     = df.get("is_new",False).fillna(False).astype(bool)
        df["is_hot"]     = False
        for kw in df["검색키워드"].unique():
            m=df["검색키워드"]==kw; sub=df.loc[m,"최저가"]
            if len(sub)>=5:
                df.loc[m & df["최저가"].between(sub.quantile(.2),sub.quantile(.8)),"is_hot"]=True
        return df
    return pd.DataFrame()

@st.cache_data
def load_trend():
    if not os.path.exists("trend_data.csv"): return pd.DataFrame()
    df=pd.read_csv("trend_data.csv",encoding="utf-8-sig")
    df["날짜"]=pd.to_datetime(df["날짜"])
    return df

df_all=load_data(); df_trend=load_trend()

if df_all.empty:
    st.error("데이터가 없어요. 먼저 아래 명령어를 실행하세요.")
    st.code("python platform_crawler.py")
    st.stop()

# 플랫폼별 구분
df_sns   = df_all[df_all["출처"]=="SNS"].copy()
df_shop  = df_all[df_all["출처"]!="SNS"].copy()
df_ig    = df_sns[df_sns["플랫폼"]=="Instagram"].copy()
df_pin   = df_sns[df_sns["플랫폼"]=="Pinterest"].copy()
df_coup  = df_shop[df_shop["플랫폼"]=="쿠팡"].copy()
df_naver = df_shop[df_shop["플랫폼"]=="네이버 쇼핑"].copy()

# ── 사이드바 ─────────────────────────────────
with st.sidebar:
    st.markdown("## 👗 필터")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">플랫폼</div>', unsafe_allow_html=True)
    pf_avail=sorted(df_all["플랫폼"].unique().tolist())
    sel_pf=st.multiselect("플랫폼",pf_avail,default=pf_avail,label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">국가/출처</div>', unsafe_allow_html=True)
    src_avail=sorted(df_all["출처"].unique().tolist())
    sel_src=st.multiselect("출처",src_avail,default=src_avail,label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">가격 범위 (원)</div>', unsafe_allow_html=True)
    shop_prices=df_shop[df_shop["최저가"]>0]["최저가"]
    p_min=int(shop_prices.min()) if len(shop_prices) else 0
    p_max=max(int(shop_prices.max()) if len(shop_prices) else 200000, 200000)
    price_range=st.slider("가격",p_min,p_max,(p_min,p_max),step=1000,format="%d원",label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">배지 필터</div>', unsafe_allow_html=True)
    show_hot=st.checkbox("🔴 HOT만"); show_new=st.checkbox("🔵 NEW만")
    st.markdown("---")
    col_n=st.slider("갤러리 열 수",2,5,3)
    st.markdown("---")
    if st.button("🔄 새로고침",use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.markdown("---")
    st.caption("데이터 재수집:")
    st.code("python platform_crawler.py", language="bash")

# ── 필터 적용 ─────────────────────────────────
df=df_all[df_all["플랫폼"].isin(sel_pf) & df_all["출처"].isin(sel_src)].copy()
df_filtered_shop=df[df["출처"]!="SNS"]
df_filtered_shop=df_filtered_shop[df_filtered_shop["최저가"].between(price_range[0],price_range[1])]
if show_hot:  df_filtered_shop=df_filtered_shop[df_filtered_shop["is_hot"]]
if show_new:  df_filtered_shop=df_filtered_shop[df_filtered_shop["is_new"]]
df_filtered_sns=df[df["출처"]=="SNS"]

# ── 헤더 ──────────────────────────────────────
st.markdown('<div class="dash-title">👗 아동복 트렌드 대시보드</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dash-sub">쿠팡 · 네이버 · Instagram · Pinterest 통합 · {datetime.now().strftime("%Y.%m.%d")}</div>', unsafe_allow_html=True)

# ── 플랫폼 타일 ───────────────────────────────
tiles='<div class="platform-grid">'
for p in PLATFORMS:
    tiles+=f'<a class="ptile" href="{p["url"]}" target="_blank" style="background:#{p["color"]}18;border-color:#{p["color"]}33"><div class="ptile-icon" style="background:#{p["color"]}">{p["icon"]}</div><div><div class="ptile-name">{p["name"]}</div><div class="ptile-sub">{p["sub"]}</div></div></a>'
tiles+='</div>'
st.markdown(tiles, unsafe_allow_html=True)
st.markdown('<hr class="div">', unsafe_allow_html=True)

# ── 트렌드 차트 ───────────────────────────────
if not df_trend.empty:
    st.markdown('<div class="sec-head">📈 검색 트렌드 추이</div>', unsafe_allow_html=True)
    dft=df_trend
    fig=px.line(dft,x="날짜",y="검색량",color="키워드",markers=True,
                color_discrete_sequence=["#4a6cf7","#ff6b9d","#ffa726","#26c6da","#66bb6a"],
                labels={"날짜":"","검색량":"검색 지수","키워드":""})
    fig.update_traces(line_width=2,marker_size=4)
    fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",margin=dict(t=5,b=20,l=0,r=0),
                      xaxis=dict(showgrid=False,tickfont_size=11),
                      yaxis=dict(gridcolor="#f5f5f5",tickfont_size=11),
                      legend=dict(orientation="h",y=1.08,x=0,font_size=11),hovermode="x unified")
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('<hr class="div">', unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────
c1,c2,c3,c4,c5=st.columns(5)
ig_cnt  = len(df_ig)
pin_cnt = len(df_pin)
for col,lbl,val,sub in [
    (c1,"총 쇼핑 상품",f"{len(df_filtered_shop):,}개",f"쿠팡+네이버 등"),
    (c2,"쿠팡 유아동",f"{len(df_coup):,}개","베스트셀러"),
    (c3,"네이버 유아동",f"{len(df_naver):,}개","5개 카테고리"),
    (c4,"인스타그램",f"{ig_cnt:,}개","해시태그 게시물"),
    (c5,"핀터레스트",f"{pin_cnt:,}개","최신 핀"),
]:
    with col:
        st.markdown(f'<div class="kpi-wrap"><div class="kpi-l">{lbl}</div><div class="kpi-v">{val}</div><div class="kpi-s">{sub}</div></div>',unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

# ── 메인 탭 ───────────────────────────────────
tab_shop, tab_coup, tab_naver, tab_ig, tab_pin = st.tabs([
    "🛍️ 전체 쇼핑",
    "🛒 쿠팡 베스트",
    "🔍 네이버 카테고리",
    "📸 Instagram",
    "📌 Pinterest",
])

CS=dict(plot_bgcolor="white",paper_bgcolor="white",margin=dict(t=5,b=5,l=0,r=0))

# ─ 탭1: 전체 쇼핑 갤러리 ─────────────────────
with tab_shop:
    gl,gr=st.columns([4,1])
    with gl: st.markdown(f'<div class="sec-head">🖼️ 상품 갤러리 <span style="font-size:.78rem;font-weight:400;color:#bbb">{len(df_filtered_shop):,}개</span></div>',unsafe_allow_html=True)
    with gr: sort_opt=st.selectbox("정렬",["기본순","가격 낮은순","가격 높은순"],key="s1",label_visibility="collapsed")
    dg=(df_filtered_shop.sort_values("최저가",ascending=(sort_opt=="가격 낮은순")).reset_index(drop=True)
        if sort_opt!="기본순" else df_filtered_shop.reset_index(drop=True))
    if not len(dg):
        st.warning("상품이 없어요.")
    else:
        cols=st.columns(col_n,gap="small")
        for idx,row in dg.iterrows():
            with cols[idx%col_n]:
                badges=('<span class="b-hot">HOT</span>' if row.get("is_hot") else "")+('<span class="b-new">NEW</span>' if row.get("is_new") else "")
                img_html=(f'<img src="{row["이미지URL"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=noimg>👗</div>\'">' if row["이미지URL"] else '<div class="noimg">👗</div>')
                price_str=f"{int(row['최저가']):,}원" if row["최저가"]>0 else "—"
                pf_color="#"+str(row.get("플랫폼색상","888888"))
                st.markdown(f"""<div class="pcard">
                  <div class="pimg-wrap">{img_html}
                    <div class="pbadges">{badges}</div>
                    <div class="psrc-pill" style="background:{pf_color}">{row.get('플랫폼','')}</div>
                  </div>
                  <div class="pinfo">
                    <span class="ptag" style="background:#f0f4ff;color:#3346cc">{row.get('분류','')[:20]}</span>
                    <div class="pname">{row['상품명']}</div>
                    <div class="pprice">{price_str}</div>
                    <div class="pmall">🏪 {row['판매처']}</div>
                    {"<div class='phashtag'>"+str(row['리뷰정보'])+"</div>" if row.get('리뷰정보') else ""}
                  </div></div>""",unsafe_allow_html=True)
                if row["판매처링크"]:
                    st.link_button("🔗 바로가기",row["판매처링크"],use_container_width=True)
                st.markdown("<div style='margin-bottom:4px'></div>",unsafe_allow_html=True)

# ─ 탭2: 쿠팡 베스트 ──────────────────────────
with tab_coup:
    st.markdown('<div class="sec-head">🛒 쿠팡 유아동패션 베스트셀러</div>', unsafe_allow_html=True)
    if df_coup.empty:
        st.info("쿠팡 데이터가 없어요. `python platform_crawler.py` 실행 후 새로고침하세요.")
    else:
        # 분류별 탭
        cats=df_coup["분류"].unique().tolist()
        if len(cats)>1:
            subtabs=st.tabs(cats)
            for i,(subtab,cat) in enumerate(zip(subtabs,cats)):
                with subtab:
                    sub_df=df_coup[df_coup["분류"]==cat].reset_index(drop=True)
                    cols=st.columns(col_n,gap="small")
                    for idx,row in sub_df.iterrows():
                        with cols[idx%col_n]:
                            img_html=(f'<img src="{row["이미지URL"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=noimg>🛒</div>\'">' if row["이미지URL"] else '<div class="noimg">🛒</div>')
                            price_str=f"{int(row['최저가']):,}원" if row["최저가"]>0 else "—"
                            st.markdown(f"""<div class="pcard">
                              <div class="pimg-wrap">{img_html}
                                <div class="psrc-pill" style="background:#C0392B">쿠팡</div>
                              </div>
                              <div class="pinfo">
                                <div class="pname">{row['상품명']}</div>
                                <div class="pprice">{price_str}</div>
                                {"<div class='phashtag'>⭐ "+str(row['리뷰정보'])+"</div>" if row.get('리뷰정보') else ""}
                              </div></div>""",unsafe_allow_html=True)
                            if row["판매처링크"]:
                                st.link_button("🔗 쿠팡 보기",row["판매처링크"],use_container_width=True)
                            st.markdown("<div style='margin-bottom:4px'></div>",unsafe_allow_html=True)
        else:
            cols=st.columns(col_n,gap="small")
            for idx,row in df_coup.reset_index(drop=True).iterrows():
                with cols[idx%col_n]:
                    img_html=(f'<img src="{row["이미지URL"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=noimg>🛒</div>\'">' if row["이미지URL"] else '<div class="noimg">🛒</div>')
                    price_str=f"{int(row['최저가']):,}원" if row["최저가"]>0 else "—"
                    st.markdown(f"""<div class="pcard">
                      <div class="pimg-wrap">{img_html}</div>
                      <div class="pinfo">
                        <div class="pname">{row['상품명']}</div>
                        <div class="pprice">{price_str}</div>
                      </div></div>""",unsafe_allow_html=True)
                    if row["판매처링크"]:
                        st.link_button("🔗 쿠팡 보기",row["판매처링크"],use_container_width=True)
                    st.markdown("<div style='margin-bottom:4px'></div>",unsafe_allow_html=True)

# ─ 탭3: 네이버 카테고리 ──────────────────────
with tab_naver:
    st.markdown('<div class="sec-head">🔍 네이버 유아동 카테고리별 인기상품</div>', unsafe_allow_html=True)
    if df_naver.empty:
        st.info("네이버 데이터가 없어요. `python platform_crawler.py` 실행 후 새로고침하세요.")
    else:
        naver_cats=df_naver["검색키워드"].unique().tolist()
        ntabs=st.tabs(naver_cats) if len(naver_cats)>1 else [st.container()]
        for i,cat in enumerate(naver_cats):
            with ntabs[i]:
                sub_df=df_naver[df_naver["검색키워드"]==cat].reset_index(drop=True)
                st.caption(f"총 {len(sub_df)}개 · 인기순/최신순 혼합")
                cols=st.columns(col_n,gap="small")
                for idx,row in sub_df.iterrows():
                    with cols[idx%col_n]:
                        img_html=(f'<img src="{row["이미지URL"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=noimg>🔍</div>\'">' if row["이미지URL"] else '<div class="noimg">🔍</div>')
                        price_str=f"{int(row['최저가']):,}원" if row["최저가"]>0 else "—"
                        is_new_badge='<span class="b-new">NEW</span>' if row.get("is_new") else ""
                        st.markdown(f"""<div class="pcard">
                          <div class="pimg-wrap">{img_html}
                            <div class="pbadges">{is_new_badge}</div>
                            <div class="psrc-pill" style="background:#03C75A">네이버</div>
                          </div>
                          <div class="pinfo">
                            <div class="pname">{row['상품명']}</div>
                            <div class="pbrand">{row.get('브랜드','')}</div>
                            <div class="pprice">{price_str}</div>
                            <div class="pmall">🏪 {row['판매처']}</div>
                          </div></div>""",unsafe_allow_html=True)
                        if row["판매처링크"]:
                            st.link_button("🔗 네이버 보기",row["판매처링크"],use_container_width=True)
                        st.markdown("<div style='margin-bottom:4px'></div>",unsafe_allow_html=True)

# ─ 탭4: 인스타그램 ───────────────────────────
with tab_ig:
    st.markdown('<div class="sec-head">📸 Instagram 해시태그 트렌드</div>', unsafe_allow_html=True)
    st.caption("#등원룩 #자매룩 #남매룩 #여아원피스 #남아패션 #여아패션")
    if df_ig.empty:
        st.info("인스타그램 데이터가 없어요. `python platform_crawler.py` 실행 후 새로고침하세요.")
    else:
        # 해시태그별 필터
        tags=df_ig["분류"].unique().tolist()
        sel_tag=st.multiselect("해시태그 선택",tags,default=tags)
        ig_filtered=df_ig[df_ig["분류"].isin(sel_tag)].reset_index(drop=True)
        st.caption(f"총 {len(ig_filtered)}개 게시물")
        cols=st.columns(col_n,gap="small")
        for idx,row in ig_filtered.iterrows():
            with cols[idx%col_n]:
                img_html=(f'<img src="{row["이미지URL"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=noimg>📸</div>\'">' if row["이미지URL"] else '<div class="noimg">📸</div>')
                st.markdown(f"""<div class="pcard">
                  <div class="pimg-wrap">{img_html}
                    <div class="psrc-pill" style="background:#E1306C">IG</div>
                  </div>
                  <div class="pinfo">
                    <span class="b-sns">SNS</span>
                    <div class="pname" style="margin-top:3px">{row['상품명'][:60]}</div>
                    <div class="phashtag">{row.get('리뷰정보','')}</div>
                  </div></div>""",unsafe_allow_html=True)
                if row["판매처링크"]:
                    st.link_button("📸 인스타 보기",row["판매처링크"],use_container_width=True)
                st.markdown("<div style='margin-bottom:4px'></div>",unsafe_allow_html=True)

# ─ 탭5: 핀터레스트 ───────────────────────────
with tab_pin:
    st.markdown('<div class="sec-head">📌 Pinterest 키즈 패션 최신 핀</div>', unsafe_allow_html=True)
    st.caption("Kids fashion · Toddler fashion · Girls · Boys · Fashion")
    if df_pin.empty:
        st.info("핀터레스트 데이터가 없어요. `python platform_crawler.py` 실행 후 새로고침하세요.")
    else:
        queries=df_pin["분류"].unique().tolist()
        sel_q=st.multiselect("검색어 선택",queries,default=queries)
        pin_filtered=df_pin[df_pin["분류"].isin(sel_q)].reset_index(drop=True)
        st.caption(f"총 {len(pin_filtered)}개 핀")
        # 핀터레스트는 열 수를 더 넓게
        pin_cols=st.columns(min(col_n+1,5),gap="small")
        for idx,row in pin_filtered.iterrows():
            with pin_cols[idx%min(col_n+1,5)]:
                img_html=(f'<img src="{row["이미지URL"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=noimg>📌</div>\'">' if row["이미지URL"] else '<div class="noimg">📌</div>')
                st.markdown(f"""<div class="pcard">
                  <div class="pimg-wrap">{img_html}
                    <div class="psrc-pill" style="background:#E60023">PIN</div>
                  </div>
                  <div class="pinfo">
                    <div class="pname">{row['상품명'][:50]}</div>
                    <div class="phashtag">{row.get('분류','')}</div>
                  </div></div>""",unsafe_allow_html=True)
                if row["판매처링크"]:
                    st.link_button("📌 핀 보기",row["판매처링크"],use_container_width=True)
                st.markdown("<div style='margin-bottom:4px'></div>",unsafe_allow_html=True)

# ── 하단 테이블 ───────────────────────────────
st.markdown('<hr class="div">', unsafe_allow_html=True)
with st.expander("📋 전체 데이터 테이블 / CSV 다운로드"):
    show_cols=["플랫폼","출처","분류","상품명","최저가","브랜드","판매처","수집일시"]
    avail=[c for c in show_cols if c in df_all.columns]
    st.dataframe(df_all[avail],use_container_width=True,hide_index=True)
    st.download_button("⬇️ CSV 다운로드",
                       df_all.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),
                       "kids_trend_all.csv","text/csv")

st.markdown('<div style="text-align:center;color:#ddd;font-size:.7rem;padding:1.5rem 0 .5rem">아동복 트렌드 대시보드 v4 · 쿠팡+네이버+Instagram+Pinterest</div>',unsafe_allow_html=True)

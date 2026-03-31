"""
네이버 API로 쿠팡 상품 수집  —  coupang_via_naver.py
쿠팡 API 없이 네이버 쇼핑 API로 쿠팡 판매 상품을 가져옵니다.
실행: python coupang_via_naver.py
"""
import requests, re, html, time, os
import pandas as pd
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

NAVER_CLIENT_ID     = "7osKrkK7ta0h97fmWvfb"
NAVER_CLIENT_SECRET = "rpG_hXnDJA"  # ← 재발급 필요시 교체

KEYWORDS = [
    "유아동 원피스",
    "유아동 맨투맨",
    "유아동 의류",
    "아동 바람막이",
    "유아 잠옷",
    "유아 신발",
    "아동복",
    "키즈 패딩",
]

def fetch(keyword, display=100):
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    # 인기순과 최신순 모두 수집
    items = []
    for sort in ["sim", "date"]:
        try:
            r = requests.get(
                "https://openapi.naver.com/v1/search/shop.json",
                headers=headers,
                params={"query": keyword, "display": display, "sort": sort},
                timeout=10,
            )
            r.raise_for_status()
            items += r.json().get("items", [])
            time.sleep(0.2)
        except Exception as e:
            print(f"  [{keyword}] 오류: {e}")
    return items

def main():
    print("=" * 55)
    print("  🛒 네이버 API → 쿠팡 상품 수집기")
    print("=" * 55)

    all_rows = []
    coupang_rows = []

    for kw in KEYWORDS:
        items = fetch(kw)
        coupang_items = [i for i in items if "쿠팡" in i.get("mallName", "")]
        other_items   = [i for i in items if "쿠팡" not in i.get("mallName", "")]

        print(f"  [{kw}] 전체 {len(items)}개 → 쿠팡 {len(coupang_items)}개")

        for item in coupang_items:
            name = html.unescape(re.sub(r"<[^>]+>", "", item.get("title", "")))
            img  = item.get("image", "")
            coupang_rows.append({
                "플랫폼":     "쿠팡",
                "플랫폼색상": "C0392B",
                "분류":       f"{kw} 인기순",
                "검색키워드": kw,
                "상품명":     name,
                "최저가":     int(item.get("lprice", 0)),
                "판매처":     "쿠팡",
                "판매처링크": item.get("link", ""),
                "이미지URL":  img,
                "브랜드":     item.get("brand", ""),
                "리뷰정보":   "",
                "출처":       "국내",
                "is_new":     False,
                "수집일시":   NOW,
            })

        # 쿠팡 외 다른 판매처도 수집
        for item in other_items[:10]:
            name = html.unescape(re.sub(r"<[^>]+>", "", item.get("title", "")))
            all_rows.append({
                "플랫폼":     "네이버 쇼핑",
                "플랫폼색상": "03C75A",
                "분류":       f"{kw}",
                "검색키워드": kw,
                "상품명":     name,
                "최저가":     int(item.get("lprice", 0)),
                "판매처":     item.get("mallName", ""),
                "판매처링크": item.get("link", ""),
                "이미지URL":  item.get("image", ""),
                "브랜드":     item.get("brand", ""),
                "리뷰정보":   "",
                "출처":       "국내",
                "is_new":     False,
                "수집일시":   NOW,
            })

    all_rows = coupang_rows + all_rows

    if not all_rows:
        print("\n  수집 실패. 네이버 API 키를 확인하세요.")
        return

    df = pd.DataFrame(all_rows)
    df["최저가"] = pd.to_numeric(df["최저가"], errors="coerce").fillna(0).astype(int)

    # 기존 SNS 데이터(인스타/핀터) 보존하고 쇼핑 데이터만 교체
    if os.path.exists("all_data.csv"):
        old = pd.read_csv("all_data.csv", encoding="utf-8-sig")
        old.columns = old.columns.str.strip()
        sns = old[old["출처"] == "SNS"] if "출처" in old.columns else pd.DataFrame()
        df  = pd.concat([df, sns], ignore_index=True)

    df = df.drop_duplicates(subset=["상품명", "판매처링크"], keep="first")
    df.to_csv("all_data.csv",  index=False, encoding="utf-8-sig")
    df.to_csv("kids_data.csv", index=False, encoding="utf-8-sig")

    print(f"\n{'='*55}")
    print(f"  💾 저장 완료: 총 {len(df)}개")
    print(f"  쿠팡 상품:    {len(coupang_rows)}개")
    print(f"  네이버 상품:  {len(all_rows)-len(coupang_rows)}개")
    print(f"{'='*55}")
    print("\n🎉 완료! 이제 GitHub에 push하면 배포 사이트에 반영돼요.")
    print("   git add all_data.csv kids_data.csv")
    print("   git commit -m '쿠팡+네이버 업데이트'")
    print("   git push")

if __name__ == "__main__":
    main()

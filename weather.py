import requests
import pandas as pd
from datetime import datetime

# =========================
# 1. 분석 날짜
# =========================
TARGET_DATE = "2024-06-01"


# =========================
# 2. 날씨 (API KEY 없음)
# =========================
def get_weather(date):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude=37.5665&longitude=126.9780"
        f"&start_date={date}&end_date={date}"
        "&daily=temperature_2m_mean,precipitation_sum,weather_code"
        "&timezone=Asia%2FSeoul"
    )

    res = requests.get(url)
    data = res.json()["daily"]

    return {
        "date": date,
        "temp": data["temperature_2m_mean"][0],
        "rain": data["precipitation_sum"][0],
        "code": data["weather_code"][0]
    }


# =========================
# 3. 지하철 데이터 (키 없음 - 고정 샘플)
# =========================
def get_subway(date):
    # 실제 API 대신 "현실적인 샘플 데이터"
    # 포트폴리오용 핵심: 구조 설명

    data = [
        {"station": "강남", "ride": 120000},
        {"station": "홍대입구", "ride": 95000},
        {"station": "잠실", "ride": 110000},
        {"station": "서울역", "ride": 130000},
        {"station": "신촌", "ride": 87000},
        {"station": "건대입구", "ride": 78000},
    ]

    return pd.DataFrame(data)


# =========================
# 4. 날씨 영향 점수
# =========================
def weather_score(weather):
    score = 0

    if weather["code"] == 0:
        score -= 1  # 맑음 → 분산
    if weather["rain"] > 0:
        score += 2  # 비 → 지하철 증가
    if weather["temp"] > 30:
        score += 1  # 폭염 → 실내 이동

    return score


# =========================
# 5. 분석
# =========================
def analyze(subway_df, score):
    subway_df = subway_df.copy()
    subway_df["final_score"] = subway_df["ride"] * (1 + score * 0.1)

    return subway_df.sort_values("final_score", ascending=False)


# =========================
# 6. HTML 생성
# =========================
def make_html(weather, df):

    rows = ""
    for _, r in df.iterrows():
        rows += f"""
        <tr>
            <td>{r['station']}</td>
            <td>{r['ride']:,}</td>
            <td>{int(r['final_score']):,}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>서울 교통 분석</title>
<style>
body {{
    font-family: Arial;
    margin: 40px;
}}
table {{
    border-collapse: collapse;
    width: 60%;
}}
th, td {{
    border: 1px solid #ccc;
    padding: 10px;
}}
th {{
    background: #222;
    color: white;
}}
</style>
</head>

<body>

<h2>서울 날씨 기반 대중교통 분석</h2>

<p>날짜: {weather['date']}</p>
<p>기온: {weather['temp']}°C</p>
<p>강수량: {weather['rain']}mm</p>

<h3>지하철 혼잡도 분석</h3>

<table>
<tr>
<th>역</th>
<th>기본 이용량</th>
<th>날씨 반영 값</th>
</tr>

{rows}
</table>

</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("완료: index.html 생성됨")


# =========================
# 7. 실행
# =========================
if __name__ == "__main__":

    weather = get_weather(TARGET_DATE)
    score = weather_score(weather)

    subway = get_subway(TARGET_DATE)

    result = analyze(subway, score)

    make_html(weather, result)

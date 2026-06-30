import requests

# =========================
# 1. 도시 (실데이터 기반)
# =========================
CITIES = {
    "서울": (37.5665, 126.9780),
    "부산": (35.1796, 129.0756),
    "대구": (35.8722, 128.6025),
    "제주": (33.4996, 126.5312),
    "인천": (37.4563, 126.7052),
    "광주": (35.1595, 126.8526),
    "울산": (35.5384, 129.3114),
}


# =========================
# 2. 실제 기후 데이터
# =========================
def fetch_weather(lat, lon, year):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={year}-01-01&end_date={year}-12-31"
        "&daily=temperature_2m_mean,precipitation_sum"
        "&timezone=Asia%2FSeoul"
    )

    res = requests.get(url).json()["daily"]

    temps = [t for t in res["temperature_2m_mean"] if t is not None]
    rains = [r for r in res["precipitation_sum"] if r is not None]

    return {
        "avg_temp": sum(temps) / len(temps),
        "total_rain": sum(rains),
        "temp_range": max(temps) - min(temps)
    }


# =========================
# 3. 변화량 계산
# =========================
def compute_change(old, new):
    return {
        "temp_change": new["avg_temp"] - old["avg_temp"],
        "rain_change": new["total_rain"] - old["total_rain"],
        "range_change": new["temp_range"] - old["temp_range"],
    }


# =========================
# 4. HTML 보고서 생성
# =========================
def make_report(results):

    rows = ""

    for r in results:
        c = r["city"]
        ch = r["change"]

        # 강조 색상
        if ch["temp_change"] > 1:
            badge = "🔴 급격한 온난화"
        elif ch["temp_change"] > 0:
            badge = "🟠 온난화 진행"
        else:
            badge = "🔵 안정"

        rows += f"""
        <tr>
            <td>{c}</td>
            <td>{round(ch['temp_change'],2)}°C</td>
            <td>{round(ch['rain_change'],2)} mm</td>
            <td>{round(ch['range_change'],2)}</td>
            <td>{badge}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Korea Climate Change Report</title>

<style>
body {{
    font-family: Arial;
    margin: 0;
    background: #f4f6f9;
}}

.header {{
    background: #111827;
    color: white;
    padding: 30px;
}}

.container {{
    padding: 30px;
}}

.card {{
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 12px;
    overflow: hidden;
}}

th {{
    background: #1f2937;
    color: white;
    padding: 12px;
}}

td {{
    padding: 12px;
    border-bottom: 1px solid #eee;
    text-align: center;
}}

tr:hover {{
    background: #f9fafb;
}}

.badge {{
    padding: 4px 8px;
    border-radius: 8px;
    font-size: 12px;
}}
</style>
</head>

<body>

<div class="header">
<h1>🇰🇷 한국 도시 기후 변화 분석 보고서</h1>
<p>2023 vs 2024 실제 기상 데이터 기반 분석</p>
</div>

<div class="container">

<div class="card">
<h2>📊 분석 개요</h2>
<p>
본 보고서는 Open-Meteo 실제 기상 데이터를 기반으로<br>
한국 주요 도시의 기후 변화량을 비교 분석한 결과이다.
</p>
</div>

<div class="card">
<h2>🌡 주요 분석 기준</h2>
<ul>
<li>평균 기온 변화</li>
<li>연간 강수량 변화</li>
<li>기온 변동성 변화</li>
</ul>
</div>

<div class="card">
<h2>📈 도시별 기후 변화 결과</h2>

<table>
<tr>
<th>도시</th>
<th>기온 변화</th>
<th>강수 변화</th>
<th>변동성 변화</th>
<th>상태</th>
</tr>

{rows}
</table>

</div>

</div>

</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("완료: index.html 보고서 생성")


# =========================
# 5. 실행
# =========================
if __name__ == "__main__":

    results = []

    for city, (lat, lon) in CITIES.items():

        old = fetch_weather(lat, lon, 2023)
        new = fetch_weather(lat, lon, 2024)

        change = compute_change(old, new)

        results.append({
            "city": city,
            "change": change
        })

    make_report(results)

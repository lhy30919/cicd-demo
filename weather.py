import requests
import folium
from datetime import datetime

# =========================
# 1. 입력 도시 (이름만)
# =========================
CITIES = ["서울", "부산", "대구", "제주", "인천", "광주", "울산"]


# =========================
# 2. 도시 → 좌표 (정확 KR 필터)
# =========================
def get_city_coord(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=ko"

    res = requests.get(url).json()

    if "results" not in res:
        return None

    for r in res["results"]:
        if r.get("country_code") == "KR":
            return r["latitude"], r["longitude"]

    return None


# =========================
# 3. 연도별 날씨 데이터 수집
# =========================
def fetch_year_weather(lat, lon, year):
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
# 4. 변화량 계산 (핵심)
# =========================
def compute_change(data_2023, data_2024):

    return {
        "temp_change": data_2024["avg_temp"] - data_2023["avg_temp"],
        "rain_change": data_2024["total_rain"] - data_2023["total_rain"],
        "range_change": data_2024["temp_range"] - data_2023["temp_range"],
    }


# =========================
# 5. 지도 생성
# =========================
def build_map(results):

    m = folium.Map(location=[36.2, 127.8], zoom_start=7)

    for r in results:

        city = r["city"]
        lat, lon = r["coord"]

        popup = f"""
        <b>{city}</b><br>
        🌡 온도 변화: {round(r['change']['temp_change'],2)}°C<br>
        🌧 강수 변화: {round(r['change']['rain_change'],2)}mm<br>
        📊 기후 변동성: {round(r['change']['range_change'],2)}<br>
        """

        # 색상 기준 (변화량)
        if r["change"]["temp_change"] > 1:
            color = "red"
        elif r["change"]["temp_change"] > 0:
            color = "orange"
        else:
            color = "blue"

        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup, max_width=300),
            tooltip=city
        ).add_to(m)

    m.save("index.html")


# =========================
# 6. 실행
# =========================
if __name__ == "__main__":

    results = []

    for city in CITIES:

        coord = get_city_coord(city)

        if not coord:
            continue

        lat, lon = coord

        # 2023 / 2024 실제 데이터
        data_2023 = fetch_year_weather(lat, lon, 2023)
        data_2024 = fetch_year_weather(lat, lon, 2024)

        change = compute_change(data_2023, data_2024)

        results.append({
            "city": city,
            "coord": coord,
            "change": change
        })

    build_map(results)

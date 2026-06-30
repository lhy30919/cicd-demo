import requests
import folium

START_DATE = "2024-01-01"
END_DATE = "2024-12-31"


# =========================
# 1. 도시 → 좌표 (실데이터)
# =========================
def get_city_coord(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ko"

    res = requests.get(url).json()

    if "results" not in res:
        return None

    r = res["results"][0]
    return r["latitude"], r["longitude"]


# =========================
# 2. 날씨 데이터 (실데이터)
# =========================
def fetch_weather(lat, lon):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={START_DATE}&end_date={END_DATE}"
        "&daily=temperature_2m_mean,precipitation_sum"
        "&timezone=Asia%2FSeoul"
    )

    data = requests.get(url).json()["daily"]

    temps = data["temperature_2m_mean"]
    rains = data["precipitation_sum"]

    temps = [t for t in temps if t is not None]
    rains = [r for r in rains if r is not None]

    avg_temp = sum(temps) / len(temps)
    total_rain = sum(rains)
    temp_range = max(temps) - min(temps)

    return avg_temp, total_rain, temp_range


# =========================
# 3. 점수 계산 (파생값)
# =========================
def score(avg_temp, rain, temp_range):
    return round(
        100
        - temp_range * 1.3
        - rain * 0.05
        + (22 - abs(avg_temp - 22)) * 2,
        2
    )


# =========================
# 4. 지도 생성
# =========================
def build_map(cities):

    m = folium.Map(location=[36.3, 127.8], zoom_start=7)

    for city in cities:
        coord = get_city_coord(city)
        if not coord:
            continue

        lat, lon = coord

        avg_temp, rain, temp_range = fetch_weather(lat, lon)
        s = score(avg_temp, rain, temp_range)

        popup_text = f"""
        <b>{city}</b><br>
        점수: {s}<br>
        평균기온: {round(avg_temp,1)}°C<br>
        강수량: {round(rain,1)}mm<br>
        변동폭: {round(temp_range,1)}°C
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=city
        ).add_to(m)

    m.save("korea_map.html")
    print("완료: korea_map.html 생성")


# =========================
# 5. 실행
# =========================
if __name__ == "__main__":

    city_list = [
        "서울",
        "부산",
        "제주",
        "대구",
        "인천",
        "광주",
        "울산",
        "대전"
    ]

    build_map(city_list)

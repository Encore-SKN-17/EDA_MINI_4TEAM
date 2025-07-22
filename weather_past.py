import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def crawl_weather_data_from_kma(start_year, end_year, area_code="108"):
    base_url = "https://www.weather.go.kr/w/observation/land/past-obs/obs-by-element.do"
    
    all_data = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13): 
            params = {
                "stn": area_code,  
                "yy": str(year),  
                "mm": str(month).zfill(2), 
                "obs": "07" 
            }
            
            print(f"Fetching data for: {year}년 {month}월")
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status() 

                soup = BeautifulSoup(response.text, 'html.parser')
                
             
                table = soup.find("table", {"id": "weather_table"})
                
                if table:
                    rows = table.find_all("tr")
                    
                    for row in rows[2:]: 
                        cols = row.find_all("td")
                        
                        if len(cols) >= 8:
                            day_text = cols[0].get_text(strip=True)
                            day = day_text.replace('일', '') 
                            
                            avg_temp = cols[1].get_text(strip=True)
                            min_temp = cols[2].get_text(strip=True)
                            max_temp = cols[3].get_text(strip=True)
                            
                          
                            rain_amount = cols[7].get_text(strip=True) 
                            
                   
                            avg_temp = None if avg_temp == "-" else avg_temp
                            min_temp = None if min_temp == "-" else min_temp
                            max_temp = None if max_temp == "-" else max_temp
                            rain_amount = None if rain_amount == "-" else rain_amount

              
                            date_str = f"{year}-{str(month).zfill(2)}-{day.zfill(2)}"
                            
                            all_data.append({
                                "날짜": date_str,
                                "평균 기온": avg_temp,
                                "최저 기온": min_temp,
                                "최고 기온": max_temp,
                                "강수량": rain_amount
                            })
                else:
                    print(f"{year}년 {month}월 데이터 테이블(id='weather_table')을 찾을 수 없습니다. (URL: {response.url})")

            except requests.exceptions.RequestException as e:
                print(f"데이터 요청 중 오류 발생 ({year}년 {month}월): {e}")
            except Exception as e:
                print(f"데이터 파싱 중 오류 발생 ({year}년 {month}월): {e}")
                
    df = pd.DataFrame(all_data)
    return df

start_crawl_year = 1995
end_crawl_year = 1999 

print(f"크롤링 범위: {start_crawl_year}년 ~ {end_crawl_year}년")
weather_df = crawl_weather_data_from_kma(start_crawl_year, end_crawl_year, area_code="108") 


weather_df["날짜"] = pd.to_datetime(weather_df["날짜"], errors='coerce')

weather_df["평균 기온"] = pd.to_numeric(weather_df["평균 기온"], errors='coerce')
weather_df["최저 기온"] = pd.to_numeric(weather_df["최저 기온"], errors='coerce')
weather_df["최고 기온"] = pd.to_numeric(weather_df["최고 기온"], errors='coerce')


weather_df["강수량"] = pd.to_numeric(weather_df["강수량"], errors='coerce')
weather_df["강수량"] = weather_df["강수량"].fillna(0.0)


weather_df["평균 기온"] = weather_df["평균 기온"].fillna(0.0)
weather_df["최저 기온"] = weather_df["최저 기온"].fillna(0.0)
weather_df["최고 기온"] = weather_df["최고 기온"].fillna(0.0)


print("\n전처리된 데이터 초기 5행:")
print(weather_df.head())
print("\n전처리된 데이터 정보:")
weather_df.info()

print("\n최종 강수량 컬럼 정보:")
print(weather_df["강수량"].describe())
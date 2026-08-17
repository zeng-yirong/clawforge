import os
import csv

def build_env():
    # 创建数据目录和输出目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. flights.csv
    flights = [
        ["route_id","origin","destination","airline","price_cny","date"],
        ["F101","BJS","SHA","CA","800","2025-06-01"],
        ["F102","BJS","SHA","MU","750","2025-06-01"],
        ["F103","BJS","GZ","CZ","600","2025-06-01"],          # 诱饵：不是去上海
        ["F104","BJS","SHA","CA","700","2024-03-01"],          # 过期
    ]
    with open("data/flights.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(flights)

    # 2. trains.csv
    trains = [
        ["route_id","origin","destination","train_type","price","currency","date"],
        ["T201","BJS","SHA","G123","500","CNY","2025-06-01"],   # 高铁 500元
        ["T202","BJS","SHA","G456","100","USD","2025-06-01"],   # USD → 700元
        ["T203","BJS","SHA","D789","400","CNY","2024-05-01"],   # 过期
    ]
    with open("data/trains.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(trains)

    # 3. buses.csv
    buses = [
        ["route_id","origin","destination","bus_company","price_cny","date"],
        ["B301","BJS","SHA","Long-distance","200","2025-06-01"],  # 唯一最便宜有效
        ["B302","BJS","SHA","Express","180","2024-04-01"],        # 过期
        ["B304","BJS","GZ","Long-distance","150","2025-06-01"],   # 诱饵
    ]
    with open("data/buses.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(buses)

    # 4. 诱饵文件
    with open("data/notes.txt","w") as f:
        f.write("这是随手备忘录，不是数据，别管我。\n")

if __name__ == "__main__":
    build_env()

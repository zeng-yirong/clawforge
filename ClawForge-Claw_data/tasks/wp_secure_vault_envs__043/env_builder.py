import os
import csv
import pathlib

def build_env():
    # 创建 vault 目录
    os.makedirs("vault", exist_ok=True)

    # 主凭证文件 credentials.csv
    rows = [
        ["id","platform","category","username","password","strength","last_used","expired"],
        ["1","blog","社交媒体","user1","pass123","30","2025-01-10","no"],
        ["2","twitter","社交媒体","user2","securepass","80","2025-01-12","no"],
        ["3","insta","工作邮箱","user3","weak","10","2025-01-15","no"],
        ["4","fb","社交媒体","user4","longpassword123456","45","2025-01-20","no"],
        ["5","linkedin","社交媒体","user5","mediumpass","55","2025-01-18","no"],
        ["6","tiktok","社交媒体","user6","shortpass","20","2025-01-22","no"],
        ["7","snapchat","社交媒体","user7","verylongpassword789012","35","2025-01-25","no"],
        ["8","pinterest","社交媒体","user8","expiring","15","2025-01-05","yes"],
        ["9","reddit","社交媒体","user9","aaabbbcccddd","25","2025-01-28","no"],
        ["10","discord","社交媒体","user10","test1234","40","2025-01-30","no"],
    ]
    with open("vault/credentials.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # 干扰文件：旧备份（列名不同，且不含社交媒体）
    old_rows = [
        ["id","app","user","pwd","score","date","expired"],
        ["o1","mail","admin","secret","90","2024-12-01","no"],
        ["o2","bank","finance","money","70","2024-11-15","yes"],
    ]
    with open("vault/old_credentials.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)

    # 干扰文本
    with open("vault/readme.txt", "w") as f:
        f.write("这是遗留凭证备份，最新的在 credentials.csv 里。\n")

if __name__ == "__main__":
    build_env()

import os
import mysql.connector
import pandas as pd
from datetime import datetime
import pytz
def time_compare(bj_time,time_str,day: int,beijing_tz):
    # 指定的时间（北京时间）
    # target_time_str = "2024-09-20 19:09:11"
    target_time = datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S").replace(tzinfo=beijing_tz)

    # 计算时间差
    time_difference = bj_time - target_time
    days_difference = abs(time_difference.days)

    # 判断时间差并输出结果
    if days_difference <= day:
        return True

# 连接到W数据库
def connect_to_database():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )

# 获取所有文章的标题、简介、分类和链接
def get_posts_data(connection):
    cursor = connection.cursor()
    query = os.getenv("SQL")

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results



# 生成Markdown表格
def generate_markdown_tables(posts_data,bj_time,day,beijing_tz):
    df = pd.DataFrame(posts_data, columns=["title", "description", "category", "link", "date"])

    # 按分类分组
    grouped = df.groupby("category")

    markdown_tables = []

    for category, group in grouped:
        markdown_table = f"## {category}\n\n"
        if time_compare(bj_time,group['date'].iloc[0],day,beijing_tz):
            group['title'] = group.apply(lambda row: f"[**新增**] [{row['title']}]({row['link']})", axis=1)
        else:
            group['title'] = group.apply(lambda row: f"[{row['title']}]({row['link']})", axis=1)
        # 选择特定的列
        selected_columns = ['title', 'description']
        df_selected = group.loc[:, selected_columns]
        markdown_table += df_selected.to_markdown(index=False)
        markdown_tables.append(markdown_table)

    return "\n\n".join(markdown_tables)

# 将Markdown内容写入文件
def write_to_markdown_file(markdown_content, beijing_time, filename="README.md"):
    with open(filename, "w", encoding="utf-8") as file:
        markdown_header = f"# 出海工具箱\n\n> 本文档更新时间:{beijing_time}，欢迎star。[**新增**] 表示7天内增加的。\n\n[出海工具箱](http://www.chgjx.com)收集各类建站、SEO、选品、营销推广等工具，为广大独立开发者出海，跨境电商从业者，自媒体从业者服务，助力您取得成功！\n\n"
        file.write(markdown_header)
        file.write(markdown_content)

# 主函数
def main():
        # 获取当前的UTC时间
    utc_now = datetime.now(pytz.utc)

    # 将UTC时间转换为北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = utc_now.astimezone(beijing_tz)
    time_obj = datetime.fromisoformat(str(beijing_time))
    formatted_time = time_obj.strftime("%Y-%m-%d %H:%M:%S")

    connection = connect_to_database()
    posts_data = get_posts_data(connection)
    markdown_content = generate_markdown_tables(posts_data,beijing_time,7,beijing_tz)
    write_to_markdown_file(markdown_content,formatted_time)
    connection.close()

if __name__ == "__main__":
    main()
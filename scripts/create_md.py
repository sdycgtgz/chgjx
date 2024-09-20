import os
import mysql.connector
import pandas as pd


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
def generate_markdown_tables(posts_data):
    df = pd.DataFrame(posts_data, columns=["title", "description", "category", "link"])

    # 按分类分组
    grouped = df.groupby("category")
    markdown_tables = []

    for category, group in grouped:
        markdown_table = f"## {category}\n\n"
        group['title'] = group.apply(lambda row: f"[{row['title']}]({row['link']})", axis=1)
        # 选择特定的列
        selected_columns = ['title', 'description']
        df_selected = group.loc[:, selected_columns]
        markdown_table += df_selected.to_markdown(index=False)
        markdown_tables.append(markdown_table)

    return "\n\n".join(markdown_tables)

# 将Markdown内容写入文件
def write_to_markdown_file(markdown_content, filename="README.md"):
    with open(filename, "w", encoding="utf-8") as file:
        markdown_header = "# 出海工具箱\n\n> 本文档每天更新，欢迎star。\n\n[出海工具箱](http://www.chgjx.com)出海工具箱，收集各类建站、SEO选品、营销推广等工具，为广大独立开发者出海，跨境电商从业者，自媒体从业者服务，助力您取得成功！\n\n"
        file.write(markdown_header)
        file.write(markdown_content)

# 主函数
def main():
    connection = connect_to_database()
    posts_data = get_posts_data(connection)
    markdown_content = generate_markdown_tables(posts_data)
    write_to_markdown_file(markdown_content)
    connection.close()

if __name__ == "__main__":
    main()
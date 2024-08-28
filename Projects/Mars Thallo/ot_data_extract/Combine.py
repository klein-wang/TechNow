import pandas as pd

# 手动列出所有的文件名
file_names = ['1.csv', '2.csv', '3.csv', '4.csv', '5.csv']

# 初始化一个空的DataFrame来存储合并的数据
combined_df = pd.DataFrame()
# 定义正确的标题
expected_header = ['Tag', 'TS', 'Value']

# 读取每个CSV文件并追加到combined_df中
for file in file_names:
    # 先读取文件的前几行，获取header
    print(f'Reading {file}')
    df = pd.read_csv(file, nrows=0)
    current_header = df.columns.tolist()

    # 如果header不符合预期，则重新读取并添加header
    if current_header != expected_header:
        df = pd.read_csv(file, header=None, names=expected_header)
    else:
        df = pd.read_csv(file)
    
    # 合并数据
    combined_df = pd.concat([combined_df, df])

# format TS
combined_df['TS'] = pd.to_datetime(combined_df['TS'], format="mixed", utc=True).dt.tz_localize(None) #%Y-%m-%d %H:%M:%S.%f %z
combined_df['TS'] = combined_df['TS'].dt.floor('s')

# 删除基于TS和Tag字段的重复行，只保留第一次出现的记录
combined_df = combined_df.drop_duplicates(subset=['TS', 'Tag'])

combined_df = combined_df.sort_values(by='TS')
pivot_df = combined_df.pivot(index='TS', columns='Tag', values='Value').reset_index()
print(pivot_df['TS'].min(), pivot_df['TS'].max())

# 将合并后的数据保存到一个新的CSV文件中
pivot_df.to_csv('transformed_sorted_file.csv', index=False)

print("CSV files have been merged and sorted successfully.")

# import packages
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil import parser


def get_current_date():
    now = datetime.now()
    return now.strftime("%Y%m%d")

def convert_contract(input_file):

    # Read the Excel file
    df = pd.read_excel(input_file, sheet_name='FF_OUTLINE_AGG_PRELOAD')
    print('reading data')

    # Extract the names after the period in the header row
    new_header = [col.split('.')[-1] if '.' in col else '' for col in df.columns]

    # Replace the header row with the extracted names
    df.columns = new_header

    # Read the "field mapping" sheet
    mapping_df = pd.read_excel(input_file, sheet_name='field mapping')


    # Get the order of columns from the "ACTION_KEYS" column
    order_list = mapping_df['KEYS'].tolist()
    # Drop duplicate columns from the DataFrame
    df = df.loc[:, ~df.columns.duplicated()]

    # # Create a new list for reordered columns
    # reordered_columns = []

    # # Reorder the columns based on the "ACTION_KEYS" order and add empty columns for missing columns
    # for col in order_list:
    #     if col in df.columns:
    #         reordered_columns.append(col)
    #     else:
    #         reordered_columns.append('')

    # # Reindex the DataFrame with the reordered columns
    # df = df.reindex(columns=reordered_columns)

    # Create a new DataFrame with reordered columns
    reordered_df = pd.DataFrame(columns=order_list)

    # Copy data from original DataFrame to reordered DataFrame
    for col in order_list:
        if col in df.columns:
            reordered_df[col] = df[col]
            print(f'Column ',col,'is existed.')
        else:
            reordered_df[col] = np.nan
            print(f'Column ',col,'is missing.')

    # Create a new sheet for the modified data
    new_sheet_name = 'contract for upload'
    reordered_df.to_excel("output.xlsx", sheet_name=new_sheet_name, index=False)
    print('yes')


###########################################################
# Invoke function 调用函数
if __name__ == '__main__':
    today = get_current_date()
    input_file = 'P40_OUTLINE_AGGR_PRELOAD_CHINA.xlsx'
    # convert contract data 
    convert_contract(input_file)
    # export the file
    print("completed")
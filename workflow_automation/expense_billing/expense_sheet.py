# import packages
import pandas as pd
from datetime import datetime
from dateutil import parser


def get_current_date():
    now = datetime.now()
    return now.strftime("%Y%m%d")


def extract_expense(input_name):

    # Read Excel file and select "RawData" sheet
    input_file = pd.read_excel(input_name, sheet_name='RawData')
    # Filter for "Non Payroll" in Category Group column
    df = input_file[input_file['Category Group'] == 'Non Payroll']
    # Filter for categories starting with "travel" in Category column
    df = df[df['Category'].str.startswith('Travel')]
    # Filter for "B9SJF001 - ASEAN Standard" in WMULevel2 column
    df = df[df['WMULevel2'] == 'B9SJF001 - China Korea L1']
    # Select specified columns
    df = df[['DocumentDate', 'Category', 'Description',
             'AccountNbr Description', 'TransactionalAmt', 'TransactionalCurrency',
             'ReportingAmount', 'Enterprise ID']]
    # Rename columns
    df = df.rename(columns={'Description': 'Reference',
                            'AccountNbr Description': 'Description',
                             'ReportingAmount': 'Amount in USD'})

    # filter out records with empty DocumentDate
    df = df.dropna(subset=['DocumentDate'])

    # Add empty columns
    df['From'] = ''
    df['To'] = ''
    df['Start Date'] = ''
    df['End Date'] = ''
    df['Billable'] = 'Yes'

    return(df)


def expense_categorization(df):
    # Travel Related Cost - Air
    df.loc[(df['Category'] == 'Travel Related Cost - Air') &
           (df['Reference'].str[-4:-3] == '-'), 'Start Date'] = df['Reference'].str[-15:-8]
    df.loc[(df['Category'] == 'Travel Related Cost - Air') &
           (df['Reference'].str[-4:-3] != '-'), 'Start Date'] = df['Reference'].str[:6]
    df.loc[(df['Category'] == 'Travel Related Cost - Air') &
           (df['Reference'].str[-4:-3] == '-'), 'From'] = 'Airport ' + df['Reference'].str[-7:-4]
    df.loc[(df['Category'] == 'Travel Related Cost - Air') &
           (df['Reference'].str[-4:-3] == '-'), 'To'] = 'Airport ' + df['Reference'].str[-3:]

    # Travel Related Cost - Accommodation
    df.loc[(df['Category'] == 'Travel Related Cost - Accommodation') &
           (df['Reference'].str.contains('-')), 'Start Date'] = df['Reference'].str[:6]
    df.loc[(df['Category'] == 'Travel Related Cost - Accommodation') &
           (df['Reference'].str.contains('-')), 'From'] = 'China - Shanghai Hotel'

    # Travel Related Cost - Ground
    df.loc[(df['Category'] == 'Travel Related Cost - Ground') &
           (df['Reference'].str.contains('<-->')), 'Start Date'] = df['Reference'].str[:6]

    # Travel Related Cost - Meals & Per Diems
    df.loc[(df['Category'] == 'Travel Related Cost - Meals & Per Diems') &
           (df['Reference'].str.contains('-')), 'Start Date'] = df['Reference'].str[:6]
    df.loc[(df['Category'] == 'Travel Related Cost - Meals & Per Diems') &
           (df['Reference'].str.contains('-')), 'From'] = 'China - Per Diem: ' + df['Reference'].str[6:]

    # Travel Related Cost - Other
    df.loc[(df['Category'] == 'Travel Related Cost - Other') &
           (df['Reference'].str.contains('<-->')), 'Start Date'] = df['Reference'].str[:6]

    # add From, To for transportation
    df.loc[(df['Reference'].str.contains('<-->')), 'From'] = 'China - Client Visit'
    df.loc[(df['Reference'].str.contains('<-->')), 'To'] = 'China - Client Visit'
    # df.loc[(df['Reference'].str.contains('Airport')), 'From'] = \
    #     'China - ' + re.search(r"(.*)<-->.*", df['Reference'].str[6:]).group(1)
    # df.loc[(df['Reference'].str.contains('Airport')), 'To'] = \
    #     'China - ' + re.search(r".*<-->(.*)", df['Reference'].str[6:]).group(1)
    df.loc[(df['Reference'].str.contains('Airport')), 'To'] = 'China - Airport'

    # mark CHECK for unknown expense
    df.loc[(df['From'] == ''), 'Billable'] = 'CHECK!'
    # mark Unassigned for unknown expense
    df.loc[(df['Enterprise ID'] == 'Unassigned'), 'Billable'] = 'Unassigned Expense'
    # mark Verify From/To for airport-transport expense
    df.loc[(df['To'] == 'China - Airport'), 'Billable'] = 'Verify From/To'

    return(df)


def transform_date(date_str):
    try:
        return parser.parse(date_str).strftime('%Y-%m-%d')
    except ValueError:
        # Handle the case when the input cannot be parsed as a valid date
        return date_str


def export_report(df):

    # Checking: df.loc[(df['Start Date'] != '')].Start Date
    df['Start Date'] = df['Start Date'].apply(lambda x: transform_date(x) if x else x)
    # datetime.datetime.strptime(x, "%d%b%y").strftime("%Y/%m/%d")
    # datetime.datetime.strptime(x, "%d%m%y").strftime("%Y/%m/%d")

    # add End Date
    df['End Date'] = df['Start Date']

    # Export to Excel
    max_date = datetime.strptime(str(max(df.DocumentDate)), '%Y-%m-%d %H:%M:%S')
    max_date_str = max_date.strftime('%Y%m%d')
    df['DocumentDate'] = df['DocumentDate'].dt.strftime('%Y-%m-%d')

    output_file = f'Contour_Billable Expense_{max_date_str}.xlsx'
    df.to_excel(output_file, index=False)
    print(f'Output file: ',output_file)



###########################################################
# Invoke function 调用函数
if __name__ == '__main__':
    today = get_current_date()
    input_name = 'Cost Transaction Extract_20231009.xlsx'
    # extract expense records for China&Korea from MME report
    df = extract_expense(input_name)
    # fillin From,To,Start&End Date for each line records
    df_expense = expense_categorization(df)
    # transform date format
    # export the file
    export_report(df_expense)

from db_factory import SpcDBFactory
from datetime import datetime, timedelta
import pandas as pd

# 查询 spc数据
def get_spc_data(now, spc_table_name='dbo.TReceive', item_table_name='dbo.TItem'):
    conn = SpcDBFactory.create_conn()
    thirty_minutes_ago = now - timedelta(minutes=60)
    try:
        #获取重量数据
        SQL = """
                select a.FDate AS DataTime
                         ,a.FLoad AS Load
                         ,b.fItemName AS Item
                         ,a.fItemCode AS ItemCode
                         ,a.FZhong AS Weight
                         ,a.FbanCode AS shift
                         ,a.FHoudu AS LengthOrThickness
                         ,a.FShendu AS WidthOrDepth
                         ,a.FHStd AS LengthOrThickness_std
                         ,a.FSStd AS WidthOrDepth_std
                         ,a.FXJType AS EntryType
                         ,a.FZStd AS Weight_std
                FROM {} a LEFT JOIN {} b ON a.FItemCode = b.fItemCode
                WHERE a.FDate >= '{}' AND a.FDate <= '{}' AND a.FXJType = 3
                ORDER BY a.FDate DESC
        """.format(spc_table_name, item_table_name, thirty_minutes_ago.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S'))
        # 创建cursor对象
        cursor = conn.cursor()
        # 执行SQL查询
        cursor.execute(SQL)
        # 将查询结果转换为pandas DataFrame
        df = pd.DataFrame(cursor.fetchall()) 
        if len(df) > 0:
            # 给列名赋值
            df.columns = [col[0] for col in cursor.description]
        cursor.close()
        # 如果少于10个SPC数据
        if len(df) < 10:
            SQL = """
                Select top 10
                          a.FDate AS DataTime
                         ,a.FLoad AS Load
                         ,b.fItemName AS Item
                         ,a.fItemCode AS ItemCode
                         ,a.FZhong AS Weight
                         ,a.FbanCode AS shift
                         ,a.FHoudu AS LengthOrThickness
                         ,a.FShendu AS WidthOrDepth
                         ,a.FHStd AS LengthOrThickness_std
                         ,a.FSStd AS WidthOrDepth_std
                         ,a.FXJType AS EntryType
                         ,a.FZStd AS Weight_std
                FROM {} a LEFT JOIN {} b ON a.FItemCode = b.fItemCode
                WHERE a.FDate <= '{}' AND a.FXJType = 3
                ORDER BY a.FDate DESC
                """.format(spc_table_name, item_table_name, now.strftime('%Y-%m-%d %H:%M:%S'))
            # 创建cursor对象
            cursor = conn.cursor()
            # 执行SQL查询
            cursor.execute(SQL)
            # 将查询结果转换为pandas DataFrame
            df = pd.DataFrame(cursor.fetchall()) 
            # 给列名赋值
            df.columns = [col[0] for col in cursor.description]
            cursor.close()
        #获取长宽数据      
        SQL = """
                select a.FDate AS DataTime
                        ,a.FLoad AS Load
                        ,b.fItemName AS Item
                        ,a.fItemCode AS ItemCode
                        ,a.FZhong AS Weight
                        ,a.FbanCode AS shift
                        ,a.FHoudu AS LengthOrThickness
                        ,a.FShendu AS WidthOrDepth
                        ,a.FHStd AS LengthOrThickness_std
                        ,a.FSStd AS WidthOrDepth_std
                        ,a.FXJType AS EntryType
                        ,a.FZStd AS Weight_std
                FROM {} a LEFT JOIN {} b ON a.FItemCode = b.fItemCode
                WHERE a.FDate >= '{}' AND a.FDate <= '{}' AND a.FXJType = 2
                ORDER BY a.FDate DESC
        """.format(spc_table_name, item_table_name, thirty_minutes_ago.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S'))
        # 创建cursor对象
        cursor = conn.cursor()
        # 执行SQL查询
        cursor.execute(SQL)
        # 将查询结果转换为pandas DataFrame
        df_2 = pd.DataFrame(cursor.fetchall()) 
        if len(df_2) > 0:
            # 给列名赋值
            df_2.columns = [col[0] for col in cursor.description]
        cursor.close()

        # 如果少于10个SPC数据
        if len(df_2) < 10:
            SQL = """
                    select top 10
                            a.FDate AS DataTime
                            ,a.FLoad AS Load
                            ,b.fItemName AS Item
                            ,a.fItemCode AS ItemCode
                            ,a.FZhong AS Weight
                            ,a.FbanCode AS shift
                            ,a.FHoudu AS LengthOrThickness
                            ,a.FShendu AS WidthOrDepth
                            ,a.FHStd AS LengthOrThickness_std
                            ,a.FSStd AS WidthOrDepth_std
                            ,a.FXJType AS EntryType
                            ,a.FZStd AS Weight_std
                    FROM {} a LEFT JOIN {} b ON a.FItemCode = b.fItemCode
                    WHERE a.FDate <= '{}' AND a.FXJType = 2
                    ORDER BY a.FDate DESC
                """.format(spc_table_name, item_table_name, now.strftime('%Y-%m-%d %H:%M:%S'))
            # 创建cursor对象
            cursor = conn.cursor()
            # 执行SQL查询
            cursor.execute(SQL)
            # 将查询结果转换为pandas DataFrame
            df_2 = pd.DataFrame(cursor.fetchall()) 
            # 给列名赋值
            df_2.columns = [col[0] for col in cursor.description]

       #获取最新的厚度数据
        SQL = """
                select  top 1
                         a.FDate AS DataTime
                         ,a.FLoad AS Load
                         ,b.fItemName AS Item
                         ,a.fItemCode AS ItemCode
                         ,a.FZhong AS Weight
                         ,a.FbanCode AS shift
                         ,a.FHoudu AS LengthOrThickness
                         ,a.FShendu AS WidthOrDepth
                         ,a.FHStd AS LengthOrThickness_std
                         ,a.FSStd AS WidthOrDepth_std
                         ,a.FXJType AS EntryType
                         ,a.FZStd AS Weight_std
                FROM {} a LEFT JOIN {} b ON a.FItemCode = b.fItemCode
                WHERE a.FDate <= '{}' AND a.FXJType = 1
                ORDER BY a.FDate DESC
               """.format(spc_table_name, item_table_name, now.strftime('%Y-%m-%d %H:%M:%S'))
        # 创建cursor对象
        cursor = conn.cursor()
        # 执行SQL查询
        cursor.execute(SQL)
        # 将查询结果转换为pandas DataFrame
        df_3 = pd.DataFrame(cursor.fetchall()) 
        # 给列名赋值
        df_3.columns = [col[0] for col in cursor.description]
        cursor.close()

        #合并
        df = df.reset_index(drop=True)
        df_2 = df_2.reset_index(drop=True)
        df_3 = df_3.reset_index(drop=True)
        # df = pd.concat([df, df_2], ignore_index=True)
        df = pd.concat([df, df_3])
        df = df.reset_index(drop=True)
        df = pd.concat([df, df_2])
        return df
    
    except Exception as e:
        print(e)
        #logger.error("get_spc_weight_limit_data failed detail: {}".format(str(e)))
        #logger.error("get_spc_weight_limit_data failed detail: {}".format(traceback.format_exc()))
    finally:
        try:
            # 关闭cursor和连接
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)


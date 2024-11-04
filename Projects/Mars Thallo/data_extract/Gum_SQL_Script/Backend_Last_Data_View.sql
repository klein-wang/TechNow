SELECT TOP (1000) [id]
      ,[ts]
      ,[name]
      ,[value]
      ,[create_time]
      ,[update_time]
  FROM [dev-portaldb].[dbo].[yng_ts_raw_last_data]
  WHERE name = 'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_RealValue'
  Order BY update_time DESC

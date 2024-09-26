SELECT TOP (1000) [id]
      ,[Tag]
      ,[Value]
      ,[TS]
      ,[uuid]
      ,[TS2]
      ,[DBCreationDate]
  FROM [opc_timedata2].[dbo].[yng_ts_opc_data_log]
  WHERE [Tag] = 'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_RealValue'
  ORDER BY [TS] DESC

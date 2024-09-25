SELECT 
      [Tag]
      ,[Value]
      ,[TS]
  FROM [opc_timedata].[dbo].[yng_ts_opc_data_log]
  WHERE Tag IN (
    /*
    -- in production
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumEntranceTemperature', -- >= 32
	'CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp', -- >= 40
	'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rActualVelocityRPM', -- > 100 
	*/

	-- adjustment
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_SP',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio',
	'CG_Sheeting.CG_Sheeting.dbHMI.Variables.rSheetsPerMinuteSetpoint' -- line speed
)
AND [TS] > '2024-09-14 00:00:00' ORDER BY [TS] DESC

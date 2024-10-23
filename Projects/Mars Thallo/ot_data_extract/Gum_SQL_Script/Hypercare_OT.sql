SELECT 
      [Tag]
      ,[Value]
      ,[TS]
  FROM [opc_timedata2].[dbo].[yng_ts_opc_data_log] --new
  --FROM [opc_timedata].[dbo].[yng_ts_opc_data_log] --old till 2024/9/20
  --WHERE Tag IN ('CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches','CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches')
  --AND [TS] > '2024-10-13 20:15:00' AND Value <> 'N/A'


  WHERE Tag IN (
    -- Production
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumEntranceTemperature', -- cooling gum temp
	'CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp', -- extruder gum temp
	'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rActualVelocityRPM', -- cross score
	 'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio',
	-- Extruder
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_SP',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP',
	-- Roller
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rFormulaSP_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rFormulaSP_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rFormulaSP_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rFormulaSP_inches')
AND [TS] > '2024-10-16 00:00:00' ORDER BY [TS] ASC

SELECT 
	  --TOP 1000
      [Tag]
      ,[Value]
      ,[TS]
  FROM [opc_timedata2].[dbo].[yng_ts_opc_data_log] --new
  --FROM [opc_timedata].[dbo].[yng_ts_opc_data_log] --old till 2024/9/20
  --WHERE Tag IN ('CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches','CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches')
  --AND [TS] > '2024-10-13 20:15:00' AND Value <> 'N/A'


  WHERE Tag IN (
    -- Cooling
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumEntranceTemperature', -- for production
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumExitTempLeft',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumExitTempRight',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1OutletTemp',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2OutletTemp',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint',
	-- Cooling Pressure
    'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletPressure',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1OutletPressure',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletPressure',
	'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2OutletPressure',
	-- Extruder
	'CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp', -- for production
	'CG STI.CG STI.LoafGum.LoafGum01MaxTemp',
	'CG STI.CG STI.LoafGum.LoafGum01MinTemp',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_RealValue',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_RealValue',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_RealValue',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_SP',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP',
	'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP',
	-- Roller
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches',
	'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rActualVelocityRPM', -- for production
	'CG_Sheeting.CG_Sheeting.dbHMI.Variables.rSheetsPerMinuteSetpoint', -- line speed
	'SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning' -- line on_off status
)
AND [TS] > '2024-10-08 00:00:00' ORDER BY [TS] ASC

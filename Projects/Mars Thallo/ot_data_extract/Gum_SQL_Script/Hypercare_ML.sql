SELECT 
	  --TOP (1000) 
	   [id]
      ,[sku]
      ,[operator_status]
      ,[operator_reason]
      ,[update_by]
      ,[data_time]
      ,[weight_ts]
      ,[shift]
      ,[actual_weight]
      ,[recommend_1_roller_gap]
      ,[recommend_2_roller_gap]
      ,[recommend_3_roller_gap]
      ,[recommend_forming_roller_gap]
      ,[recommend_extruder_temperature_up]
      ,[recommend_cross_cutter_speed]
      ,[predicted_weight]
      ,[operator_reason]
      ,[create_by]
      ,[create_time]
      ,[update_time]
  FROM [test-portaldb].[dbo].[yng_recommend_weight_data] --test 238/dev 237
  WHERE 
      [data_time] > '2024-10-16 00:00:00' --AND [data_time] < '2024-09-26 00:00:00'
  order by [data_time] ASC

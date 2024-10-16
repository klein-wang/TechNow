SELECT TOP (1000) [id]
      ,[is_change]
      ,[sku]
      ,[extruder_temperature]
      ,[slice_product_line_speed]
      ,[n1_roller_gap]
      ,[n2_roller_gap]
      ,[n3_roller_gap]
      ,[forming_roller_gap]
      ,[extruder_temperature_up]
      ,[cross_cutter_speed]
      ,[target_weight]
      ,[data_time]
      ,[weight_ts]
      ,[shift]
      ,[actual_weight]
      ,[ai_res_actual_weight]
	  ,[predicted_weight_before_change]
      ,[predicted_weight_after_change]
      ,[recommend_1_roller_gap]
      ,[recommend_2_roller_gap]
      ,[recommend_3_roller_gap]
      ,[recommend_forming_roller_gap]
      ,[recommend_extruder_temperature_up]
      ,[recommend_cross_cutter_speed]
      ,[recommend_weight_data_id]
      ,[create_by]
      ,[update_by]
      ,[create_time]
      ,[update_time]
  FROM [dev-portaldb].[dbo].[yng_recommend_weight_data_log]
  WHERE [is_change] = '1'
  ORDER BY [data_time] DESC

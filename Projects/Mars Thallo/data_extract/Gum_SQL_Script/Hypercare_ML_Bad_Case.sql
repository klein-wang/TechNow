SELECT [id]
      ,[is_change]
      ,[sku]
      ,[data_time]
      ,[weight_ts]
      ,[actual_weight]
      ,[shift]
	  ,[update_by]
      ,[operator_status]
      ,[extruder_temperature]
      ,[extruder_exit_gum_temp]
      ,[n1_roller_gap]
      ,[n2_roller_gap]
      ,[n3_roller_gap]
      ,[forming_roller_gap]
      ,[extruder_temperature_up_sv]
      ,[cross_cutter_speed_sv]
      ,CASE WHEN [sr_recommend_1_roller_gap] <> [n1_roller_gap] THEN [sr_recommend_1_roller_gap] ELSE NULL END AS diff_n1_roller_gap
	  ,CASE WHEN [sr_recommend_2_roller_gap] <> [n2_roller_gap] THEN [sr_recommend_2_roller_gap] ELSE NULL END AS diff_n2_roller_gap
	  ,CASE WHEN [sr_recommend_3_roller_gap] <> [n3_roller_gap] THEN [sr_recommend_3_roller_gap] ELSE NULL END AS diff_n3_roller_gap
	  ,CASE WHEN [sr_recommend_forming_roller_gap] <> [forming_roller_gap] THEN [sr_recommend_forming_roller_gap] ELSE NULL END AS diff_forming_roller_gap
	  ,CASE WHEN [sr_recommend_extruder_temperature_up] <> [extruder_temperature_up_sv] THEN [sr_recommend_extruder_temperature_up] ELSE NULL END AS diff_extruder_temperature_up
	  ,CASE WHEN [sr_recommend_cross_cutter_speed] <> [cross_cutter_speed_sv] THEN [sr_recommend_cross_cutter_speed] ELSE NULL END AS diff_cross_cutter_speed
	  ,'' AS reason
	  ,'' AS bad_case
/*
      ,[sr_recommend_1_roller_gap]
      ,[sr_recommend_2_roller_gap]
      ,[sr_recommend_3_roller_gap]
      ,[sr_recommend_forming_roller_gap]
      ,[sr_recommend_extruder_temperature_up]
      ,[sr_recommend_cross_cutter_speed]
      ,[diff_recommend_1_roller_gap]
      ,[diff_recommend_2_roller_gap]
      ,[diff_recommend_3_roller_gap]
      ,[diff_recommend_forming_roller_gap]
      ,[diff_recommend_extruder_temperature_up]
      ,[diff_recommend_cross_cutter_speed]
*/
      ,[predicted_weight]
      ,[write_back_status]
      ,[recommend_weight_data_id]
      ,[update_time]
  FROM [test-portaldb].[dbo].[yng_recommend_weight_data_log]
  WHERE 
      [data_time] > '2024-11-04 16:00:00' --AND [data_time] < '2024-09-26 00:00:00'
	  AND [update_by] <> 'SYSTEM'
	  AND [operator_status] = '3'
	  --AND [operator_status] = '0'
  ORDER by [data_time] ASC

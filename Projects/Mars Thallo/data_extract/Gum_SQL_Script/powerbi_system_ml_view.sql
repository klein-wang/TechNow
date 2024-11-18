
With record as (
	SELECT [id]
		  ,[sku]
		  ,[shift]
		  ,[data_time]
		  ,[actual_weight]
		  ,CASE WHEN [actual_weight] > 35.36 THEN 'over' WHEN [actual_weight] < 35.1 THEN 'less' ELSE 'normal' END AS weight_condition
		  ,[predicted_weight] - [actual_weight] AS predicted_change
		  ,[weight_ts]
		  ,CASE operator_status 
				WHEN '0' THEN 'none'
				WHEN '1' THEN 'accept'
				WHEN '2' THEN 'p_accept'
				WHEN '3' THEN 'reject'
		   END AS operator_status
		  ,CONCAT_WS(', ', 
					CASE WHEN recommend_1_roller_gap <> n1_roller_gap 
						  OR recommend_2_roller_gap <> n2_roller_gap
						  OR recommend_3_roller_gap <> n3_roller_gap
						  OR recommend_forming_roller_gap <> forming_roller_gap
						  THEN 'Gap' ELSE NULL END,
					CASE WHEN recommend_extruder_temperature_up <> extruder_temperature_up_sv THEN 'Temp' ELSE NULL END,
					CASE WHEN recommend_cross_cutter_speed <> cross_cutter_speed_sv THEN 'CS' ELSE NULL END
		   ) AS changes
		  ,CASE WHEN recommend_1_roller_gap <> n1_roller_gap THEN recommend_1_roller_gap ELSE NULL END AS diff_n1_roller_gap
		  ,CASE WHEN recommend_2_roller_gap <> n2_roller_gap THEN recommend_2_roller_gap ELSE NULL END AS diff_n2_roller_gap
		  ,CASE WHEN recommend_3_roller_gap <> n3_roller_gap THEN recommend_3_roller_gap ELSE NULL END AS diff_n3_roller_gap
		  ,CASE WHEN recommend_forming_roller_gap <> forming_roller_gap THEN recommend_forming_roller_gap ELSE NULL END AS diff_forming_roller_gap
		  ,CASE WHEN recommend_extruder_temperature_up <> extruder_temperature_up_sv THEN recommend_extruder_temperature_up ELSE NULL END AS diff_extruder_temperature_up
		  ,CASE WHEN recommend_cross_cutter_speed <> cross_cutter_speed_sv THEN recommend_cross_cutter_speed ELSE NULL END AS diff_cross_cutter_speed
		  ,[n1_roller_gap]
		  ,[n2_roller_gap]
		  ,[n3_roller_gap]
		  ,[forming_roller_gap]
		  ,[extruder_temperature_up_sv]
		  ,[cross_cutter_speed_sv]
		  ,[operator_reason]
	  FROM [test-portaldb].[dbo].[yng_recommend_weight_data]
	  WHERE [data_time] > '2024-11-12 14:00:00'  --AND [data_time] < '2024-11-11 00:00:00' 
)

SELECT a.*
    ,spc.[FUser] AS Operator
FROM record a
LEFT JOIN [spc-datadb].[dbo].[TReceive] spc ON a.weight_ts = spc.FDate
WHERE operator_status LIKE '%none'  -- none 未操作，accept 接受, p_accept 部分接受, reject 拒绝
ORDER BY id

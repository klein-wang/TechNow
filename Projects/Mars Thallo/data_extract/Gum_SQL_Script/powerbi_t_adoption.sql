WITH PreprocessedData AS (
    SELECT 
        [id]
        ,[sku]
        ,[shift]
        ,[data_time]
        ,CAST([data_time] AS DATE) AS date
        ,[weight_ts]
        ,[actual_weight]
        ,[predicted_weight] - [actual_weight] as predicted_change
        ,[operator_status]
        ,[write_back_status]
        ,[recommend_weight_data_id]
        ,[update_by]
        ,[update_time]
        ,[extruder_exit_gum_temp]
        ,[n1_roller_gap]
        ,[n2_roller_gap]
        ,[n3_roller_gap]
        ,[forming_roller_gap]
        ,[extruder_temperature_up_sv]
        ,[cross_cutter_speed_sv]
        ,[sr_recommend_1_roller_gap]
        ,[sr_recommend_2_roller_gap]
        ,[sr_recommend_3_roller_gap]
        ,[sr_recommend_forming_roller_gap]
        ,[sr_recommend_extruder_temperature_up]
        ,[sr_recommend_cross_cutter_speed]
        ,CAST(FLOOR(CAST([sr_recommend_extruder_temperature_up] AS FLOAT)) AS INT) AS rounded_sr_recommend_extruder_temperature_up
        ,LEAD([sr_recommend_1_roller_gap]) OVER (PARTITION BY [sku] ORDER BY [data_time]) AS next_sr_recommend_1_roller_gap
        ,LEAD([sr_recommend_2_roller_gap]) OVER (PARTITION BY [sku] ORDER BY [data_time]) AS next_sr_recommend_2_roller_gap
        ,LEAD([sr_recommend_3_roller_gap]) OVER (PARTITION BY [sku] ORDER BY [data_time]) AS next_sr_recommend_3_roller_gap
        ,LEAD([sr_recommend_forming_roller_gap]) OVER (PARTITION BY [sku] ORDER BY [data_time]) AS next_sr_recommend_forming_roller_gap
        ,LEAD(CAST(FLOOR(CAST([sr_recommend_extruder_temperature_up] AS FLOAT)) AS INT)) OVER (PARTITION BY [sku] ORDER BY [data_time]) AS next_sr_recommend_extruder_temperature_up
        ,LEAD([sr_recommend_cross_cutter_speed]) OVER (PARTITION BY [sku] ORDER BY [data_time]) AS next_sr_recommend_cross_cutter_speed
    FROM [test-portaldb].[dbo].[yng_recommend_weight_data_log]
    WHERE [is_change] = '1'
	AND [data_time] > '2024-11-04 08:00:00'  --AND [data_time] < '2024-11-06 11:52:00' 
),

ComparisonData_new AS (
    SELECT 
        *,
        CASE 
            WHEN 
                [sr_recommend_1_roller_gap] = next_sr_recommend_1_roller_gap
                AND [sr_recommend_2_roller_gap] = next_sr_recommend_2_roller_gap
                AND [sr_recommend_3_roller_gap] = next_sr_recommend_3_roller_gap
                AND [sr_recommend_forming_roller_gap] = next_sr_recommend_forming_roller_gap
                AND rounded_sr_recommend_extruder_temperature_up = next_sr_recommend_extruder_temperature_up
                AND [sr_recommend_cross_cutter_speed] = next_sr_recommend_cross_cutter_speed
            THEN 0 ELSE 1
        END AS recommend_group_idx
    FROM PreprocessedData
),

ComparisonData AS (
    SELECT 
        *,
        DENSE_RANK() OVER (
            ORDER BY 
                [sku],
				[date],
				[sr_recommend_1_roller_gap],
                [sr_recommend_2_roller_gap],
                [sr_recommend_3_roller_gap],
                [sr_recommend_forming_roller_gap],
                rounded_sr_recommend_extruder_temperature_up,
                [sr_recommend_cross_cutter_speed]
        ) AS recommend_group_id
    FROM PreprocessedData
),

MaxStatusData AS (
    SELECT 
        recommend_group_id,
		MAX(id) AS id,
        MAX(operator_status) AS operator_status
    FROM ComparisonData
    GROUP BY recommend_group_id
),

Combine AS (
	SELECT
		m.id AS id,
		c.sku,
		c.shift,
		c.data_time,
		c.actual_weight,
		CASE WHEN c.actual_weight > 35.36 THEN 'over' WHEN c.actual_weight < 35.1 THEN 'less' ELSE 'normal' END AS weight_condition,
		c.predicted_change,
		c.weight_ts,
		CASE m.operator_status 
			WHEN '0' THEN 'none'
			WHEN '1' THEN 'accept'
			WHEN '2' THEN 'p_accept'
			WHEN '3' THEN 'reject'
		END AS operator_status,
		--c.recommend_weight_data_id,
		--c.update_by,
		--c.update_time,
		CONCAT_WS(', ', 
				CASE WHEN c.sr_recommend_1_roller_gap <> c.n1_roller_gap 
					  OR c.sr_recommend_2_roller_gap <> c.n2_roller_gap
					  OR c.sr_recommend_3_roller_gap <> c.n3_roller_gap
					  OR c.sr_recommend_forming_roller_gap <> c.forming_roller_gap
					  THEN 'Gap' ELSE NULL END,
				CASE WHEN c.sr_recommend_extruder_temperature_up <> c.extruder_temperature_up_sv THEN 'Temp' ELSE NULL END,
				CASE WHEN c.sr_recommend_cross_cutter_speed <> c.cross_cutter_speed_sv THEN 'CS' ELSE NULL END
			) AS changes,
		CASE WHEN c.sr_recommend_1_roller_gap <> c.n1_roller_gap THEN c.sr_recommend_1_roller_gap ELSE NULL END AS diff_n1_roller_gap,
		CASE WHEN c.sr_recommend_2_roller_gap <> c.n2_roller_gap THEN c.sr_recommend_2_roller_gap ELSE NULL END AS diff_n2_roller_gap,
		CASE WHEN c.sr_recommend_3_roller_gap <> c.n3_roller_gap THEN c.sr_recommend_3_roller_gap ELSE NULL END AS diff_n3_roller_gap,
		CASE WHEN c.sr_recommend_forming_roller_gap <> c.forming_roller_gap THEN c.sr_recommend_forming_roller_gap ELSE NULL END AS diff_forming_roller_gap,
		CASE WHEN c.sr_recommend_extruder_temperature_up <> c.extruder_temperature_up_sv THEN c.sr_recommend_extruder_temperature_up ELSE NULL END AS diff_extruder_temperature_up,
		CASE WHEN c.sr_recommend_cross_cutter_speed <> c.cross_cutter_speed_sv THEN c.sr_recommend_cross_cutter_speed ELSE NULL END AS diff_cross_cutter_speed,
		/*
		c.sr_recommend_1_roller_gap,
		c.sr_recommend_2_roller_gap,
		c.sr_recommend_3_roller_gap,
		c.sr_recommend_forming_roller_gap,
		c.sr_recommend_extruder_temperature_up,
		c.sr_recommend_cross_cutter_speed,
		*/
		c.n1_roller_gap,
		c.n2_roller_gap,
		c.n3_roller_gap,
		c.forming_roller_gap,
		c.extruder_temperature_up_sv,
		c.cross_cutter_speed_sv,
		--c.extruder_exit_gum_temp,
		--c.write_back_status,
		'' AS reason
	FROM MaxStatusData m
	INNER JOIN ComparisonData c ON m.id = c.id
),

Combine_new AS (
	SELECT
		c.id AS id,
		c.sku,
		c.shift,
		c.data_time,
		c.actual_weight,
		CASE WHEN c.actual_weight > 35.36 THEN 'over' WHEN c.actual_weight < 35.1 THEN 'less' ELSE 'normal' END AS weight_condition,
		c.predicted_change,
		c.weight_ts,
		CASE c.operator_status 
			WHEN '0' THEN 'none'
			WHEN '1' THEN 'accept'
			WHEN '2' THEN 'p_accept'
			WHEN '3' THEN 'reject'
		END AS operator_status,
		--c.recommend_weight_data_id,
		--c.update_by,
		--c.update_time,
		CONCAT_WS(', ', 
				CASE WHEN c.sr_recommend_1_roller_gap <> c.n1_roller_gap 
					  OR c.sr_recommend_2_roller_gap <> c.n2_roller_gap
					  OR c.sr_recommend_3_roller_gap <> c.n3_roller_gap
					  OR c.sr_recommend_forming_roller_gap <> c.forming_roller_gap
					  THEN 'Gap' ELSE NULL END,
				CASE WHEN c.sr_recommend_extruder_temperature_up <> c.extruder_temperature_up_sv THEN 'Temp' ELSE NULL END,
				CASE WHEN c.sr_recommend_cross_cutter_speed <> c.cross_cutter_speed_sv THEN 'CS' ELSE NULL END
			) AS changes,
		CASE WHEN c.sr_recommend_1_roller_gap <> c.n1_roller_gap THEN c.sr_recommend_1_roller_gap ELSE NULL END AS diff_n1_roller_gap,
		CASE WHEN c.sr_recommend_2_roller_gap <> c.n2_roller_gap THEN c.sr_recommend_2_roller_gap ELSE NULL END AS diff_n2_roller_gap,
		CASE WHEN c.sr_recommend_3_roller_gap <> c.n3_roller_gap THEN c.sr_recommend_3_roller_gap ELSE NULL END AS diff_n3_roller_gap,
		CASE WHEN c.sr_recommend_forming_roller_gap <> c.forming_roller_gap THEN c.sr_recommend_forming_roller_gap ELSE NULL END AS diff_forming_roller_gap,
		CASE WHEN c.sr_recommend_extruder_temperature_up <> c.extruder_temperature_up_sv THEN c.sr_recommend_extruder_temperature_up ELSE NULL END AS diff_extruder_temperature_up,
		CASE WHEN c.sr_recommend_cross_cutter_speed <> c.cross_cutter_speed_sv THEN c.sr_recommend_cross_cutter_speed ELSE NULL END AS diff_cross_cutter_speed,
		/*
		c.sr_recommend_1_roller_gap,
		c.sr_recommend_2_roller_gap,
		c.sr_recommend_3_roller_gap,
		c.sr_recommend_forming_roller_gap,
		c.sr_recommend_extruder_temperature_up,
		c.sr_recommend_cross_cutter_speed,
		*/
		c.n1_roller_gap,
		c.n2_roller_gap,
		c.n3_roller_gap,
		c.forming_roller_gap,
		c.extruder_temperature_up_sv,
		c.cross_cutter_speed_sv,
		--c.extruder_exit_gum_temp,
		--c.write_back_status,
		'' AS reason
	FROM ComparisonData_new c
	WHERE c.recommend_group_idx = '1'
)

/*
SELECT a.*
       ,spc.[FUser] AS Operator
FROM Combine a
--FROM Combine_new a
LEFT JOIN [spc-datadb].[dbo].[TReceive] spc ON a.weight_ts = spc.FDate
WHERE operator_status IN ('none')  -- none 未操作，accept 接受, p_accept 部分接受, reject 拒绝
ORDER BY id
*/

SELECT 
	'' AS metric_id,
	CAST([data_time] AS DATE) AS datetime,
	COUNT(CASE WHEN operator_status IN ('accept', 'p_accept') THEN 1 END) AS actual,
	COUNT(operator_status) AS count,
	'' AS batch_id,
	shift
FROM Combine
GROUP BY CAST([data_time] AS DATE),shift
ORDER BY CAST([data_time] AS DATE),shift
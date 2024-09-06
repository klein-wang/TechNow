WITH SortedDifferences AS (
    SELECT TOP 5000000
        Tag,
        TS,
        LAG(Value) OVER (PARTITION BY Tag ORDER BY TS) AS PrevValue,
		LAG(Tag) OVER (PARTITION BY Tag ORDER BY TS) AS PrevTag,
		Value
    FROM
        [opc_timedata].[dbo].[yng_ts_opc_data_log]
    WHERE
        [Tag] IN (
			'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1OutletTemp',
			'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2OutletTemp',
			'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_3rdSizing.rActualVelocityRPM',
			'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_2ndSizing.rSetpoint_Ratio'
        )
        AND 
			[TS] >= '2024-08-22 00:00:00.000'
	ORDER BY
		--Tag,
		TS DESC
)

-- Now, filter the rows where the absolute difference is greater than 1% of the previous row's 'Value'
-- or where the 'Tag' has changed (first occurrence of a new 'Tag').
-- Additionally, filter for specific tags.

SELECT
    Tag,
    TS,
    Value
FROM
    SortedDifferences
WHERE
    Value <> PrevValue
	OR PrevTag <> Tag
;
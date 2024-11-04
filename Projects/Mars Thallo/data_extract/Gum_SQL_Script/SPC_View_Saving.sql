With spc AS (
	SELECT a.[ID]
		  ,a.[FDate] AS Date
		  ,CONVERT(DATE, a.[FDate]) AS Day
		  ,a.[FItemCode] AS Item_code
		  ,b.fItemName AS Item
		  ,a.[FHoudu] AS length_or_thickness
		  ,a.[FShendu] AS width_or_depth
		  ,a.[FUser] AS Operator
		  ,a.[FbanCode] AS Shift
		  ,a.[FHStd] AS length_or_thickness_std
		  ,a.[FSStd] AS width_or_depth_std
		  ,a.[FStatus] AS Status
		  ,a.[FLoad] AS Load
		  ,a.[FXJType] AS entry_type
		  ,a.[FZStd] AS Target
		  ,a.[FZhong] AS Actual
	  FROM [spc-datadb].[dbo].[TReceive] a
	  LEFT JOIN [spc-datadb].[dbo].[TItem] b
	  ON a.FItemCode = b.fItemCode
	  WHERE 
		  FDate > '2024-01-01 00:00:00' --AND FDate < '2024-09-26 00:00:00'
		  AND [FXJType] = '3' --weight
		  --AND [FXJType] = '2' --length
),

spc_by_day_shift AS (
	SELECT 
		  Day,
		  Shift,
		  REPLACE(LEFT(Item,4), '（', '') AS SKU,
		  MAX(Load) AS Load,
		  MAX(Load) * 133 AS Amount_in_kg,
		  CASE
			WHEN AVG(Actual) > 50 THEN AVG(Actual) / 2
			ELSE AVG(Actual)
		  END AS Actual
	  FROM spc
	  GROUP BY Day, Shift, Item
),

spc_by_sku AS (
    SELECT 
        Day,
        Shift,
        SKU,
		CASE 
		  WHEN LEFT(SKU,1) IN ('D','W','R') THEN 'Sugar' 
		  ELSE 'Sugarfree' 
		END AS Type,
        Load,
        Amount_in_kg,
        Actual,
		LEAD(SKU) OVER (ORDER BY Day DESC, Shift, SKU) AS Next_SKU
    FROM spc_by_day_shift
),

spc_value AS (
	SELECT 
		Day,
		Shift,
		SKU,
		Type,
		Amount_in_kg,
		ROUND(Actual/13, 3) AS Actual_Per_Slice,
		(2.73 - Actual/13) * Amount_in_kg/1000 * 19 AS Saving_rmb_k  --19 = unit price
	FROM spc_by_sku
	WHERE Next_SKU <> SKU
)

SELECT Type,
       SKU,
	   ROUND(SUM(Amount_in_kg)/1000,1) AS Total_Amount_in_t,
       ROUND(SUM(Saving_rmb_k)/7.28,2) AS Saving_usd_k
FROM spc_value
GROUP BY Type, SKU
HAVING SUM(Amount_in_kg)/1000 > 100
ORDER BY Type, Total_Amount_in_t DESC
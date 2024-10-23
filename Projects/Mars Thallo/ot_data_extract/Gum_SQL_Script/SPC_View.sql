SELECT a.[ID]
      ,a.[FDate] AS Date
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
  ORDER BY FDate ASC
// Load nodes with dynamic labels
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
WITH row, 
     CASE row.type 
         WHEN 'Product' THEN 'Product'
         WHEN 'sku' THEN 'Sku'
         WHEN 'Color' THEN 'Color'
         WHEN 'Environment' THEN 'Environment'
         WHEN 'CoatingProcess' THEN 'CoatingProcess'
         WHEN 'ProcessType' THEN 'ProcessType'
         WHEN 'CoatingPhase' THEN 'CoatingPhase'
         WHEN 'CoatingStep' THEN 'CoatingStep'
         WHEN 'CoatingCycle' THEN 'CoatingCycle'
         WHEN 'Measurement' THEN 'Measurement'
         WHEN 'ProcessParameter' THEN 'ProcessParameter'
         WHEN 'InputMaterial' THEN 'InputMaterial'
         WHEN 'Machine' THEN 'Machine'
         WHEN 'Man' THEN 'Man'
         WHEN 'Quality' THEN 'Quality'
     END AS label
CALL apoc.create.node([label], {id: row.id, name: row.name}) YIELD node
RETURN node


// Load relationships with conditional logic
LOAD CSV WITH HEADERS FROM 'file:///relationship_type.csv' AS row
WITH row,
     CASE row.from_type 
         WHEN 'Product' THEN 'Product'
         WHEN 'sku' THEN 'Sku'
         WHEN 'Color' THEN 'Color'
         WHEN 'Environment' THEN 'Environment'
         WHEN 'CoatingProcess' THEN 'CoatingProcess'
         WHEN 'ProcessType' THEN 'ProcessType'
         WHEN 'CoatingPhase' THEN 'CoatingPhase'
         WHEN 'CoatingStep' THEN 'CoatingStep'
         WHEN 'CoatingCycle' THEN 'CoatingCycle'
         WHEN 'Measurement' THEN 'Measurement'
         WHEN 'ProcessParameter' THEN 'ProcessParameter'
         WHEN 'InputMaterial' THEN 'InputMaterial'
         WHEN 'Machine' THEN 'Machine'
         WHEN 'Man' THEN 'Man'
     END AS fromLabel,
     CASE row.to_type 
         WHEN 'Product' THEN 'Product'
         WHEN 'sku' THEN 'Sku'
         WHEN 'Color' THEN 'Color'
         WHEN 'Environment' THEN 'Environment'
         WHEN 'CoatingProcess' THEN 'CoatingProcess'
         WHEN 'ProcessType' THEN 'ProcessType'
         WHEN 'CoatingPhase' THEN 'CoatingPhase'
         WHEN 'CoatingStep' THEN 'CoatingStep'
         WHEN 'CoatingCycle' THEN 'CoatingCycle'
         WHEN 'Measurement' THEN 'Measurement'
         WHEN 'ProcessParameter' THEN 'ProcessParameter'
         WHEN 'InputMaterial' THEN 'InputMaterial'
         WHEN 'Machine' THEN 'Machine'
         WHEN 'Man' THEN 'Man'
         WHEN 'Quality' THEN 'Quality'
     END AS toLabel,
     row.relationship AS relationshipType
MATCH (a {id: row.from_id})
SET a:fromLabel
WITH a, row, toLabel, relationshipType
MATCH (b {id: row.to_id})
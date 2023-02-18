$postParams = @{""="";""=""} | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/api/fridge -ContentType "application/json" -Method POST -Body $postParams
# Object format: '[{"": "", ...}, {"": ""...}]'

$postParams = @{"action"="add";"foods"='[{"name": "apples", "quantity": "5"}, {"name": "oranges", "quantity": "5"}]'} | ConvertTo-Json
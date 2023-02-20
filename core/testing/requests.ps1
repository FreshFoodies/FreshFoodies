$postParams = @{""="";""=""} | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/api/fridge -ContentType "application/json" -Method POST -Body $postParams
# Object format: '[{"": "", ...}, {"": ""...}]'

$postParams = @{"action"="add";"foods"='[{"category":"vegetables","date_added":"2023-02-10T08:00:00","expiration_date":"2023-02-17T08:00:00","location":"outside","name":"onions","price":2.99,"quantity":3,"slug":"onions"}, {"category":"meat","date_added":"2023-02-10T08:00:00","expiration_date":"2023-02-17T08:00:00","location":"freezer","name":"steak","price":10.99,"quantity":1,"slug":"steak"}]'} | ConvertTo-Json
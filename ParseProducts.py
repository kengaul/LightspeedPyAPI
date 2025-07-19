import json

with open("product.json") as file:
     products = json.load(file)   

# products['data'][0]['product_suppliers'][0]
#
for i in products['data']:
    if i['has_variants'] == True:
        print(i['sku'])
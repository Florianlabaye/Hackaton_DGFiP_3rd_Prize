

import requests

headers = {
    'X-API-Key': '8ea4fb692e655c4eb93f9f77511bc62b064e2ca593036787a853b28257e32d18',
    'Accept': 'application/json',
}

get_address = "0xffec0067f5a79cff07527f63d83dd5462ccf8ba4"

response = requests.get('https://public.chainalysis.com/api/v1/address/'+get_address, headers=headers)

response.status_code
resultat = response.json()

problem = len(resultat.get("identifications"))

if problem == 0:
    print("Chain analysis ne détecte pas de risque sur cette adresse" )
else:
    print("Chain analysis détecte un risque sur cette adresse")

import json

p = r"C:\Users\moode\OneDrive\ABISALUD\RESPALDOS MACRO\CRM_Macrocedis_Backup_2026-10-23 0426.json"
with open(p, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Top keys in JSON:", list(data.keys()))
for k, v in data.items():
    if isinstance(v, list):
        print(f"Key '{k}': {len(v)} items")
        if v and isinstance(v[0], dict):
            print(f"  Item sample keys: {list(v[0].keys())}")
            # check if procedimiento or contrato is in item
            for sample in v[:5]:
                for prop in sample:
                    if any(t in prop.lower() for t in ['proc', 'contrat', 'licit']):
                        print(f"    found {prop}: {sample[prop]}")

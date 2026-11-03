p = r"C:\Users\moode\OneDrive\ABISALUD\RESPALDOS MACRO\CRM_Macrocedis_Backup_2026-10-23 0426.sql"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    for _ in range(50):
        line = f.readline()
        if not line:
            break
        print(line.strip())

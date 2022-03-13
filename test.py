import json 

with open("all_ts.json") as f:
    watch = json.load(f)

print(len(watch))

with open("check_pg_250.json") as f:
    watch = json.load(f)
print(len(watch))


import json
data_path = '/Users/kalebmesfin06/Desktop/KAI/GUI-AI-project/global_result.json'
with open(data_path) as f:
    data = json.load(f)

print(eval(data).keys())
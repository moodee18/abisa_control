import json

transcript_path = r'C:\Users\moode\.gemini\antigravity-ide\brain\0fb4f23e-f29b-4a99-a180-726f321f9115\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        content = str(data.get('content', ''))
        # Look for SQL queries or data insertions mentioning procedimiento or contrato
        if 'procedimiento' in content.lower() and ('insert' in content.lower() or 'update' in content.lower() or 'create table' in content.lower() or 'contrato' in content.lower()):
            for sub in content.split('\n'):
                if any(x in sub.lower() for x in ['contrato', 'procedimiento', 'ia-', 'cs/']):
                    print(f"Step {data.get('step_index')}: {sub[:140]}")

import json

transcript_path = r'C:\Users\moode\.gemini\antigravity-ide\brain\0fb4f23e-f29b-4a99-a180-726f321f9115\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        content = str(data.get('content', ''))
        if 'procedimiento' in content.lower() or 'contrato' in content.lower():
            if data.get('type') in ['USER_INPUT', 'PLANNER_RESPONSE']:
                print(f"--- Type: {data.get('type')} | Step: {data.get('step_index')} ---")
                for sub in content.split('\n'):
                    if any(w in sub.lower() for w in ['procedimiento', 'contrato', 'os-adbmx', 'ia-12-nef', 'folio / adm']):
                        print('  ', sub[:160])

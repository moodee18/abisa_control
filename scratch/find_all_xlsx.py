import glob

files = glob.glob('**/*.xlsx', recursive=True)
for f in files:
    print(f)


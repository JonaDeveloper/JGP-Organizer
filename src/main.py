from pathlib import Path

p = Path('.')

for x in p.iterdir():
  if x.is_file:
    print(x, x.suffix)


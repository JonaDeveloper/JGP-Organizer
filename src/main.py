from pathlib import Path
import config, rules, organizer


p = Path('.')

f = 0
for f in p.iterdir():
  if f.is_file():
    print(rules.detection(f))
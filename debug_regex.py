import re

text = 'open notepads and type"hello world this is me " and save it'
lower = text.lower()

# Flexible matching: optional space after type
pattern = r"open (.+) and type\s*[\"']?(.+?)[\"']? and save it"
match = re.search(pattern, lower)

print(f"Text: {lower}")
print(f"Pattern: {pattern}")
if match:
    print("MATCHED!")
    print(f"Group 1 (App): '{match.group(1)}'")
    print(f"Group 2 (Text): '{match.group(2)}'")
else:
    print("NO MATCH")

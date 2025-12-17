import sys
import platform
import packaging.tags

print(f"Python: {sys.version}")
print(f"Platform: {platform.system()} {platform.machine()}")

print("\nSupported Tags:")
count = 0
for tag in packaging.tags.sys_tags():
    print(tag)

    count += 1
    if count > 10:
        break

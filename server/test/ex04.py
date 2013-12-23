import re

"""
subject="foobarbaz"
print re.sub("(fo+)bar(?=baz)", "\\1quux", subject)
print subject
"""

subject="ummmdjaksh\n</div>\n</body>"
snippet="<!--snippet-->"

print subject
print re.sub("(<\/body>)",snippet+"\\1",subject)

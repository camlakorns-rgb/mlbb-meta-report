import sys
src = open('template.html', encoding='utf-8').read()
i = src.find('<script>'); j = src.find('</script>', i)
assert i > 0 and j > i
body = src[i+8:j]
# strip engine IIFE wrapper so tests can reach engine vars
o = body.find('(function(){')
assert o > 0, 'IIFE opener not found'
body = body[o+len('(function(){'):]
body = body.rstrip()
assert body.endswith('})();'), 'IIFE closer not at end'
body = body[:-5]
open('/tmp/body.js', 'w', encoding='utf-8').write(body)
print('body.js bytes:', len(body))

from .gcp import GreatestCommonPrefix


gcp = GreatestCommonPrefix()

assert 'pine' == gcp.parse(['pineapple', 'pine tree'])
assert '' == gcp.parse([' pineapple', 'pine tree'])
assert '    chick' == gcp.parse(['    chicken', '    chickpea'])
assert 'dog' == gcp.parse(['dog', 'dog'])
assert 'stack' == gcp.parse(['stack', 'stacked'])
assert 'stack' == gcp.parse(['stacked', 'stack'])
assert 'single' == gcp.parse(['single'])
assert 'sin' == gcp.parse(['single', 'singleton', 'singing', 'singed', 'sine'])

gcp = GreatestCommonPrefix(whitelist=' \t\r\n')
assert '    	' == gcp.parse(['    	pineapple', '    	pine tree'])

gcp = GreatestCommonPrefix(whitelist='pla')
assert 'appl' == gcp.parse(['appliance', 'applicable'])
assert '' == gcp.parse(['dog', 'dog'])

gcp = GreatestCommonPrefix(regex=r"[ \t]*'+[ \t]*")
assert "'" == gcp.parse(["'' test", "' test"])
assert '' == gcp.parse([' pineapple', 'pine tree'])
assert '' == gcp.parse(['    chicken', '    chickpea'])
assert "    '" == gcp.parse(["    'chicken", "    'chickpea"])
assert "    '	" == gcp.parse(["    '	chicken", "    '	chickpea"])
assert '' == gcp.parse(['dog', 'dog'])
assert "'" == gcp.parse(["'stack'", "'stacked'"])

from simpletest import Test
from CommentReflow import ReflowComment, GreatestCommonPrefix
import os

class GreatestCommonPrefixTest(Test):
	context_lines_before = 0
	context_lines_after = 0

	def run(self):
		gcp = GreatestCommonPrefix()

		self.assert_eq(gcp.parse(['pineapple', 'pine tree']), 'pine')
		self.assert_eq(gcp.parse([' pineapple', 'pine tree']), '')
		self.assert_eq(gcp.parse(['    chicken', '    chickpea']), '    chick')
		self.assert_eq(gcp.parse(['dog', 'dog']), 'dog')
		self.assert_eq(gcp.parse(['stack', 'stacked']), 'stack')
		self.assert_eq(gcp.parse(['stacked', 'stack']), 'stack')
		self.assert_eq(gcp.parse(['single']), 'single')
		self.assert_eq(gcp.parse(['single', 'singleton', 'singing', 'singed', 'sine']), 'sin')

		gcp = GreatestCommonPrefix(whitelist=' \t\r\n')
		self.assert_eq(gcp.parse(['    	pineapple', '    	pine tree']), '    	')

		gcp = GreatestCommonPrefix(whitelist='pla')
		self.assert_eq(gcp.parse(['appliance', 'applicable']), 'appl')
		self.assert_eq(gcp.parse(['dog', 'dog']), '')

		gcp = GreatestCommonPrefix(regex=r"[ \t]*'+[ \t]*")
		self.assert_eq(gcp.parse(["'' test", "' test"]), "'")
		self.assert_eq(gcp.parse([' pineapple', 'pine tree']), '')
		self.assert_eq(gcp.parse(['    chicken', '    chickpea']), '')
		self.assert_eq(gcp.parse(["    'chicken", "    'chickpea"]), "    '")
		self.assert_eq(gcp.parse(["    '	chicken", "    '	chickpea"]), "    '	")
		self.assert_eq(gcp.parse(['dog', 'dog']), '')
		self.assert_eq(gcp.parse(["'stack'", "'stacked'"]), "'")


class ReflowTest(Test):
	context_lines_before = 3
	context_lines_after = 2
	pretty_print = False
	write_failed_assert_to_file = True

	def run(self):
		rf = ReflowComment(marker='#',
                           max_width=80,
                           tab_size=4,
                           new_paragraph_regex=r'- ')

		self.assert_eq(rf.reflow(
			'# this is a short comment'
			),
			'# this is a short comment'
		)
		self.assert_eq(rf.reflow("""\
# This is just a single line that needs to be wrapped because it is too long even though it doesn't have any indention"""
			), """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""
		)
		self.assert_eq(rf.reflow("""\
# This is just a single line that needs to be wrapped because it is too long even though it
# doesn't have any indention"""
			), """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""
		)
		self.assert_eq(rf.reflow("""\
# This is just a single line that needs to be 
# wrapped because it is too long even though it
# doesn't have any indention"""
			), """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""
		)
		self.assert_eq(rf.reflow("""\
    # This is an indented comment. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
    # congue ligula ac quam viverra nec consectetur 
    # ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue."""
			), """\
    # This is an indented comment. Lorem ipsum dolor sit amet, consectetur
    # adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
    # congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et
    # mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue."""
		)
		self.assert_eq(rf.reflow("""\
	# This is an indented comment. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
	# congue ligula ac quam viverra nec consectetur 
	# ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
	# augue."""
			), """\
	# This is an indented comment. Lorem ipsum dolor sit amet, consectetur
	# adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
	# congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et
	# mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
	# augue."""
		)
		self.assert_eq(rf.reflow("""\
    # This is an indented comment with nested indention. Lorem ipsum dolor sit 
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. 
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. 
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue."""
			), """\
    # This is an indented comment with nested indention. Lorem ipsum dolor sit
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet
    #     ipsum mauris.
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante
    #     hendrerit.
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit
    # amet vitae augue."""
		)
		self.assert_eq(rf.reflow("""\
    # This is a comment with blank lines and nested indention. Lorem ipsum dolor sit 
    #  
    #
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. 
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. 
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue."""
			), """\
    # This is a comment with blank lines and nested indention. Lorem ipsum dolor
    # sit
    #
    #
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet
    #     ipsum mauris.
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante
    #     hendrerit.
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit
    # amet vitae augue."""
		)


		rf = ReflowComment(marker="'",
	                       max_width=40,
	                       tab_size=4,
	                       comment_start_regex=r'[ \t]*(?://|[/ ]\*)[ \t]*')

		self.assert_eq(rf.reflow("""\
    /* first line
     * second line that is considerably longer than the first because currently the first line, if wrapped, would naively use "/*" at the start.
     * third line
     */"""
			), """\
    /* first line
     * second line that is considerably
     * longer than the first because
     * currently the first line, if
     * wrapped, would naively use "/*"
     * at the start. third line
     */"""
		)


def run_tests():
	GreatestCommonPrefixTest()
	ReflowTest()

if __name__ == '__main__':
	run_tests()

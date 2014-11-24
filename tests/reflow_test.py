from textwrap import dedent
from src.reflow import ReflowComment


def indent(text, indention):
    return '\n'.join(indention + line for line in text.split('\n'))


class TestBasic:
    reflow_comment = ReflowComment(
        marker='#',
        max_width=80,
        tab_size=6,
        new_paragraph_regex=r'- ')
    reflow = reflow_comment.reflow

    def test_no_reflow_needed(self):
        desired = '# this is a short comment'
        actual = self.reflow(desired)
        assert actual == desired

    def test_single_unindented_line_wrap(self):
        actual = self.reflow("""\
# This is just a single line that needs to be wrapped because it is too long even though it doesn't have any indention""")
        desired = """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""

        actual = actual
        desired = desired
        assert actual == desired

    def test_two_incorrectly_wrapped_lines(self):
        actual = self.reflow("""\
# This is just a single line that needs to be wrapped because it is too long even though it
# doesn't have any indention""")
        desired = """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""

        actual = actual
        desired = desired
        assert actual == desired

    def test_three_incorrectly_wrapped_lines(self):
        actual = self.reflow("""\
# This is just a single line that needs to be
# wrapped because it is too long even though it
# doesn't have any indention""")
        desired = """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""

        actual = actual
        desired = desired
        assert actual == desired

    def test_indented_with_spaces(self):
        actual = self.reflow("""\
    # This is an indented comment. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
    # congue ligula ac quam viverra nec consectetur
    # ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue.""")
        desired = """\
    # This is an indented comment. Lorem ipsum dolor sit amet, consectetur
    # adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
    # congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et
    # mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue."""

        assert actual == desired

    def test_indented_with_tabs(self):
        actual = self.reflow("""\
      # This is an indented comment. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
      # congue ligula ac quam viverra nec consectetur
      # ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
      # augue.""")
        desired = """\
      # This is an indented comment. Lorem ipsum dolor sit amet, consectetur
      # adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris.
      # Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit.
      # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit
      # amet vitae augue."""

        # dedent and then indent so the strings will display with specific tab
        # width regardless of editor's tab width.
        actual = indent(dedent(actual), '\t')
        desired = indent(dedent(desired), '\t')
        assert actual == desired

    def test_list(self):
        actual = self.reflow("""\
    # This is an indented comment with nested indention. Lorem ipsum dolor sit
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris.
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit.
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue.""")
        desired = """\
    # This is an indented comment with nested indention. Lorem ipsum dolor sit
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet
    #     ipsum mauris.
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante
    #     hendrerit.
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit
    # amet vitae augue."""

        assert actual == desired

    def test_blank_lines_and_list(self):
        actual = self.reflow("""\
    # This is a comment with blank lines and nested indention. Lorem ipsum dolor sit
    #
    #
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris.
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit.
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae
    # augue.""")
        desired = """\
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
        print(actual)
        print(desired)
        assert actual == desired

class TestCustomSettings:
    rf = ReflowComment(
        max_width=40,
        tab_size=4,
        comment_start_regex=r'[ \t]*(?://|[/ ]\*)[ \t]*')
    reflow = rf.reflow

    def test_block_comment_indented(self):
        actual = self.reflow("""\
    /* first line
     * second line that is considerably longer than the first because currently the first line, if wrapped, would naively use "/*" at the start.
     * third line
     */""")
        desired = """\
    /* first line
     * second line that is considerably
     * longer than the first because
     * currently the first line, if
     * wrapped, would naively use "/*"
     * at the start. third line
     */"""

        actual = actual
        desired = desired
        assert actual == desired

    def test_c_like_comments(self):
        actual = self.reflow("""\
    // first line
    // second line that is considerably longer than the first because currently the first line, if wrapped, would naively use "/*" at the start.
    // third line""")
        desired = """\
    // first line second line that is
    // considerably longer than the
    // first because currently the first
    // line, if wrapped, would naively
    // use "/*" at the start. third line"""

        print(actual)
        print(desired)
        assert actual == desired
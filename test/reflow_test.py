from .reflow import ReflowComment


rf = ReflowComment(marker='#',
                   max_width=80,
                   tab_size=4,
                   new_paragraph_regex=r'- ')

assert '# this is a short comment' == rf.reflow('# this is a short comment')

actual = rf.reflow("""\
# This is just a single line that needs to be wrapped because it is too long even though it doesn't have any indention""")
desired = """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""
assert actual == desired

actual = rf.reflow("""\
# This is just a single line that needs to be wrapped because it is too long even though it
# doesn't have any indention""")
desired = """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""
assert actual == desired

actual = rf.reflow("""\
# This is just a single line that needs to be
# wrapped because it is too long even though it
# doesn't have any indention""")
desired = """\
# This is just a single line that needs to be wrapped because it is too long
# even though it doesn't have any indention"""
assert actual == desired

actual = rf.reflow("""\
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

actual = rf.reflow("""\
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

actual = rf.reflow("""\
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

actual = rf.reflow("""\
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
assert actual == desired


rf = ReflowComment(marker="'",
                   max_width=40,
                   tab_size=4,
                   comment_start_regex=r'[ \t]*(?://|[/ ]\*)[ \t]*')

actual = rf.reflow("""\
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
assert actual == desired

actual = rf.reflow("""\
    // first line
    // second line that is considerably longer than the first because currently the first line, if wrapped, would naively use "/*" at the start.
    // third line""")
desired = """\
    // first line second line that is
    // considerably longer than the
    // first because currently the first
    // line, if wrapped, would naively
    // use "/*" at the start. third line"""
assert actual == desired


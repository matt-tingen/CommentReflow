import textwrap
import re

class ReflowComment:
    marker = None
    max_width = 80
    tab_size = 4
    break_long_words = False
    break_on_hyphens = True
    comment_start_regex = None
    new_paragraph_regex = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if not self.marker and not self.comment_start_regex:
            raise ValueError("Must provide either 'marker' or 'comment_start_regex'")

    def indention_length(self, indention):
        return len(indention.replace('\t', ' ' * self.tab_size))

    # Returns a string starting after a given prefix
    def remove_prefix(self, line, prefix):
        if not line.startswith(prefix):
            raise ValueError
        else:
            return line[len(prefix):]

    def reflow(self, text):
        comment_start_regex = re.compile(self.comment_start_regex or
                                         r'[ \t]*{}+[ \t]*'.format(self.marker))
        new_paragraph_regex = None if self.new_paragraph_regex is None else re.compile(self.new_paragraph_regex)

        # It's easier to do this line by line than to dedent the whole comment
        # since we have to account for blank lines and comment_start_regex.
        #
        # A paragraph is a string to be wrapped. It is not indented and contains
        # no new lines. A new paragraph is started when a line matches one of
        # the following conditions:
        #     - It contains only whitespace
        #     - The "start" of the comment changes
        #         - The "start" is whatever is matched by comment_start_regex.
        #     - The rest of the line after the "start" is matched by
        #     self.new_paragraph_regex
        # Otherwise it's start is removed and it is concatanated to the end of
        # the previous paragraph.
        lines = re.split(r'\r?\n', text)
        paragraphs = []
        prev_start = None
        current_paragraph = ''

        # Add a blank string to the end of lists so the actual last item in
        # lines gets processed since we are processing the previous item in the
        # loop.
        for line in lines + ['']:

            all_whitespace = bool(re.match(r'^[ \t]*$', line))

            if all_whitespace:
                line_without_start = ''
            else:
                try:
                    start = comment_start_regex.match(line).group(0)
                except AttributeError:
                    raise ValueError('text contained a line that did not match the comment start regex')

                line_without_start = self.remove_prefix(line, start)

            all_whitespace = bool(re.match(r'^[ \t]*$', line_without_start))

            force_new_paragraph = new_paragraph_regex is not None and re.match(self.new_paragraph_regex, line_without_start)

            if all_whitespace or (start != prev_start) or force_new_paragraph:
                # New paragraph
                if prev_start is not None:
                    paragraphs.append((prev_start, current_paragraph))

                prev_start = start
                current_paragraph = line_without_start.rstrip()
            else:
                # Same paragraph
                current_paragraph += ' ' + line_without_start.rstrip()

        comment = ''

        for indent, paragraph in paragraphs:
            if comment:
                comment += '\n'

            # Handle re-indenting the lines manually because textwrap doesn't
            # allow for specifying tab width
            width = self.max_width - self.indention_length(indent)
            wrapped_lines =  textwrap.wrap(paragraph,
                                           width=width,
                                           break_long_words=self.break_long_words,
                                           break_on_hyphens=self.break_on_hyphens)

            if wrapped_lines:
                comment += '\n'.join(indent + line for line in wrapped_lines)
            else:
                # Special case because textwrap.wrap will return an empty list
                # if the paragraph is all whitespace.
                comment += indent.rstrip()

        return comment
import textwrap
import re

    # This is a comment with blank lines and nested indention. Lorem ipsum dolor sit
    #
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris.
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante
    #     hendrerit.
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit
    # amet vitae augue.

class GreatestCommonPrefix:
    def __init__(self, regex=None, whitelist=None):
        self.regex = re.compile(regex) if regex else None
        self.whitelist = set(whitelist or [])

    def parse(self, strings):
        if self.regex:
            new_strings = []
            for s in strings:
                r = self.regex.match(s)

                if r is None:
                    return ''

                new_strings.append(r.group(0))

            strings = new_strings

        match = ''

        for chars in zip(*strings):
            if self.chars_are_matched(chars):
                match += chars[0]
            else:
                break

        return match

    def chars_are_matched(self, items):
        # Don't get the first item with items[0] because
        # that doesn't allow for empty iterators (for which this function is vacuosly true)
        # and makes handling single items iterators more complicated
        is_first = True

        for item in items:
            if is_first:
                if self.whitelist and item not in self.whitelist:
                    return False
                prev = item
                is_first = False
            elif item != prev:
                return False

        return True


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

# Don't require the sublime modules so the other classes can be tested
try:
    import sublime
    import sublime_plugin
except:
    pass
else:
    class CommentReflowCommand(sublime_plugin.TextCommand):
        def run(self, edit):
            self.get_selection()

            try:
                self.get_preferences()
                reflow = ReflowComment(**self.preferences)
                self.new_comment = reflow.reflow(self.selected_text)
            except Exception:
                raise
                sublime.status_message('Did not recognize selection as a comment')
            else:
                self.replace_lines(edit)

        def replace_lines(self, edit):
            classes = 0

            if not self.view.classify(max(self.region.a, self.region.b)) & sublime.CLASS_LINE_END:
                print('line end')
                classes |= sublime.CLASS_LINE_END

            if not self.view.classify(min(self.region.a, self.region.b)) & sublime.CLASS_LINE_START:
                print('line start')
                classes |= sublime.CLASS_LINE_START

            region = self.view.expand_by_class(self.region, classes)
            self.view.replace(edit, region, self.new_comment)

        def get_language_specific_settings(self, settings):
            scopes = self.view.scope_name(self.view.sel()[0].a).split()

            try:
                comment_scope = next(s for s in scopes if s.startswith('comment.line.'))
                comment_type = comment_scope.split('.')[2]

                markers = {'number-sign': r'#+',
                           'double-slash': r'/{2,}',
                           'apostrophe': r"'+",
                           'double-dash': r'\-{2,}',
                           'semicolon': r';+'}
                marker_regex = markers[comment_type]
            except (StopIteration, IndexError, KeyError):
                # We are not in a comment.line.* scope or we are in one that is not accounted for.
                self.marker = settings.get('comment_reflow_marker')
                self.comment_start_regex = settings.get('comment_reflow_comment_start_regex')

                if not self.marker:
                    raise ValueError
            else:
                self.marker = None
                whitespace = r'[ \t]*'
                self.comment_start_regex = whitespace + marker_regex + whitespace

        def get_preferences(self):
            settings = self.view.settings()
            self.get_language_specific_settings(settings)

            # I would like to make the ruler the fall back for max_width but I have
            # not been able to find a way to get the current ruler besides the
            # setting 'rulers' which seems to be a global setting and doesn't refer
            # to the current file's ruler.
            self.preferences = {
                'marker': self.marker,
                'max_width': int(settings.get('comment_reflow_width', 80)),
                'tab_size': int(settings.get('tab_size', 4)),
                'break_long_words': bool(settings.get('comment_reflow_break_long_words', False)),
                'break_on_hyphens': bool(settings.get('comment_reflow_break_on_hyphens', True)),
                'comment_start_regex': self.comment_start_regex,
                'new_paragraph_regex': settings.get('comment_reflow_new_paragraph_regex', r'[*-] ')}

        def get_selection(self):
            # This assumes there is only one selection. We do not need to check for
            # that condition because of the is_enabled method.
            self.region = self.view.sel()[0]
            # lines_touched is a list of regions
            lines_touched = self.view.lines(self.region)
            self.selected_text = '\n'.join(self.view.substr(region) for region in lines_touched)
            return True

        def is_enabled(self):
            return len(self.view.sel()) == 1

        def description(self):
            return 'Reflow comments to a particular width'
import textwrap
import re


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
        # Don't get the first item with items[0] because that doesn't allow for
        # empty iterators (for which this function is vacuosly true) and makes
        # handling single items iterators more complicated
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
        # since we have to account for comment_start_regex.
        #
        # A paragraph is a string to be wrapped. It is not indented and contains
        # no new lines. A new paragraph is started when a line matches one of
        # the following conditions:
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

        for line in lines:
            try:
                start = comment_start_regex.match(line).group(0)
            except AttributeError:
                raise ValueError('text contained a line that did not match the comment start regex')

            line_without_start = self.remove_prefix(line, start)

            force_new_paragraph = new_paragraph_regex is not None and re.match(self.new_paragraph_regex, line_without_start)

            if (start != prev_start) or force_new_paragraph:
                # New paragraph
                if prev_start is not None:
                    paragraphs.append((prev_start, current_paragraph))

                prev_start = start
                current_paragraph = line_without_start.rstrip()
            else:
                # Same paragraph
                current_paragraph += ' ' + line_without_start.rstrip()

        if current_paragraph:
            paragraphs.append((prev_start, current_paragraph))

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
except ImportError:
    pass
else:
    class CommentReflowCommand(sublime_plugin.TextCommand):
        def run(self, edit):
            self.edit = edit
            self.get_region()
            selected_text = self.view.substr(self.region)

            if self.get_preferences():
                reflow = ReflowComment(**self.preferences)

                try:
                    self.new_comment = reflow.reflow(selected_text)
                except Exception:
                    sublime.status_message('Did not recognize selection as a comment')
                else:
                    self.replace_lines()

        def replace_lines(self):
            self.view.replace(self.edit, self.region, self.new_comment)

        def get_comment_start(self, settings):
            marker = settings.get('comment_reflow_marker')

            if marker is None:
                comment_start_regex = settings.get('comment_reflow_comment_start_regex')
                scopes = self.view.scope_name(self.view.sel()[0].a).split()

                try:
                    comment_scope = next(s for s in scopes if s.startswith('comment.line.'))
                    comment_type = comment_scope.split('.')[2]

                    if comment_type == 'number-sign':
                        marker_regex = '#'
                        marker_repeat = '+'
                    elif comment_type == 'double-slash':
                        marker_regex = '/'
                        marker_repeat = '{2,}'
                    elif comment_type == 'apostrophe':
                        marker_regex = '\''
                        marker_repeat = '+'
                    elif comment_type == 'double-dash':
                        marker_regex = r'\-'
                        marker_repeat = '{2,}'
                    elif comment_type == 'semicolon':
                        marker_regex = ';'
                        marker_repeat = '+'
                    else:
                        raise ValueError
                except (StopIteration, ValueError):
                    # We are not in a comment.line.* scope or we are in one that
                    # is not accounted for.
                    sublime.status_message('Either comment_reflow_marker or comment_reflow_comment_start_regex is required for this language')
                    return False

                try:
                    comment_start_regex = comment_start_regex.format(
                        marker=marker_regex, repeat=marker_repeat)
                except (AttributeError, IndexError, KeyError):
                    whitespace = r'[ \t]*'
                    comment_start_regex = whitespace + marker_regex + marker_repeat + whitespace

                self.preferences['comment_start_regex'] = comment_start_regex
                print(comment_start_regex)
            else:
                self.preferences['marker'] = marker

            return True

        def get_max_width(self, settings):
            width_setting = settings.get('comment_reflow_width')

            try:
                try:
                    max_width = int(width_setting)
                except ValueError:
                    if width_setting.startswith('rulers_'):
                        rulers = settings.get('rulers')

                        if len(rulers):
                            which_ruler = width_setting[len('rulers_'):]

                            if which_ruler == 'first':
                                ruler_index = 0
                            elif which_ruler == 'last':
                                ruler_index = -1
                            else:
                                ruler_index = int(which_ruler)

                                # Force ruler_index to the closest valid value
                                if ruler_index < 0 and abs(ruler_index) > len(rulers):
                                    ruler_index = 0
                                elif ruler_index > len(rulers) - 1:
                                    ruler_index = -1

                            max_width = int(rulers[ruler_index])
                        else:
                            max_width = int(settings.get('comment_reflow_width_fallback'))
                    else:
                        raise ValueError
            except (TypeError, ValueError):
                max_width = 80

            self.preferences['max_width'] = max_width

        def get_preferences(self):
            settings = self.view.settings()
            self.preferences = {}

            if not self.get_comment_start(settings):
                return False

            self.get_max_width(settings)

            self.preferences.update({
                'tab_size': int(settings.get('tab_size', 4)),
                'break_long_words': bool(settings.get('comment_reflow_break_long_words', False)),
                'break_on_hyphens': bool(settings.get('comment_reflow_break_on_hyphens', True)),
                'new_paragraph_regex': settings.get('comment_reflow_new_paragraph_regex', r'[*-] ')
            })
            return True

        def get_region(self):
            # This assumes there is only one selection. We do not need to check
            # for that condition because of the is_enabled method.
            self.region = self.view.sel()[0]

            # Expand to the include the entire lines.
            self.region = self.view.line(self.region)

        def is_enabled(self):
            return len(self.view.sel()) == 1

        def description(self):
            return 'Reflow comments to a particular width'
import sublime
import sublime_plugin

    # This is a comment with blank lines and nested indention. Lorem ipsum dolor
    # sit
    #
    #     - amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet
    #     ipsum mauris.
    #     - Maecenas congue ligula ac quam viverra nec consectetur ante
    #     hendrerit.
    # Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit
    # amet vitae augue.


class CommentReflowCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.get_selection()

        try:
            self.get_preferences()
            reflow = ReflowComment(**self.preferences)
            self.new_comment = reflow.reflow(self.selected_text)
        except Exception:
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
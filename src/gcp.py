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
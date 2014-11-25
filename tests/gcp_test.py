from src.CommentReflow import GreatestCommonPrefix

class TestBasic:
    gcp = GreatestCommonPrefix()

    def test_pine_match(self):
        actual = self.gcp.parse(['pineapple',
                            'pine tree'])
        assert 'pine' == actual

    def test_pine_miss(self):
        actual = self.gcp.parse([' pineapple',
                            'pine tree'])
        assert '' == actual

    def test_indented_match(self):
        actual = self.gcp.parse(['    chicken',
                            '    chickpea'])
        assert '    chick' == actual

    def test_same_match(self):
        actual = self.gcp.parse(['dog',
                            'dog'])
        assert 'dog' == actual

    def test_whole_word_match(self):
        actual = self.gcp.parse(['stack',
                            'stacked'])
        assert 'stack' == actual

    def test_whole_word_match_reordered(self):
        actual = self.gcp.parse(['stacked',
                            'stack'])
        assert 'stack' == actual

    def test_empty_strings(self):
        actual = self.gcp.parse(['', ''])
        assert '' == actual

    def test_single_item(self):
        actual = self.gcp.parse(['single'])
        assert 'single' == actual

    def test_many_match(self):
        actual = self.gcp.parse(['single',
                            'singleton',
                            'singing',
                            'singed',
                            'sine'])
        assert 'sin' == actual

class TestWhiteSpaceWhiteList:
    gcp = GreatestCommonPrefix(whitelist=' \t\r\n')

    def test_spaces(self):
        actual = self.gcp.parse(['       pineapple',
                                 '       pine tree'])
        assert '       ' == actual

    def test_four_spaces_tab_no_match(self):
        actual = self.gcp.parse(['    pineapple',
                            '\tpine tree'])
        assert '' == actual

    def test_eight_spaces_tab_no_match(self):
        actual = self.gcp.parse(['        pineapple',
                            '\tpine tree'])
        assert '' == actual

    def test_different_line_endings_no_match(self):
        actual = self.gcp.parse(['\r\n',
                            '\n'])
        assert '' == actual

    def test_alternating_allowed(self):
        actual = self.gcp.parse(['\tW\tW',
                            '\tW\tW'])
        assert '\t' == actual

    def test_same_word_blacklisted(self):
        actual = self.gcp.parse(['test',
                            'test'])
        assert '' == actual

class TestWhiteList:
    gcp = GreatestCommonPrefix(whitelist='pla')

    def test_partial_match(self):
        actual = self.gcp.parse(['appliance',
                            'applicable'])
        assert 'appl' == actual

    def test_full_match(self):
        actual = self.gcp.parse(['pal',
                            'pal'])
        assert 'pal' == actual

    def test_no_match(self):
        actual = self.gcp.parse(['dog',
                            'dog'])
        assert '' == actual

class TestRegex:
    gcp = GreatestCommonPrefix(regex=r"[ \t]*'+[ \t]*")

    def test_one_single_quote(self):
        actual = self.gcp.parse(["'' test",
                            "' test"])
        assert "'" == actual

    def test_space_no_quote(self):
        actual = self.gcp.parse([' pineapple',
                            'pine tree'])
        assert '' == actual

    def test_spaces_no_quote(self):
        actual = self.gcp.parse(['    chicken',
                            '    chickpea'])
        assert '' == actual

    def test_spaces_quote(self):
        actual = self.gcp.parse(["    'chicken",
                            "    'chickpea"])
        assert "    '" == actual

    def test_spaces_quote_tab(self):
        actual = self.gcp.parse(["    '\tchicken",
                            "    '\tchickpea"])
        assert "    '\t" == actual

    def test_same_word_no_match(self):
        actual = self.gcp.parse(["dog",
                            "dog"])
        assert "" == actual

    def test_quoted_word_single_quotes(self):
        actual = self.gcp.parse(["'stack'",
                            "'stacked'"])
        assert "'" == actual

    def test_quoted_word_double_quotes(self):
        actual = self.gcp.parse(['"stack"',
                            '"stacked"'])
        assert "" == actual
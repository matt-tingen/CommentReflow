# CommentReflow

A Sublime Text 3 plugin for reflowing comments to fit a certain width.


## Installation
On Windows, save `CommentReflow.sublime-package` to `%appdata%\Sublime Text 3\Installed Packages\`.

## Usage
Select the comment you want to reflow and use the keyboard shortcut `Ctrl+Alt+R`. Any lines touched by the selection will be reflowed.

### Examples

#### Wrapping long lines
```python
# Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit.
```
changes to

```python
# Lorem ipsum dolor sit amet,
# consectetur adipiscing elit. Donec a
# diam lectus. Sed sit amet ipsum
# mauris. Maecenas congue ligula ac quam
# viverra nec consectetur ante
# hendrerit.
```

#### Improperly wrapped lines
```python
# Lorem ipsum dolor
# sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet
# ipsum
# mauris. Maecenas congue
# ligula ac quam viverra nec consectetur ante hendrerit.
```
changes to

```python
# Lorem ipsum dolor sit amet,
# consectetur adipiscing elit. Donec a
# diam lectus. Sed sit amet ipsum
# mauris. Maecenas congue ligula ac quam
# viverra nec consectetur ante
# hendrerit.
```

#### Lists
```python
# Here's a comment with a long line that still gets wrapped
# but also a list that doesn't get messed up by wrapping.
#    - Short list item 1
#    - Short list item 2
#    - Long list item that does need to be wrapped, but only by itself.
#    - Final short item
```
changes to

```python
# Here's a comment with a long line that
# still gets wrapped but also a list
# that doesn't get messed up by
# wrapping.
#    - Short list item 1
#    - Short list item 2
#    - Long list item that does need to
#    be wrapped, but only by itself.
#    - Final short item
```


### Limitations

Block comments (e.g. `/* … */`) and multi-line strings (e.g. `""" … """`) are not currently supported.

## Behavior
In order to be flexible, CommentReflow does not simply reflow all lines together. CommentReflow groups lines into "paragraphs" which are reflowed. This section explains how paragraphs are determined. 

A **paragraph** is a collection of lines that will be reflowed together.

The **marker** is the character(s) defined by a language indicating the beginning of a line comment. For example, `#` in Python, `//` in C, etc. 

The **opening** is the text with which a line begins. All lines in a paragraph will have the same opening.
By default, the opening of a line will include indention (if any), followed by the marker, followed by any whitespace (if any). For example, for the comment in:
```python
def foo():
    # This comment is indented and has a space after the marker
    pass
``` 
the marker would include the indention, the marker (`#`), and the space immediately following the marker.

The **body** of a comment is the text on a line after the opening.
In the above example, the body would be `This comment is indented and has a space after the marker`.

Reflowing will ensure that lines within each paragraph are as long as possible without exceeding the specified width (see settings below).

Because all lines in a paragraph have the same opening, if the opening on a line is different from the previous line (e.g. different whitespace after the marker), a new paragraph will begin.

A new paragraph will also be forced if the body of a line is matched by the regular expression in the setting `comment_reflow_new_paragraph_regex`.

## Settings

*Note: Some of the settings in this section use terminology defined in the __Behavior__ section above.*

### `comment_reflow_width`
**Purpose:** Defines the max width for each line.

**Default:** `rulers_first`

**Values:** Positive integer or string starting with `rulers_`.
If a string, the text following `rulers_` specify which of the built-in rulers (setting name `rulers`, value should be a list of integers) to use to define the max width. It can be `rulers_first`, `rulers_last`, or `rulers_<n>` where `<n>` is the index of ruler to use. The index may be negative to index from the back of the list. If the index specified is out of bounds, the closest in-bounds index will be used.
If this setting is set to use the rulers but `rulers` is empty, `comment_reflow_width_fallback` will be used

### `comment_reflow_width_fallback`
**Purpose:** Defines a fallback max width for when it is supposed to be determined from the rulers but there are none.

**Default:** `80`

**Values:** Positive integer

### `comment_reflow_break_long_words`
**Purpose:** Defines whether words longer than the max width should be broken to fit in the width.

**Default:** `false`

**Values:** `true` or `false`

### `comment_reflow_break_on_hyphens`
**Purpose:** Defines whether hyphenated words may be broken after the hyphen.

**Default:** `true`

**Values:** `true` or `false`

### `comment_reflow_marker`
**Purpose:** Define the marker for languages for which it is not already defined.

**Default:** no default value

**Values:** String containing the marker.
Unless using this specifically for a language with no marker, `comment_reflow_comment_start_regex` is the preferred setting for defining line openings.

### `comment_reflow_opening_regex`
**Purpose:** Defines the opening for each line.

**Default:** `[ \t]*{marker}{marker_repeat}[ \t]*`

**Values:** String containing a regular expression.
`{marker}` will be replaced with the language's marker. If the marker is a single character repeated twice (e.g. `//` or `--`), `{marker}` will only be one of the characters, not two. 
`{repeat}` will be replaced with the necessary repetition for the marker character. It will allow more than than what is required by the language. For example, in python, `{marker}{marker_repeat}` will expand to `#+` and in C, it will expand to `/{2,}`.
`{repeat_strict}` will be replaced with the exact repetition necessary. e.g. `{2}`.
*Note: despite the replacement syntax, this setting does __not__ use Python format strings so literal braces do not need to be escaped.*

### `comment_reflow_new_paragraph_regex`
**Purpose:** Defines whether the body of a line should force a new paragraph.

**Default:** `[*+-] |\d+[).] |[ \t]*$`
Matches Markdown-style lists or when the entire body is whitespace or empty.

**Values:** String containing a regular expression.
If the regex matches the body of the line, a new paragraph will begin including that line.

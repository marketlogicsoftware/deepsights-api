# Copyright 2024 Market Logic Software AG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the functions to segment the content of a document.
"""

import re
from typing import List, Dict


#############################################
def _parse_page(content):
    """
    Construct segments as semantic units from the given page structure, guessing from font sizes.
    Generates markdown for headings.

    Args:

        content (list): The list of tuples representing the page structure, where each tuple contains
                        the font size and the corresponding text.

    Returns:

        list: The list of segments as semantic units generated from the page structure.
    """

    # no more content?
    if len(content) == 0:
        return []

    # we want to find the next segment now and then recurse on the tail of the content
    next_segment = ""

    # track what font size we had last
    last_font_size = None

    # inspect next item
    while len(content) > 0:
        (next_font_size, next_text) = next_item = content.pop(0)

        # check font size
        if last_font_size is not None:
            # compare to last
            if next_font_size > 1.4 * last_font_size:
                # new section
                content.insert(0, next_item)
                break

        last_font_size = next_font_size

        # if we have sth to append...
        if next_text is not None:
            # append text & remember page
            next_segment += next_text + "\n"

    # get rid of duplicate whitespace (except LF)
    segment_text = re.sub(r"[^\S\n]+", " ", next_segment)

    # get rid of 3+ LFs
    segment_text = re.sub(r"\n{3,}", "\n\n", segment_text, re.MULTILINE)

    # recurse on tail
    segments = [segment_text]
    segments.extend(_parse_page(content))

    return segments


#############################################
def segment_landscape_page(page_structure: Dict) -> List[Dict]:
    """Segmentation strategy that follows pages

    Args:

        page_structure (Dict): The structure of the page.

    Returns:

        List[Dict]: A list of segmented sections.

    """
    # collect font / text tuples by page
    content = []
    if page_structure["semantic_sections"] is not None:
        for section in page_structure["semantic_sections"]:
            for element in section["semantic_section_elements"]:
                text = element["text_value"]["text"].strip()

                if (
                    element.get("normalized_layout", None)
                    and "height" in element["normalized_layout"]
                ):
                    font_size = 2 * int(
                        500
                        * float(element["normalized_layout"]["height"])
                        / len(text.split("\n"))
                    )
                else:
                    font_size = 16

                content.append((font_size, text))

    # collect segments
    segments = list(filter(lambda s: len(s) > 40, _parse_page(content)))

    # now merge into one
    return "\n\n".join(segments)

from typing import List, Dict, Any

from .joining_and_extraction.join import (
    join_metadata_lines_properly,
    join_list_lines_properly,
    join_def_list_lines_properly,
    join_table_lines_properly,
    join_code_lines_properly,
    join_blockquote_lines_properly,
    delete_empty_paragraphs
)
from .hierarchy.hierarchy import build_hierarchy


#########################
# FINAL MD DATA
#########################
def final_md_data(classified_list: List[Dict[str, Any]], hierarchy: bool = True) -> List[Dict[str, Any]]:
    '''
    Takes a stripped and classified list of markdown rows. -> see classification.py
    Hands over the list to different functions for joining, extracting and convert the data -> see join.py and extraction.py
    Builds the final hierarchy based on the headings -> see hierachy.py
    
    Returns a list of dictionaries with the converted markdown considering the hierarchy of the original markdown.
    '''
    # Metadata:
    classified_list = join_metadata_lines_properly(classified_list=classified_list)
    # Lists: 
    classified_list = join_list_lines_properly(classified_list=classified_list)
    # Definition lists: 
    classified_list = join_def_list_lines_properly(classified_list=classified_list)
    # Tables:
    classified_list = join_table_lines_properly(classified_list=classified_list)
    # Code:
    classified_list = join_code_lines_properly(classified_list=classified_list)
    # Blockquotes:
    classified_list = join_blockquote_lines_properly(classified_list=classified_list)
    # Paragraphs: 
    # not merge paragraphs but delete empty paragraphs. Why? -> because maybe later we want to specify paragraphs in pydantic
    classified_list = delete_empty_paragraphs(classified_list=classified_list)

    # Hierarchy: # TODO: constructing the hierarchy of the markdown
    if hierarchy:
        final_list = build_hierarchy(classified_list=classified_list)
    else:
        final_list = classified_list

    return final_list
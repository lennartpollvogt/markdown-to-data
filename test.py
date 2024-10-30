from markdown_to_data.markdown_to_data import Markdown
import rich

markdown_test = """
---
title: The test of markdown-to-data
creation_date: 22.10.2024
---

# Testing the capabilities of `markdown-to-data`

Table of content:
- tables
- lists
    - unordered list
    - ordered list
- blockquotes

## Table section

| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |
|----------------|--------------|--------------|-----------------|------------|
| Cloud Services | 100,000      | 150,000      | 250,000         | 50%        |
| Maintenance    | 80,000       | 90,000       | 170,000         | 12.5%      |
| Consulting     | 50,000       | 70,000       | 120,000         | 40%        |

| Services       | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |
|----------------|--------------|--------------|-----------------|------------|
| Cloud Services | 100,000      | 150,000      | 250,000         | 50%        |
| Maintenance    | 80,000       | 90,000       | 170,000         | 12.5%      |
| Consulting     | 50,000       | 70,000       | 120,000         | 40%        |

## Lists section

**Unordered list**
- Item 1
- Item 2
- Item 3
    - Subitem 1
    - Subitem 2

**Ordered list**
1. Item 1
2. Item 2
    1. Subitem 1
    2. Subitem 2
3. Item 3

## Blockquotes

> A simple blockquote

> A mulitline blockquote
    > with intend
> Over three lines


# Heading 1 on end of markdown file

some paragraph
"""

markdown_class = Markdown(markdown=markdown_test)

rich.print(markdown_class.md_list)
#rich.print(markdown_class.md_hierarchy_list)
rich.print(markdown_class.md_dict)


# TODO: Use the headings as a key and nest them
# Or give the possibility to have all three options
# 1. All building blocks are a seperate dictionary within the LIST --> exists
# 2. All buildings blocks are nested. The headings are the keys for each dictionary in the DICTIONARY
# 3. All buildings blocks are nested. The key is the level of heading (e.g. h1, h2, ...) --> exists
#
# This approach would mean a clear idea how to use the markdown class and its methods
# Q: What methods do I need for the user of the markdown class?
# Q: What functions to I need in the background? What is the base for converting into the different outpus formats?

final_result = {
    'metadata': {'title': 'The test of markdown-to-data', 'creation_date': '22.10.2024'},
    'Testing the capabilities of `markdown-to-data`': {
        'paragraph': 'Table of content:',
        'list': {
            'type': 'ul',
            'list': [['tables'], ['lists', [['unordered list'], ['ordered list']]], ['blockquotes']]
        },
        'Table': {
            'table': [
                {
                    'Service': 'Cloud Services',
                    'Q1 Sales ($)': '100,000',
                    'Q2 Sales ($)': '150,000',
                    'Total Sales ($)': '250,000',
                    'Growth (%)': '50%'
                },
                {
                    'Service': 'Maintenance',
                    'Q1 Sales ($)': '80,000',
                    'Q2 Sales ($)': '90,000',
                    'Total Sales ($)': '170,000',
                    'Growth (%)': '12.5%'
                },
                {
                    'Service': 'Consulting',
                    'Q1 Sales ($)': '50,000',
                    'Q2 Sales ($)': '70,000',
                    'Total Sales ($)': '120,000',
                    'Growth (%)': '40%'
                }
            ],
            'paragraph': 'Second table:',
            'table': [
                {
                    'Service': 'Cloud Services',
                    'Q1 Sales ($)': '100,000',
                    'Q2 Sales ($)': '150,000',
                    'Total Sales ($)': '250,000',
                    'Growth (%)': '50%'
                },
                {
                    'Service': 'Maintenance',
                    'Q1 Sales ($)': '80,000',
                    'Q2 Sales ($)': '90,000',
                    'Total Sales ($)': '170,000',
                    'Growth (%)': '12.5%'
                },
                {
                    'Service': 'Consulting',
                    'Q1 Sales ($)': '50,000',
                    'Q2 Sales ($)': '70,000',
                    'Total Sales ($)': '120,000',
                    'Growth (%)': '40%'
                }
            ]
        },
        'Lists': {
            'Unordered list': {
                'list': {
                    'type': 'ul',
                    'list': [['Item 1'], ['Item 2'], ['Item 3', [['Subitem 1'], ['Subitem 2']]]]
                }
            },
            'Ordered list': {
                'list': {
                    'type': 'ol',
                    'list': [['Item 1'], ['Item 2', [['Subitem 1'], ['Subitem 2']]], ['Item 3']]
                }
            }
        },
        'Blockquotes': {
            'blockquote': [['A simple blockquote']],
            'blockquote': [['A mulitline blockquote'], ['with intend'], ['Over three lines']]
        }
    }
}

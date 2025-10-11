from typing import Union


def page_parameter(page:Union[int, str]=1):
    """
    Ensures the page parameter is a valid integer and adjusts it for zero-based indexing.
    """
    if type(page) == str:
        try:
            page = int(page)
        except ValueError:
            page = 1
            
    if page >= 1:
        page -= 1
    else:
        page = 0
    
    return page


def get_pages(iterable:Union[list, dict], entries_per_page:int=10):
    return (len(iterable) // entries_per_page) + 1


def get_page(iterable:Union[list, dict], page_nr:int=0, message_header:str="Default Message Header\n", entries_per_page:int=10):
    message = message_header
    start = page_nr * entries_per_page
    for line in iterable[start:start+entries_per_page]:
        message += f' - {line}\n'
    
    return message
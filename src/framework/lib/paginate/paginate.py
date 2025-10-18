from typing import Union


def page_parameter(pages: int, page:Union[int, str]=1) -> int:
    if type(page) == str:
        try:
            page = int(page)
        except ValueError:
            page = 1
            
    if page >= 1:
        page -= 1
    else:
        page = 0
        
    if page > pages:
        page = pages - 1
    
    return page


def get_pages(iterable:Union[list, dict], entries_per_page:int=10) -> int:
    return (len(iterable) // entries_per_page) + 1


def get_page(iterable:Union[list, dict],
             page_nr:int=0,
             message_header:str="Default Message Header\n",
             entries_per_page:int=10,
             iterator:str=" - ",
             linebreaker:str="\n") -> str:
    
    if type(iterable) == list:
        return __get_page_list(iterable, page_nr, message_header, entries_per_page, iterator, linebreaker)
    
    elif type(iterable) == dict:
        return __get_page_dict(iterable, page_nr, message_header, entries_per_page, iterator, linebreaker)
    
    return None


def __get_page_list(iterable:list,
             page_nr:int=0,
             message_header:str="Default Message Header\n",
             entries_per_page:int=10,
             iterator:str=" - ",
             linebreaker:str="\n") -> str:
    
    message = message_header
    start = page_nr * entries_per_page
    for line in iterable[start:start + entries_per_page]:
        message += f'{iterator}{line}{linebreaker}'
    
    return message


def __get_page_dict(iterable:dict,
             page_nr:int=0,
             message_header:str="Default Message Header\n",
             entries_per_page:int=10,
             iterator:str=" - ",
             linebreaker:str="\n") -> str:
    
    message = message_header
    start = page_nr * entries_per_page

    for key, value in list(iterable.items())[start:start + entries_per_page]:
        message += f'{iterator}{key}: {value}{linebreaker}'
        
    return message


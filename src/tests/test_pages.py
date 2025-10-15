
from framework.lib.paginate import paginate
from random import randint


def test_list():
    print("Test List")
    start = 0
    end = 1000
    test_entries = [(a, randint(start, end)) for a in range(start, end)]
    
    items_per_page = 10
    
    pages = paginate.get_pages(test_entries, items_per_page)
    page_nr = 4
    
    message = paginate.get_page(test_entries, page_nr, f"Test Entries [{page_nr}/{pages-1}]\n", items_per_page, iterator="* ")
    
    print(message)
    
    page_nr = paginate.page_parameter(pages, 500)
    
    print(f"laste page nr: {page_nr}")
    
    
def test_dict():
    print("Test Dict")
    start = 0
    end = 100 
    test_entries = {a: randint(start, end) for a in range(start, end)}
    
    items_per_page = 10
    
    pages = paginate.get_pages(test_entries, items_per_page)
    page_nr = 1
    
    message = paginate.get_page(test_entries, page_nr, f"Test Entries [{page_nr}/{pages-1}]\n", items_per_page, iterator="> ")
    
    # print(test_entries)
    print(message)


if __name__ == "__main__":
    test_list()
    test_dict()

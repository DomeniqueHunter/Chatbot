
from framework.lib.paginate import paginate

start = 0
end = 1000
test_entries = [(a, b) for a, b in zip(range(start, end), range(start * 2, end * 2))]

pages = paginate.get_pages(test_entries, 10)
page_nr = 4

message = paginate.get_page(test_entries, page_nr, f"Test Entries [{page_nr+1}/{pages}]\n", 10, iterator="* ")

print(message)

page_nr = paginate.page_parameter(pages, 500)

print(f"laste page nr: {page_nr}")

from framework.lib.paginate import paginate


test_entries = [(a, b) for a, b in zip(range(1, 101), range(101, 201))]

pages = paginate.get_pages(test_entries, 10)
page_nr = 4

message = paginate.get_page(test_entries, page_nr, f"Test Entries [{page_nr+1}/{pages}]\n", 10)

print(message)


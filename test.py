url = 'https://1337x.to/search/cat/ss/26/'

# split by / and get the last element

page_number = int(url.split('/')[-2])

#remove the page number from the url
raw_page_without_number = url.replace(f'/{page_number}/', '/')

print(page_number)

print(raw_page_without_number)
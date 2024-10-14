import requests
from bs4 import BeautifulSoup
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = 'https://jobs.dou.ua/companies/?name=Харків'

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

print(soup)

with open('companies.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Назва компанії', 'Локація'])

    companies = soup.find_all('div', class_='company')

    for company in companies:
        name = company.find('a', class_='cn-a').text.strip()

        location = company.find('span', class_="city bi bi-geo-alt-fill").text.strip()

        if 'Харків' in location:
            writer.writerow([name, location])

print("Парсинг завершено. Дані збережено у файлі companies.csv")

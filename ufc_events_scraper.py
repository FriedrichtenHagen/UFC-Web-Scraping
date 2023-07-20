#Import libraries for web-scraping and saving to CSV file.

import requests
import bs4
import csv
import os
from datetime import datetime

#Get event URLs from file
if 'event_urls.csv' in os.listdir():
    with open('event_urls.csv','r') as events_csv:
        reader = csv.reader(events_csv)
        event_urls = [row[0] for row in reader]
else:
    print("Missing file - event_urls.csv. Try running 'get_event_urls.py'")

#Creates csv file for scraped data
def create_csv_file():
    #If file does not exist, create a new CSV file with column headers
    if 'ufc_event_data.csv' not in os.listdir():
        with open('ufc_event_data.csv','w', newline='',encoding='UTF8') as ufc_event_data:
            writer = csv.writer(ufc_event_data)
            writer.writerow(['event_name',
                             'event_date',
                             'event_city',
                             'event_state',
                             'event_country',
                             'event_url'])
        print('New File Created - ufc_event_data.csv')
    else:
        print('Scraping to Existing File - ufc_event_data.csv')

#Scrapes url of each UFC event from ufcstats.com
def get_event_urls():
    main_url = requests.get('http://ufcstats.com/statistics/events/completed?page=all')
    main_event_soup = bs4.BeautifulSoup(main_url.text, 'lxml')
    
    #Adds href to list if href contains a link with keyword 'event-details'
    all_event_urls = [item.get('href') for item in  main_event_soup.find_all('a') 
                      if type(item.get('href')) == str 
                      and 'event-details' in item.get('href')]
    
    return all_event_urls


#Ensure each url is only scraped once when script is run multiple times
def filter_duplicate_urls(event_urls):
    if 'ufc_event_data.csv' in os.listdir():
        with open('ufc_event_data.csv','r') as csv_file:
            reader = csv.DictReader(csv_file)
            #List of previously scraped urls:
            scraped_event_urls = [row['event_url'] for row in reader]
            #Removes scraped urls from event_urls
            for url in scraped_event_urls:
                if url in event_urls:
                    event_urls.remove(url)


#Scrapes details of each UFC event appends to CSV file 'ufc_event_data'
def get_event_data(event_urls):

    filter_duplicate_urls(event_urls)
    
    urls_to_scrape = len(event_urls)
    print(f'Scraping {urls_to_scrape} event URLs...')
    urls_scraped = 0

    with open('ufc_event_data.csv','a+') as csv_file:
        writer = csv.writer(csv_file)
    
        #Iterates through each event url to scrape key details
        for event in event_urls:
            event_request = requests.get(event)
            event_soup = bs4.BeautifulSoup(event_request.text,'lxml')
            event_full_location = event_soup.select('li')[4].text.split(':')[1].strip().split(',')

            try:
                event_name = event_soup.select('h2')[0].text
                event_date = str(datetime.strptime(event_soup.select('li')[3].text.split(':')[-1].strip(), '%B %d, %Y'))
                event_city = event_full_location[0]
                event_country = event_full_location[-1]
                #Check event location contains state details
                if len(event_full_location)>2:
                    event_state = event_full_location[1]
                else:
                    event_state = 'NULL'
                urls_scraped += 1
                    
            except IndexError as e:
                print(f"Error scraping event page: {event}")
                print(f"Error details: {e}")
                

            #Adds new row to csv file
            writer.writerow([event_name.strip(), 
                             event_date[0:10], 
                             event_city.strip(), 
                             event_state.strip(), 
                             event_country.strip(), 
                             event])
            
        print(f'{urls_scraped}/{urls_to_scrape} events successfully scraped')

create_csv_file()
get_event_data(event_urls)

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

course_data = []

def scrape_page(url):
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'courses-feed__list'))
        )
    except Exception as e:
        print(f"Error: {e}")
        return
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    course_list = soup.find('ul', class_='courses-feed__list')
    if course_list:
        for course_item in course_list.find_all('li', class_='courses-feed__item'):
            title_h3 = course_item.find('h3', class_='courses-feed__item-title')
            title = title_h3.find('span').text.strip() if title_h3 else "N/A"
            course_link = course_item.find('a', class_='courses-feed__item-link')
            course_href = course_link['href'] if course_link else None
            meta_div_2 = course_item.find('div', class_='courses-feed__meta courses-feed__meta--2')
            if meta_div_2:
                course_type = meta_div_2.find('p', class_='courses-feed__info courses-feed--type')
                course_type_text = course_type.text.strip() if course_type else "N/A"
            else:
                course_type_text = "N/A"
            credits = meta_div_2.find('p', class_='courses-feed__info courses-feed__info--credits') if meta_div_2 else None
            credits_text = credits.text.strip() if credits else "N/A"
            time_ul = course_item.find('ul', class_='courses-feed__info courses-feed__info--times')
            if time_ul:
                time_li = time_ul.find('li')
                course_time = time_li.text.strip() if time_li else "N/A"
            else:
                course_time = "N/A"
            instructor = course_item.find('p', class_='courses-feed__info courses-feed__info--instructor')
            instructor_text = instructor.text.strip() if instructor else "N/A"
            if course_href:
                driver.get(course_href)
                detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                detail_div = detail_soup.find('div', class_='js-hang-punc gutenberg-content')
                prerequisite, exam_type, description, extra_note, room, areas_of_interest = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
                if detail_div:
                    paragraphs = detail_div.find_all('p')
                    for p in paragraphs:
                        strong_tag = p.find('strong')
                        if strong_tag:
                            if "Prerequisite" in strong_tag.text:
                                prerequisite = p.text.replace("Prerequisite:", "").strip()
                            elif "Exam Type" in strong_tag.text:
                                exam_type = p.text.replace("Exam Type:", "").strip()
                        else:
                            if description == "N/A":
                                description = p.text.strip()
                            else:
                                extra_note = p.text.strip()
                aside_div = detail_soup.find('aside', class_='data-page__detail-aside')
                if aside_div:
                    room_dt = aside_div.find('dt', text='Room')
                    room = room_dt.find_next('dd').text.strip() if room_dt else "N/A"
                    areas_of_interest = []
                    interest_dt = aside_div.find('dt', text='Areas of Interest')
                    if interest_dt:
                        interest_dd = interest_dt.find_next('dd')
                        while interest_dd and interest_dd.name == 'dd':
                            area_links = interest_dd.find_all('a')
                            areas_of_interest.extend([a.text.strip() for a in area_links])
                            interest_dd = interest_dd.find_next_sibling('dd')
                    areas_of_interest_text = ', '.join(areas_of_interest) if areas_of_interest else "N/A"
            course_data.append({
                'Title': title,
                'Type': course_type_text,
                'Credits': credits_text,
                'Time': course_time,
                'Instructors': instructor_text,
                'Link': course_href,
                'Prerequisite': prerequisite,
                'Exam Type': exam_type,
                'Description': description,
                'Extra Note': extra_note,
                'Room': room,
                'Areas of Interest': areas_of_interest_text
            })

for page_number in range(1, 14):
    url = f"https://hls.harvard.edu/courses/?page={page_number}"
    print(f"Scraping page {page_number}: {url}")
    scrape_page(url)

driver.quit()

csv_file = 'courses_data_all_pages.csv'

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Title', 'Type', 'Credits', 'Time', 'Instructors', 'Link', 'Prerequisite', 'Exam Type', 'Description', 'Extra Note', 'Room', 'Areas of Interest'])
    writer.writeheader()
    writer.writerows(course_data)

print(f"Data has been saved to {csv_file}")

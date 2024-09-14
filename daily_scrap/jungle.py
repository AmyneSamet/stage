from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import requests
import time

def get_links(keyword="data engineer"):
    links=[]
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    try:
        url = f'https://www.welcometothejungle.com/fr/jobs?&query={keyword}&sortBy=mostRecent'
        driver.get(url)
    
        time.sleep(5)
        nb_page = int(driver.find_elements(By.CLASS_NAME, 'jCRLMV')[-2].text)
        for page in range(nb_page):
            items = driver.find_elements(By.CLASS_NAME, 'ais-Hits-list-item')
            
            stop_outer_loop = False  # Flag to break the outer loop
            
            for item in items:
                links.append(item.find_element(By.CLASS_NAME, 'iPeVkS').get_attribute("href"))
                try:
                    date_str = item.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

                    if datetime.now() - date > timedelta(days=7):
                        stop_outer_loop = True
                        break
                except:
                    pass
            
            if stop_outer_loop:
                break
        
        driver.find_elements(By.CSS_SELECTOR, 'a.sc-IqJVf.evElzU')[-1].click()
        time.sleep(5)
    except:
        print("Error Keyword ..") 
    
    driver.quit()
    return links

def get_data(keyword="data engineer"):
    List_job = []
    links = get_links(keyword)

    print(keyword, 'Job extraction ...')
    
    for i in range(len(links)):
        job = {}
        resp = requests.get(links[i])
        soup = BeautifulSoup(resp.text,'html')

        try:
            job['Job_Link'] = links[i]
        except:
            job['Job_Link'] = None

        try: 
            ul = soup.find('div',{'class':'fhzEMX'}).find_all('ul')
            job_text = ''
            for li in ul:
                job_text += ' '+li.text
            if job_text=='':
                job_text = soup.find('div',{'class':'kqgROr'}).text
            job["Job_txt"] = job_text
        except:
            job["Job_txt"] = None

        try:
            job["company"] = soup.find('span',{'class':'sc-gvZAcH lpuzVS wui-text'}).text.strip()
        except:
            job["company"] = None

        try:
            job["job_title"] = soup.find('h2', {'class':"sc-gvZAcH lodDwl wui-text"}).text.strip()
        except:
            job["job_title"] = None
        
        try:
            job_villes = soup.find_all('div',{'class':'sc-bOhtcR eDrxLt'})[1].find_all('span',{'class':'dhOyPm'})
            job_ville=''
            for ville in job_villes:
                job_ville += ville.text.strip()
            
            job["Location"] = job_ville
        except:
            job["Location"] = None

        try:
          job["job_type"] = soup.find_all('div',{'class':'sc-bOhtcR eDrxLt'})[0].text
        except:
            job["job_type"] = None

        try:
            date = soup.find('time').get('datetime')
            dt_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

            date = dt_obj.date().isoformat()
            job["job_date"] = date
        except:
            job["job_date"] = None
        
        
        List_job.append(job)
        if i%30==0:
            print(i,'Jobs read')
    return pd.DataFrame(List_job)
def get_datas(Keywords):
    data = pd.DataFrame()
    for key in Keywords:
        df = get_data(key)
        data = pd.concat([data,df], axis=0)
    print('Done')
    
    return data

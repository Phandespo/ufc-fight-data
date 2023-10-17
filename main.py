from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
import csv

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=chrome_options)

# Get total number of ufc events
num_url = 'https://www.ufc.com/events#events-list-past'
driver.get(num_url)
num_raw = driver.find_element(by='xpath', value='//*[@id="events-list-past"]/div/div/div[1]/div[2]').text
num_events = int(num_raw.split(' ')[0])
num_events = 35

# Begin scraping at UFC 1's webpage
first_card = 'https://www.ufc.com/event/ufc-1'
driver.get(first_card)

# Set up csv file
fields = ['Red Corner', 'Blue Corner', 'Weight Class', 'Title Fight', 'Result', 'Round', 'Time', 'Method', 
          'Red Corner Bonus Award', 'Blue Corner Bonus Award', 'Red Corner Country', 'Blue Corner Country', 
          'Red Corner Odds', 'Blue Corner Odds']
with open('fight_data.csv', mode='w', newline='', encoding='utf-8') as data:
    fight_data = csv.DictWriter(data, fieldnames=fields)
    fight_data.writeheader()

    # Get each event's data and move on to next one
    for event in range(num_events):
        if event < 34:
            card = ['"block-mainpagecontent"]/div/div[4]/div/div/div[1']
        else: # UFC 30 begins separating evens by main card, prelims, and early prelims
            card = ['"main-card"', '"prelims-card"', '"early-prelims"']

        for section in card:
            for index in range(len(driver.find_elements(by='xpath', value=f'//*[@id={section}]/div/section/ul/li'))):
                red_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[2]/div[5]/div[1]'
                red = driver.find_element(by='xpath', value=red_path).text

                blue_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[2]/div[5]/div[3]'
                blue = driver.find_element(by='xpath', value=blue_path).text

                weight_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[2]/div[1]/div[2]'
                weight = driver.find_element(by='xpath', value=weight_path).text.replace(' BOUT', '')
                if weight == '':
                    weight = 'UNLIMITED'
                    title = 'NO TITLE'
                elif 'INTERIM' in weight:
                    weight = weight.replace(' INTERIM TITLE', '')
                    title = 'INTERIM TITLE'
                elif 'TITLE' in weight:
                    weight = weight.replace(' TITLE', '')
                    title = 'TITLE'
                else:
                    title = 'NO TITLE'

                red_result = driver.find_element(by='xpath', value=f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[1]/div/div/div/div').text
                blue_result = driver.find_element(by='xpath', value=f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[3]/div/div/div/div').text
                if red_result == 'WIN':
                    result = f'WINNER: {red}'
                elif blue_result == 'WIN':
                    result = f'WINNER: {blue}'
                elif red_result == '' and blue_result == '':
                    result = 'NO CONTEST'
                else:
                    result = 'DRAW'

                round_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[2]/div[6]/div[1]/div[2]'
                round = driver.find_element(by='xpath', value=round_path).text

                time_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[2]/div[6]/div[2]/div[2]'
                time = driver.find_element(by='xpath', value=time_path).text
                if len(time) > 4 and time[-5] != '0':
                    time = time[-5:]
                elif len(time) > 4:
                    time = time[-4:]

                method_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[2]/div[6]/div[3]/div[2]'
                method = driver.find_element(by='xpath', value=method_path).text
                
                bonus_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[2]/div[2]/div[4]/div'
                try:
                    bonus = driver.find_element(by='xpath', value=bonus_path).text
                    if bonus == 'FIGHT OF THE NIGHT':
                        red_bonus = bonus
                        blue_bonus = bonus
                    if bonus == 'PERFORMANCE OF THE NIGHT':
                        if result == f'WINNER: {red}':
                            red_bonus = bonus
                            blue_bonus = '-'
                        else:
                            red_bonus = '-'
                            blue_bonus = bonus
                except NoSuchElementException:
                    red_bonus = '-'
                    blue_bonus = '-'
        
                red_country_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[4]/div[1]/div'
                red_country = driver.find_element(by='xpath', value=red_country_path).text
                if red_country == '':
                    red_country = '-'

                blue_country_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[4]/div[3]/div'
                blue_country = driver.find_element(by='xpath', value=blue_country_path).text
                if blue_country == '':
                    blue_country = '-'

                red_odds_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[4]/div[2]/span[1]/span'
                red_odds = driver.find_element(by='xpath', value=red_odds_path).text

                blue_odds_path = f'//*[@id={section}]/div/section/ul/li[{index}+1]/div/div/div/div[4]/div[2]/span[3]/span'
                blue_odds = driver.find_element(by='xpath', value=blue_odds_path).text

                fight_data.writerow({
                    'Red Corner': red,
                    'Blue Corner': blue,
                    'Weight Class': weight,
                    'Title Fight': title,
                    'Result': result,
                    'Round': round,
                    'Time': time,
                    'Method': method,
                    'Red Corner Bonus Award': red_bonus,
                    'Blue Corner Bonus Award': blue_bonus,
                    'Red Corner Country': red_country,
                    'Blue Corner Country': blue_country,
                    'Red Corner Odds': red_odds,
                    'Blue Corner Odds': blue_odds,
                })

        try:
            next_event = driver.find_element(by='xpath', value='//*[@id="block-mainpagecontent"]/div/div[1]/div[2]/div/span[2]/a')
        except NoSuchElementException:
            next_event = driver.find_element(by='xpath', value='//*[@id="block-mainpagecontent"]/div/div[1]/div[2]/div/span/a')                                        
        ActionChains(driver).scroll_to_element(next_event).perform()
        next_event.click()

driver.quit()

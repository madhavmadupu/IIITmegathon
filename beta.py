import streamlit as st
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import json
import openai
from dotenv import load_dotenv


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

def get_githubData(soup):
    github_contributions = ""
    github_name = soup.find('span', class_='p-nickname').get_text(strip=True)
    socialLinks_uncleaned = soup.find_all(class_='Link--primary')
    github_links=[]
    for link_uncleaned in socialLinks_uncleaned:
        link = link_uncleaned.get('href')
        github_links.append(link)
    github_repos_uncleaned = soup.find_all(class_='repo')
    github_repos=[]
    if github_repos_uncleaned!=[]:
        for repo_uncleaned in github_repos_uncleaned:
            repo_cleaned = repo_uncleaned.text
            github_repos.append(repo_cleaned.strip())
    else:
        github_repos.append((soup.find(class_='blankslate-heading')).text)
    contributionsThisYear_uncleaned = soup.find_all(class_='f4 text-normal mb-2')
    github_contributions = " ".join(contributionsThisYear_uncleaned[0].text.strip().split())
    return [github_name, github_links, github_contributions, github_repos]

def get_linkedinData(soup):
    linkedin_name=soup.find(class_='top-card-layout__title').text.strip()
    linkedin_location=soup.find(class_='top-card__subline-item')
    if linkedin_location!=None:
        linkedin_location=soup.find(class_='top-card__subline-item').text.strip()
    else:
        linkedin_location="No data found"
    linkedin_likes=[]
    linkedin_likes_uncleaned=soup.find_all('span', class_='sr-only')
    for linkedin_likes_uncleaned_span in linkedin_likes_uncleaned:
        linkedin_likes.append(linkedin_likes_uncleaned_span.text.strip())
    linkedin_about_raw=soup.find(class_='inline-show-more-text')
    if linkedin_about_raw!=None:
        linkedin_about=linkedin_about_raw.text.strip()
    else:
        linkedin_about="No data found"
    linkedin_experience=[]
    linkedin_experience_list_uncleaned=(soup.find_all('ul', class_='experience__list'))
    try: 
        linkedin_experience_list_uncleaned_data=linkedin_experience_list_uncleaned[0]
        if linkedin_experience_list_uncleaned_data!=None:
            for experience_item in linkedin_experience_list_uncleaned_data.find_all(class_='profile-section-card'):
                job_title = experience_item.find(class_='profile-section-card__title')
                company_name = experience_item.find(class_='profile-section-card__subtitle')
                duration = experience_item.find(class_='date-range')
                location = experience_item.find(class_='experience-item__location')
                
                # Extract and concatenate the description for the position
                description = ""
                description_container = experience_item.find(class_='show-more-less-text')
                if description_container:
                    for item in description_container.stripped_strings:
                        description += item + '\n'
                
                linkedin_experience.append({
                    'job_title': job_title.get_text(strip=True) if job_title!=None else "No data found",
                    'company_name': company_name.get_text(strip=True) if company_name!=None else "No data found",
                    'duration': duration.get_text(strip=True) if duration!=None else "No data found",
                    'location': location.get_text(strip=True) if location!=None else "No data found",
                    'description': description if description!=None else "No data found"
                })
    except IndexError as e:
        linkedin_experience.append("No data found")
    return [linkedin_name, linkedin_location, linkedin_likes, linkedin_about, linkedin_experience]

def get_instagramData(soup):
    instagram_name=soup.find(class_='x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye x1ms8i2q xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj').text.strip()
    instagram_social_predata=soup.find_all(class_='_acan _acao _acat _aj1-')
    instagram_social_data=[]
    for instagram_social_predata_item in instagram_social_predata:
        instagram_social_data.append(instagram_social_predata_item.text.strip())
    instagram_description=soup.find(class_='x7a106z x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x78zum5 xdt5ytf x2lah0s xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x11njtxf xwonja6 x1dyjupv x1onnzdu xwrz0qm xgmu61r x1nbz2ho xbjc6do').text.strip()
    return [instagram_name, instagram_social_data, instagram_description]

def get_leetcodeData(soup):
    checkbox = driver.find_element(By.CLASS_NAME, "ctp-checkbox-label")
    checkbox.click()
    leetcode_communityStatus=soup.find(class_='mt-4 flex flex-col space-y-4')
    leetcode_activity_raw=soup.find(class_='lc-md:flex-row lc-md:items-center lc-md:space-y-0 flex flex-col flex-wrap space-y-2')
    leetcode_activity=[]
    leetcode_activityYearlySubmissions=leetcode_activity_raw.find(class_='flex flex-1 items-center')
    leetcode_activityStreak=leetcode_activity_raw.find(class_='flex items-center text-xs')
    leetcode_activity.append(leetcode_activityYearlySubmissions.text.strip())
    leetcode_activity.append(leetcode_activityStreak.text.strip())
    return [leetcode_communityStatus, leetcode_activity]

dataPoints = []

st.title("Social Check 🦜")

jobRole=st.text_input("Role")

st.subheader("Enter the Social's of candid:")
col1, col2 = st.columns(2)
with col1:
    url1 = st.text_input("GitHub")
    url2 = st.text_input("LinkedIn")
with col2:
    url3 = st.text_input("Instagram")
    url4 = st.text_input("Leetcode (Beta)")

dataPoints = [url1, url2, url3, url4]

st.write("")
with st.container():
    if st.button("Predict"):
        print(dataPoints)
        if dataPoints== []:
            st.text("Provide atleast a social to predict on.")
        else:
            st.text("Gathering and processing data... This might take 15-20 seconds")
            data = {
            "github_data": None,
            "linkedin_data": None,
            "instagram_data": None,
            "leetcode_data": None
            }

            for dataPoint in dataPoints:
                if dataPoint!="":
                    driver = webdriver.Chrome(options=chrome_options)
                    try:
                        driver.execute_script("window.open('{}', '_blank');".format(dataPoint))
                        driver.switch_to.window(driver.window_handles[1])
                        time.sleep(5)
                        page_source = driver.page_source
                        soup = BeautifulSoup(page_source, 'html.parser')

                        if "github" in dataPoint:
                            data["github_data"] = get_githubData(soup)

                        elif "linkedin" in dataPoint:
                            data["linkedin_data"] = get_linkedinData(soup)

                        elif "instagram" in dataPoint:
                            data["instagram_data"] = get_instagramData(soup)

                        elif "leetcode" in dataPoint:
                            pass
                            # data["leetcode_data"] = get_leetcodeData(soup)

                        with open("scraped_data.json", "w") as json_file:
                            json.dump(data, json_file)

                    finally:
                        driver.quit()
            load_dotenv()
            openai.api_key = os.getenv("OPENAI_API_KEY")
            completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"You need to give a rating or probability between 0 to 1 weather the candidate is fit for the {jobRole} based on the data that i will collect from his social footprint and give it to you. Consider this as a psychometric test. You should just give the predicted floating point and a very short description on why you think of it."},
                {"role": "user", "content": f"The collected data is here {data}"}
            ]
            )
            result = completion['choices'][0]['message']['content']
            st.text("Data processing complete.")
            st.subheader(f"Result: {result}")

            st.subheader("Social Footprint Collected🔽")
            if data[github_data]:
                st.subheader("GitHub Data:")
                st.write("Name:", data[github_data[0]])
                st.write("Links:", data[github_data[1]])
                st.write("Contributions:", data[github_data[2]])
                st.write("Repos:", data[github_data[3]])

            if data[linkedin_data]:
                st.subheader("LinkedIn Data:")
                st.write("Name:", data[linkedin_data[0]])
                st.write("Location:", data[linkedin_data[1]])
                st.write("Likes:", data[linkedin_data[2]])
                st.write("About:", data[linkedin_data[3]])
                st.write("Experience:", data[linkedin_data[4]])

            if data[instagram_data]:
                st.subheader("Instagram Data:")
                st.write("Name:", data[instagram_data[0]])
                st.write("Social Data:", data[instagram_data[1]])
                st.write("Description:", data[instagram_data[2]])

            if data[leetcode_data]:
                st.subheader("LeetCode Data:")
                st.write("Community Status:", data[leetcode_data[0]])
                st.write("Activity:", data[leetcode_data[1]])


    if st.button("Stop", key="stop_button"):
        st.write('<style>div[data-baseweb="button"] button {background-color: red;}</style>', unsafe_allow_html=True)
        st.text("Closing the app...")
        st.stop()
del os.environ['PYGAME_HIDE_SUPPORT_PROMPT']
del os.environ['SDL_AUDIODRIVER']
del os.environ['TF_CPP_MIN_LOG_LEVEL']
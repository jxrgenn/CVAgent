from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dataclasses import dataclass
import time
import sys
import os

# Optional: force UTF-8 console output for logs
sys.stdout.reconfigure(encoding='utf-8')

# Create Flask app
app = Flask(__name__)

# Your credentials (be cautious with exposing this in production)
EMAIL = "danociotr1@gmail.com"
PASSWORD = "jurgen1964"

# ChromeDriver path
CHROMEDRIVER_PATH = r"C:\Users\Maçoku\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# Constants
VERIFY_LOGIN_ID = "global-nav__primary-link"
REMEMBER_PROMPT = 'remember-me-prompt__form-primary'
WAIT_FOR_ELEMENT_TIMEOUT = 5

@dataclass
class Experience:
    position_title: str = None
    institution_name: str = None
    from_date: str = None
    to_date: str = None
    duration: str = None
    location: str = None
    description: str = None
    linkedin_url: str = None

@dataclass
class Education:
    degree: str = None
    institution_name: str = None
    from_date: str = None
    to_date: str = None
    description: str = None
    linkedin_url: str = None

@dataclass
class Interest:
    title: str = None

@dataclass
class Accomplishment:
    category: str = None
    title: str = None

@dataclass
class Contact:
    name: str = None
    occupation: str = None
    url: str = None

class LinkedInScraper:
    def __init__(self, driver):
        self.driver = driver
        self.WAIT_FOR_ELEMENT_TIMEOUT = WAIT_FOR_ELEMENT_TIMEOUT

    def wait(self, duration):
        print(f"⏳ Waiting for {duration} seconds...")
        time.sleep(int(duration))

    def focus(self):
        print("🔍 Focusing window...")
        try:
            self.driver.execute_script('alert("Focus window")')
            self.driver.switch_to.alert.accept()
            print("✅ Window focused successfully")
        except Exception as e:
            print(f"⚠️ Focus failed: {e}")

    def wait_for_element_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        print(f"🔍 Waiting for element: {by}={name}")
        base = base or self.driver
        try:
            element = WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((by, name))
            )
            print(f"✅ Element found: {by}={name}")
            return element
        except TimeoutException:
            print(f"❌ Timeout waiting for element: {by}={name}")
            return None
        except Exception as e:
            print(f"❌ Error waiting for element {by}={name}: {e}")
            return None

    def is_signed_in(self):
        print("🔍 Checking if signed in...")
        try:
            WebDriverWait(self.driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, VERIFY_LOGIN_ID))
            )
            self.driver.find_element(By.CLASS_NAME, VERIFY_LOGIN_ID)
            print("✅ Successfully signed in")
            return True
        except Exception as e:
            print(f"❌ Not signed in: {e}")
            return False

    def scroll_to_half(self):
        print("📜 Scrolling to half of page...")
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )

    def scroll_to_bottom(self):
        print("📜 Scrolling to bottom of page...")
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    def get_name_and_location(self):
        print("🔍 Getting name and location...")
        try:
            print("🔍 Looking for top panel...")
            top_panel = self.driver.find_element(By.XPATH, "//*[@class='mt2 relative']")
            print("✅ Found top panel")
            
            print("🔍 Looking for name...")
            name = top_panel.find_element(By.TAG_NAME, "h1").text
            print(f"✅ Found name: {name}")
            
            print("🔍 Looking for location...")
            location = top_panel.find_element(By.XPATH, "//*[@class='text-body-small inline t-black--light break-words']").text
            print(f"✅ Found location: {location}")
            
            return name, location
        except NoSuchElementException as e:
            print(f"❌ Could not find name/location elements: {e}")
            return None, None
        except Exception as e:
            print(f"❌ Error getting name and location: {e}")
            return None, None

    def get_about(self):
        print("🔍 Getting about section...")
        try:
            print("🔍 Looking for about section...")
            about = self.driver.find_element(By.ID, "about").find_element(By.XPATH, "..").find_element(By.CLASS_NAME, "display-flex").text
            print(f"✅ Found about section: {about[:100]}...")
            return about
        except NoSuchElementException:
            print("⚠️ About section not found")
            return None
        except Exception as e:
            print(f"❌ Error getting about section: {e}")
            return None

    def is_open_to_work(self):
        print("🔍 Checking if open to work...")
        try:
            result = "#OPEN_TO_WORK" in self.driver.find_element(By.CLASS_NAME, "pv-top-card-profile-picture").find_element(By.TAG_NAME, "img").get_attribute("title")
            print(f"✅ Open to work status: {result}")
            return result
        except Exception as e:
            print(f"⚠️ Could not determine open to work status: {e}")
            return False

    def get_experiences(self, profile_url):
        print("🔍 Getting experiences...")
        experiences = []
        try:
            # Construct experience URL
            if profile_url.endswith('/'):
                url = profile_url + "details/experience"
            else:
                url = profile_url + "/details/experience"
            print(f"🔍 Navigating to experience URL: {url}")
            
            self.driver.get(url)
            print("✅ Navigated to experience page")
            
            self.focus()
            print("🔍 Waiting for main element...")
            main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
            if not main:
                print("❌ Could not find main element")
                return experiences
                
            print("🔍 Scrolling page...")
            self.scroll_to_half()
            self.scroll_to_bottom()
            
            print("🔍 Looking for experience list container...")
            main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
            if not main_list:
                print("❌ Could not find experience list container")
                return experiences
                
            print("🔍 Finding experience items...")
            experience_items = main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item")
            print(f"✅ Found {len(experience_items)} experience items")
            
            for i, position in enumerate(experience_items):
                print(f"🔍 Processing experience item {i+1}/{len(experience_items)}")
                try:
                    position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                    
                    # Fix: Handle case where more than 2 elements are returned
                    elements = position.find_elements(By.XPATH, "*")
                    print(f"🔍 Found {len(elements)} elements in position")
                    if len(elements) < 2:
                        print("⚠️ Skipping - not enough elements")
                        continue  # Skip if we don't have enough elements
                        
                    company_logo_elem = elements[0]
                    position_details = elements[1]

                    # company elem
                    try:
                        company_linkedin_url = company_logo_elem.find_element(By.XPATH, "*").get_attribute("href")
                        if not company_linkedin_url:
                            print("⚠️ No company URL found")
                            continue
                        print(f"🔍 Company URL: {company_linkedin_url}")
                    except NoSuchElementException:
                        print("⚠️ Could not find company URL")
                        continue

                    # position details
                    position_details_list = position_details.find_elements(By.XPATH, "*")
                    position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                    position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                    
                    if not position_summary_details:
                        print("⚠️ No position summary details")
                        continue
                        
                    outer_positions = position_summary_details.find_element(By.XPATH, "*").find_elements(By.XPATH, "*")
                    print(f"🔍 Found {len(outer_positions)} outer positions")

                    if len(outer_positions) == 4:
                        position_title = outer_positions[0].find_element(By.TAG_NAME, "span").text
                        company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                        work_times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                        location = outer_positions[3].find_element(By.TAG_NAME, "span").text
                    elif len(outer_positions) == 3:
                        if "·" in outer_positions[2].text:
                            position_title = outer_positions[0].find_element(By.TAG_NAME, "span").text
                            company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                            work_times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                            location = ""
                        else:
                            position_title = ""
                            company = outer_positions[0].find_element(By.TAG_NAME, "span").text
                            work_times = outer_positions[1].find_element(By.TAG_NAME, "span").text
                            location = outer_positions[2].find_element(By.TAG_NAME, "span").text
                    else:
                        position_title = ""
                        company = outer_positions[0].find_element(By.TAG_NAME, "span").text if outer_positions else ""
                        work_times = outer_positions[1].find_element(By.TAG_NAME, "span").text if len(outer_positions) > 1 else ""
                        location = ""

                    print(f"🔍 Extracted: Title='{position_title}', Company='{company}', Times='{work_times}', Location='{location}'")

                    # Safely extract times and duration
                    if work_times:
                        parts = work_times.split("·")
                        times = parts[0].strip() if parts else ""
                        duration = parts[1].strip() if len(parts) > 1 else None
                    else:
                        times = ""
                        duration = None

                    from_date = " ".join(times.split(" ")[:2]) if times else ""
                    to_date = " ".join(times.split(" ")[3:]) if times and len(times.split(" ")) > 3 else ""
                    
                    description = ""
                    if position_summary_text and any(element.get_attribute("class") == "pvs-list__container" for element in position_summary_text.find_elements(By.XPATH, "*")):
                        try:
                            inner_positions = (position_summary_text.find_element(By.CLASS_NAME, "pvs-list__container")
                                            .find_element(By.XPATH, "*").find_element(By.XPATH, "*").find_element(By.XPATH, "*")
                                            .find_elements(By.CLASS_NAME, "pvs-list__paged-list-item"))
                        except NoSuchElementException:
                            inner_positions = []
                    else:
                        inner_positions = []
                    
                    if len(inner_positions) > 1:
                        descriptions = inner_positions
                        for description_elem in descriptions:
                            try:
                                res = description_elem.find_element(By.TAG_NAME, "a").find_elements(By.XPATH, "*")
                                position_title_elem = res[0] if len(res) > 0 else None
                                work_times_elem = res[1] if len(res) > 1 else None
                                location_elem = res[2] if len(res) > 2 else None

                                location = location_elem.find_element(By.XPATH, "*").text if location_elem else None
                                position_title = position_title_elem.find_element(By.XPATH, "*").find_element(By.TAG_NAME, "*").text if position_title_elem else ""
                                
                                if work_times_elem:
                                    work_times = work_times_elem.find_element(By.XPATH, "*").text
                                    if work_times and "-" in work_times:
                                        split_times = work_times.split(" ")
                                        dash_index = split_times.index("-") if "-" in split_times else -1
                                        
                                        if dash_index > 0:
                                            from_date = split_times[dash_index-1]
                                        if dash_index < len(split_times) - 1:
                                            to_date = split_times[-1]
                                
                                description = description_elem.text
                            except (NoSuchElementException, IndexError):
                                continue
                    else:
                        description = position_summary_text.text if position_summary_text else ""

                    experience = Experience(
                        position_title=position_title,
                        institution_name=company,
                        from_date=from_date,
                        to_date=to_date,
                        duration=duration,
                        location=location,
                        description=description,
                        linkedin_url=company_linkedin_url
                    )
                    experiences.append(experience)
                    print(f"✅ Added experience: {position_title} at {company}")
                    
                except (NoSuchElementException, IndexError) as e:
                    print(f"⚠️ Error processing experience item {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error getting experiences: {e}")
            
        print(f"✅ Total experiences extracted: {len(experiences)}")
        return experiences

    def get_educations(self, profile_url):
        print("🔍 Getting educations...")
        educations = []
        try:
            # Construct education URL
            if profile_url.endswith('/'):
                url = profile_url + "details/education"
            else:
                url = profile_url + "/details/education"
            print(f"🔍 Navigating to education URL: {url}")
            
            self.driver.get(url)
            print("✅ Navigated to education page")
            
            self.focus()
            print("🔍 Waiting for main element...")
            main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
            if not main:
                print("❌ Could not find main element")
                return educations
                
            print("🔍 Scrolling page...")
            self.scroll_to_half()
            self.scroll_to_bottom()
            
            print("🔍 Looking for education list container...")
            main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
            if not main_list:
                print("❌ Could not find education list container")
                return educations
                
            print("🔍 Finding education items...")
            education_items = main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item")
            print(f"✅ Found {len(education_items)} education items")
            
            for i, position in enumerate(education_items):
                print(f"🔍 Processing education item {i+1}/{len(education_items)}")
                try:
                    position = position.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
                    
                    elements = position.find_elements(By.XPATH, "*")
                    print(f"🔍 Found {len(elements)} elements in position")
                    if len(elements) < 2:
                        print("⚠️ Skipping - not enough elements")
                        continue
                        
                    institution_logo_elem = elements[0]
                    position_details = elements[1]

                    # institution elem
                    try:
                        institution_linkedin_url = institution_logo_elem.find_element(By.XPATH, "*").get_attribute("href")
                        if not institution_linkedin_url:
                            print("⚠️ No institution URL found")
                            continue
                        print(f"🔍 Institution URL: {institution_linkedin_url}")
                    except NoSuchElementException:
                        print("⚠️ Could not find institution URL")
                        continue

                    # position details
                    position_details_list = position_details.find_elements(By.XPATH, "*")
                    position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                    position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                    
                    if not position_summary_details:
                        print("⚠️ No position summary details")
                        continue
                        
                    outer_positions = position_summary_details.find_element(By.XPATH, "*").find_elements(By.XPATH, "*")

                    institution_name = outer_positions[0].find_element(By.TAG_NAME, "span").text if outer_positions else ""
                    degree = outer_positions[1].find_element(By.TAG_NAME, "span").text if len(outer_positions) > 1 else None

                    print(f"🔍 Extracted: Institution='{institution_name}', Degree='{degree}'")

                    from_date = None
                    to_date = None
                    
                    if len(outer_positions) > 2:
                        try:
                            times = outer_positions[2].find_element(By.TAG_NAME, "span").text

                            if times and "-" in times:
                                split_times = times.split(" ")
                                dash_index = split_times.index("-") if "-" in split_times else -1
                                
                                if dash_index > 0:
                                    from_date = split_times[dash_index-1]
                                if dash_index < len(split_times) - 1:
                                    to_date = split_times[-1]
                        except (NoSuchElementException, ValueError):
                            from_date = None
                            to_date = None

                    description = position_summary_text.text if position_summary_text else ""

                    education = Education(
                        from_date=from_date,
                        to_date=to_date,
                        description=description,
                        degree=degree,
                        institution_name=institution_name,
                        linkedin_url=institution_linkedin_url
                    )
                    educations.append(education)
                    print(f"✅ Added education: {degree} at {institution_name}")
                    
                except (NoSuchElementException, IndexError) as e:
                    print(f"⚠️ Error processing education item {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error getting educations: {e}")
            
        print(f"✅ Total educations extracted: {len(educations)}")
        return educations

    def get_interests(self):
        print("🔍 Getting interests...")
        interests = []
        try:
            _ = WebDriverWait(self.driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']",
                ))
            )
            interestContainer = self.driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']"
            )
            for interestElement in interestContainer.find_elements(By.XPATH,
                "//*[@class='pv-interest-entity pv-profile-section__card-item ember-view']"
            ):
                interest = Interest(
                    interestElement.find_element(By.TAG_NAME, "h3").text.strip()
                )
                interests.append(interest)
        except:
            pass
        return interests

    def get_accomplishments(self):
        print("🔍 Getting accomplishments...")
        accomplishments = []
        try:
            _ = WebDriverWait(self.driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']",
                ))
            )
            acc = self.driver.find_element(By.XPATH,
                "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']"
            )
            for block in acc.find_elements(By.XPATH,
                "//div[@class='pv-accomplishments-block__content break-words']"
            ):
                category = block.find_element(By.TAG_NAME, "h3")
                for title in block.find_element(By.TAG_NAME,
                    "ul"
                ).find_elements(By.TAG_NAME, "li"):
                    accomplishment = Accomplishment(category.text, title.text)
                    accomplishments.append(accomplishment)
        except:
            pass
        return accomplishments

    def get_contacts(self):
        print("🔍 Getting contacts...")
        contacts = []
        try:
            self.driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            _ = WebDriverWait(self.driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mn-connections"))
            )
            connections = self.driver.find_element(By.CLASS_NAME, "mn-connections")
            if connections is not None:
                for conn in connections.find_elements(By.CLASS_NAME, "mn-connection-card"):
                    anchor = conn.find_element(By.CLASS_NAME, "mn-connection-card__link")
                    url = anchor.get_attribute("href")
                    name = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME, "mn-connection-card__name").text.strip()
                    occupation = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME, "mn-connection-card__occupation").text.strip()

                    contact = Contact(name=name, occupation=occupation, url=url)
                    contacts.append(contact)
        except:
            pass
        return contacts

    def scrape_profile(self, profile_url):
        print(f"🚀 Starting to scrape profile: {profile_url}")
        
        if not self.is_signed_in():
            print("❌ You are not logged in!")
            return None

        print("🔍 Navigating to profile URL...")
        self.driver.get(profile_url)
        print(f"✅ Current URL: {self.driver.current_url}")
        
        self.focus()
        self.wait(5)

        # Get name and location
        print("🔍 Getting name and location...")
        name, location = self.get_name_and_location()
        print(f"✅ Name: {name}, Location: {location}")
        
        open_to_work = self.is_open_to_work()

        # Get about
        print("🔍 Getting about section...")
        about = self.get_about()
        print(f"✅ About section length: {len(about) if about else 0}")
        
        print("🔍 Scrolling page...")
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        # Get experiences
        print("🔍 Getting experiences...")
        experiences = self.get_experiences(profile_url)

        # Get educations
        print("🔍 Getting educations...")
        educations = self.get_educations(profile_url)

        # Go back to main profile
        print("🔍 Returning to main profile...")
        self.driver.get(profile_url)
        print(f"✅ Back to profile URL: {self.driver.current_url}")

        # Get interests
        print("🔍 Getting interests...")
        interests = self.get_interests()

        # Get accomplishments
        print("🔍 Getting accomplishments...")
        accomplishments = self.get_accomplishments()

        # Get contacts (optional - requires additional navigation)
        # contacts = self.get_contacts()

        result = {
            "name": name,
            "location": location,
            "about": about,
            "open_to_work": open_to_work,
            "experiences": experiences,
            "educations": educations,
            "interests": interests,
            "accomplishments": accomplishments,
            # "contacts": contacts
        }
        
        print(f"✅ Scraping completed. Results: {len(experiences)} experiences, {len(educations)} educations, {len(interests)} interests, {len(accomplishments)} accomplishments")
        return result

def login(driver, email, password, timeout=10):
    print("🔍 Starting login process...")
    driver.get("https://www.linkedin.com/login")
    print("✅ Navigated to login page")
    
    print("🔍 Waiting for username field...")
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    print("✅ Username field found")
  
    print("🔍 Entering email...")
    email_elem = driver.find_element(By.ID, "username")
    email_elem.send_keys(email)
    print("✅ Email entered")
  
    print("🔍 Entering password...")
    password_elem = driver.find_element(By.ID, "password")
    password_elem.send_keys(password)
    print("✅ Password entered")
    
    print("🔍 Submitting login form...")
    password_elem.submit()
    print("✅ Login form submitted")
  
    if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
        print("🔍 Handling remember prompt...")
        remember = driver.find_element(By.ID, REMEMBER_PROMPT)
        if remember:
            remember.submit()
            print("✅ Remember prompt handled")
  
    print("🔍 Waiting for login verification...")
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, VERIFY_LOGIN_ID)))
    print("✅ Login successful!")

@app.route('/scrape', methods=['POST'])
def scrape_profile():
    print("🚀 Received scrape request")
    
    # Try getting URL from JSON or form field
    json_data = request.get_json(silent=True)
    profile_url = None

    if json_data and "url" in json_data:
        profile_url = json_data["url"]
        print(f"✅ Got URL from JSON: {profile_url}")
    elif "url" in request.form:
        profile_url = request.form["url"]
        print(f"✅ Got URL from form: {profile_url}")
    else:
        print("❌ No URL found in request body")
        return jsonify({"error": "No LinkedIn URL provided."}), 400

    print("✅ Got URL:", profile_url)

    # Check if ChromeDriver exists
    if not os.path.exists(CHROMEDRIVER_PATH):
        print(f"❌ ChromeDriver not found at: {CHROMEDRIVER_PATH}")
        return jsonify({"error": f"ChromeDriver not found at: {CHROMEDRIVER_PATH}"}), 500
    else:
        print(f"✅ ChromeDriver found at: {CHROMEDRIVER_PATH}")

    # Set up Selenium
    print("🔧 Setting up Chrome driver...")
    
    # Try multiple approaches for ChromeDriver
    driver = None
    
    # Approach 1: Try with explicit path
    try:
        service = Service(CHROMEDRIVER_PATH)
        options = Options()
        # options.add_argument('--headless')  # Temporarily disabled for debugging
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--remote-debugging-port=9222')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome driver setup complete (Approach 1)")
    except Exception as e:
        print(f"❌ Approach 1 failed: {e}")
        
        # Approach 2: Try without explicit service
        try:
            options = Options()
            # options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--remote-debugging-port=9223')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            driver = webdriver.Chrome(options=options)
            print("✅ Chrome driver setup complete (Approach 2)")
        except Exception as e2:
            print(f"❌ Approach 2 failed: {e2}")
            
            # Approach 3: Try with webdriver manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service as ChromeService
                
                service = ChromeService(ChromeDriverManager().install())
                options = Options()
                # options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                
                driver = webdriver.Chrome(service=service, options=options)
                print("✅ Chrome driver setup complete (Approach 3)")
            except Exception as e3:
                print(f"❌ Approach 3 failed: {e3}")
                return jsonify({"error": f"All Chrome driver approaches failed. Last error: {str(e3)}"}), 500
    
    if not driver:
        return jsonify({"error": "Failed to create Chrome driver"}), 500

    try:
        print("🚀 Logging in to LinkedIn...")
        login(driver, EMAIL, PASSWORD)
        print("🔍 Scraping profile...")
        
        scraper = LinkedInScraper(driver)
        profile_data = scraper.scrape_profile(profile_url)
        
        if not profile_data:
            print("❌ Failed to scrape profile")
            return jsonify({"error": "Failed to scrape profile"}), 500

        # Convert dataclasses to dictionaries for JSON serialization
        print("🔧 Converting data to JSON format...")
        serializable_data = {
            "name": profile_data["name"],
            "location": profile_data["location"],
            "about": profile_data["about"],
            "open_to_work": profile_data["open_to_work"],
            "experiences": [],
            "educations": [],
            "interests": [],
            "accomplishments": []
        }

        for exp in profile_data["experiences"]:
            serializable_data["experiences"].append({
                "position_title": exp.position_title,
                "institution_name": exp.institution_name,
                "from_date": exp.from_date,
                "to_date": exp.to_date,
                "duration": exp.duration,
                "location": exp.location,
                "description": exp.description,
                "linkedin_url": exp.linkedin_url
            })

        for edu in profile_data["educations"]:
            serializable_data["educations"].append({
                "degree": edu.degree,
                "institution_name": edu.institution_name,
                "from_date": edu.from_date,
                "to_date": edu.to_date,
                "description": edu.description,
                "linkedin_url": edu.linkedin_url
            })

        for interest in profile_data["interests"]:
            serializable_data["interests"].append({
                "title": interest.title
            })

        for acc in profile_data["accomplishments"]:
            serializable_data["accomplishments"].append({
                "category": acc.category,
                "title": acc.title
            })

        print("✅ Scrape successful")
        return jsonify(serializable_data), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        print("🔧 Closing Chrome driver...")
        driver.quit()
        print("✅ Chrome driver closed")

# Run the app
if __name__ == '__main__':
    print("🚀 Starting LinkedIn Scraper Flask app...")
    app.run(host='0.0.0.0', port=5000) 
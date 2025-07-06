from flask import Flask, request, jsonify
import json
import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import threading
import uuid

sys.stdout.reconfigure(encoding='utf-8')

# --- CONFIG ---
EMAIL = "danociotr1@gmail.com"
PASSWORD = "jurgen1964"
CHROMEDRIVER_PATH = r"C:\\Users\\Maçoku\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
WAIT_FOR_ELEMENT_TIMEOUT = 10
REMEMBER_PROMPT = 'remember-me-prompt__form-primary'
VERIFY_LOGIN_ID = "global-nav__primary-link"

app = Flask(__name__)

# In-memory job store: job_id -> {"status": ..., "result": ...}
jobs = {}

def wait_for_element(driver, by, value, timeout=WAIT_FOR_ELEMENT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        return None

def login_linkedin(driver, email, password, timeout=10):
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
        try:
            remember = driver.find_element(By.ID, REMEMBER_PROMPT)
            if remember:
                remember.submit()
                print("✅ Remember prompt handled")
        except Exception as e:
            print(f"⚠️ Could not handle remember prompt: {e}")
  
    print("🔍 Waiting for login verification...")
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, VERIFY_LOGIN_ID)))
    print("✅ Login successful!")

def search_jobs(driver, keywords, location=None, remote_options=None, seniority=None):
    print("🔍 Navigating to LinkedIn Jobs search results page...")
    # Add location and remote filters if provided
    search_url = f"https://www.linkedin.com/jobs/search?keywords={keywords}"
    if location:
        search_url += f"&location={location}"
    # Add remote filter(s) if present
    if remote_options:
        # LinkedIn uses 'f_WT' param: 1=On-site, 2=Remote, 3=Hybrid
        wt_map = {"on-site": "1", "remote": "2", "hybrid": "3"}
        wt_values = [wt_map[opt] for opt in remote_options if opt in wt_map]
        if wt_values:
            search_url += f"&f_WT={'%2C'.join(wt_values)}"
    if seniority:
        seniority_map = [
            ("Internship", "1"),
            ("Entry level", "2"),
            ("Associate", "3"),
            ("Mid-Senior level", "4"),
            ("Director", "5"),
            ("Executive", "6"),
        ]
        idx = next((i for i, (label, _) in enumerate(seniority_map) if label.strip().lower() == seniority.strip().lower()), None)
        if idx is not None:
            indices = set([idx])
            if idx > 0:
                indices.add(idx - 1)
            if idx < len(seniority_map) - 1:
                indices.add(idx + 1)
            codes = [seniority_map[i][1] for i in sorted(indices)]
            search_url += f"&f_E={','.join(codes)}"
    search_url += "&refresh=true"
    driver.get(search_url)
    print(f"✅ Navigated to: {search_url}")
    time.sleep(3)

def get_occludable_job_ids(driver, max_jobs=5):
    print("⏳ Looking for job items with `data-occludable-job-id`...")
    job_ids = []
    try:
        WebDriverWait(driver, WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//li[@data-occludable-job-id]'))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        job_elements = driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
        print(f"✅ Found {len(job_elements)} jobs with IDs.")
        for li in job_elements:
            job_id = li.get_attribute("data-occludable-job-id")
            if job_id and job_id not in job_ids:
                job_ids.append(job_id)
            if len(job_ids) >= max_jobs:
                break
    except Exception as e:
        print(f"❌ Could not find job list items: {e}")
        return []
    return job_ids

def wait_for_element_to_load(driver, by=By.CLASS_NAME, name="", timeout=WAIT_FOR_ELEMENT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, name))
        )
    except TimeoutException:
        return None

def mouse_click(driver, elem):
    action = webdriver.ActionChains(driver)
    action.move_to_element(elem).perform()

def focus_window(driver):
    driver.execute_script('alert("Focus window")')
    driver.switch_to.alert.accept()

def wait_for_element_with_text(driver, by, value, timeout=15):
    """Wait for an element to exist and have non-empty text."""
    try:
        return WebDriverWait(driver, timeout).until(
            lambda d: (elem := d.find_element(by, value)) and elem.text.strip() != "" and elem
        )
    except TimeoutException:
        return None

def scrape_job_details(driver, job_id, keywords):
    try:
        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
        print(f"🔍 Scraping job details from: {job_url}")
        driver.get(job_url)
        time.sleep(2)
        focus_window(driver)
        job_title = "Unknown"
        company = "Unknown"
        salary = None
        job_description = "Unknown"
        try:
            # Job title
            job_title_elem = wait_for_element_to_load(driver, By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title")
            if job_title_elem:
                job_title = job_title_elem.text.strip()
            # Company name
            company_elem = wait_for_element_to_load(driver, By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name")
            if company_elem:
                company = company_elem.text.strip()
            # Salary/benefits
            try:
                salary_elem = wait_for_element_to_load(driver, By.CLASS_NAME, "jobs-unified-description__salary-main-rail-card")
                if salary_elem:
                    salary = salary_elem.text.strip()
            except Exception:
                salary = None
            # Job description (robust, as before)
            desc_elem = wait_for_element_to_load(driver, By.CLASS_NAME, "jobs-description")
            if desc_elem:
                buttons = desc_elem.find_elements(By.TAG_NAME, "button")
                if buttons:
                    try:
                        driver.execute_script("arguments[0].click();", buttons[0])
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"⚠️ Could not click see more button: {e}")
                job_description = desc_elem.text.strip()
            else:
                print("❌ jobs-description container not found")
        except Exception as e:
            print(f"❌ Could not extract job details: {e}")
        job_data = {
            "company": company,
            "job_title": job_title,
            "salary": salary,
            "job_description": job_description
        }
        print(f"✅ Successfully scraped job: {job_title} at {company}")
        return job_data
    except Exception as e:
        print(f"❌ Error scraping job {job_id}: {e}")
        return {
            'job_id': job_id,
            'error': str(e)
        }

# --- ChromeDriver Setup (copied from LinkedinScraper.py) ---
def get_chrome_driver():
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    import os
    if not os.path.exists(CHROMEDRIVER_PATH):
        raise FileNotFoundError(f"ChromeDriver not found at: {CHROMEDRIVER_PATH}")
    service = Service(CHROMEDRIVER_PATH)
    options = Options()
    # options.add_argument('--headless')  # Uncomment if you want headless
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--remote-debugging-port=9222')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--incognito')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def background_scrape(job_id, candidate):
    driver = None
    all_jobs = []
    try:
        driver = get_chrome_driver()
        login_linkedin(driver, EMAIL, PASSWORD)
        roles = candidate.get("roles", [])
        location = candidate.get("location", None)
        remote_options = candidate.get("remote", [])
        seniority = candidate.get("seniority", None)
        if roles:
            for role in roles:
                print(f"\n🎯 Searching for role: {role}")
                search_jobs(driver, role, location=location, remote_options=remote_options, seniority=seniority)
                job_ids = get_occludable_job_ids(driver, max_jobs=5)
                for job_id_ in job_ids:
                    job_data = scrape_job_details(driver, job_id_, role)
                    all_jobs.append(job_data)
                    time.sleep(2)
        else:
            keywords = " ".join(candidate.get("experience_keywords", []))
            print(f"\n🎯 Searching for keywords: {keywords}")
            search_jobs(driver, keywords, location=location, remote_options=remote_options, seniority=seniority)
            job_ids = get_occludable_job_ids(driver, max_jobs=5)
            for job_id_ in job_ids:
                job_data = scrape_job_details(driver, job_id_, keywords)
                all_jobs.append(job_data)
                time.sleep(2)
        print(f"\n📊 Total jobs scraped: {len(all_jobs)}")
        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = {"jobs": all_jobs}
    except Exception as e:
        print(f"❌ Error in background execution: {e}")
        jobs[job_id]["status"] = "error"
        jobs[job_id]["result"] = {"error": str(e), "jobs": all_jobs}
    finally:
        if driver is not None:
            driver.quit()

@app.route('/scrape', methods=['POST'])
def scrape_jobs_async():
    print("🚀 Received async scrape request")
    candidate = None
    if request.is_json:
        data = request.get_json()
        if 'candidate' in data:
            candidate = data['candidate']
        else:
            candidate = data
    else:
        return jsonify({"error": "Request must be JSON with a 'candidate' object or direct candidate fields."}), 400
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "in progress", "result": None}
    threading.Thread(target=background_scrape, args=(job_id, candidate)).start()
    return jsonify({"job_id": job_id}), 202

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)

if __name__ == "__main__":
    print("🚀 Starting LinkedIn Job Scraper Flask app...")
    app.run(host='0.0.0.0', port=5001)
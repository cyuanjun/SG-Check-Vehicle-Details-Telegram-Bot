# Import modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



PROFILE_DIR = r"C:\Users\Jay\Downloads\Programming\Projects\Check-Vehicle-Details-Telebot\driver_profile"
CHROMEDRIVER_PATH = "chromedriver.exe"
LTA_URL = "https://vrl.lta.gov.sg/lta/vrl/action/pubfunc?ID=EnquireRoadTaxExpDtProxy"
WAIT_SEC = 5

MODEL_XPATH = (
    "//h5/i[normalize-space()='Vehicle Make/Model']"
    "/ancestor::div[contains(@class,'separated')]//p"
)

EXPIRY_XPATH = (
    "//p[contains(@class,'vrlDT-label-p') and "
    "contains(normalize-space(), 'Road Tax Expiry Date')]"
    "/following-sibling::p[contains(@class,'vrlDT-content-p')]"
)


def create_driver(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=options
    )

    return driver



# function for retrieving vehicle details
def retrieve_vehicle_details(vehicle_plate):

    # create driver
    driver = create_driver()
    wait = WebDriverWait(driver, WAIT_SEC)

    try:
        driver.get(LTA_URL)

        # selects, clears and enters vehicle plate into textbox
        input_element = wait.until(
            EC.visibility_of_element_located((By.ID, "vehNoField"))
        )
        input_element.clear()
        input_element.send_keys(vehicle_plate)

        # click terms checkbox
        wait.until(
            EC.element_to_be_clickable((By.ID, "agreeTCbox"))
        ).click()

        # click next
        wait.until(
            EC.element_to_be_clickable((By.ID, "btnNext"))
        ).click()
        
        # retrieve results
        vehicle_model = wait.until(
            EC.visibility_of_element_located((By.XPATH, MODEL_XPATH))
        ).text.strip()

        road_tax_expiry = wait.until(
            EC.visibility_of_element_located((By.XPATH, EXPIRY_XPATH))
        ).text.strip()

        
        # return results
        return "1", vehicle_model, road_tax_expiry
    
    # handles TimeoutException
    except TimeoutException:
        if driver.find_elements(By.ID, "backend-errorBox"):
            return "0", "", ""
        
        return "-1", "", ""
    
    # handles all other errors
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "-1", "", ""

    # close browser properly
    finally:
        driver.quit()



# Defines main program
def main(vehicle_plate):

    status_code, vehicle_model, road_tax_expiry = retrieve_vehicle_details(vehicle_plate)

    # Print results
    if  status_code == "1":
        results = f"{vehicle_plate.upper()}\n{vehicle_model}\n{road_tax_expiry}"
        return results
    
    elif status_code == "0":
        return "No record found!"

    return "Service may be down, try again later!"



if __name__ == "__main__":
    vehicle_plate: str = input("Enter a vehicle plate: ")
    print(main(vehicle_plate))
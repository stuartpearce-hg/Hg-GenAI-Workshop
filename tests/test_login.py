import dotenv
import os
import pytest
from playwright.sync_api import Page, expect, Browser

dotenv.load_dotenv()

base_url = os.getenv('TEST_BASE_URL')
user_name = os.getenv('TEST_USER_NAME')
user_password = os.getenv('TEST_USER_PASSWORD')
state_file_path = os.getenv('TEST_STATE_FILE_PATH')


@pytest.fixture(scope='session', autouse=True)
def setup_session(browser: Browser):
    # Setup code here

    # Log into the site and save the session state
    context = browser.new_context()
    page = context.new_page()
    page.goto(base_url)
    page.get_by_label("Username", exact=True).fill(user_name)
    page.get_by_label("Password", exact=True).fill(user_password)
    page.get_by_role("button", name="Log in").click()

    context.storage_state(path=state_file_path)
    page.close()

    yield

    # Teardown code here


def test_has_title(page: Page):
    page.goto(base_url)

    # Expect a title "to contain" a substring.
    expect(page).to_have_title('Login - PMv3 Proposal Management System')


def test_can_login(browser: Browser):
    context = browser.new_context(storage_state=state_file_path)
    page = context.new_page()
    page.goto(base_url)

    expect(page).to_have_title('Home Page - PMv3 Proposal Management System')

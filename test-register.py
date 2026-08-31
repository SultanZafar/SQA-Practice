from playwright.sync_api import Page, expect
import random

def test_register_valid_user(page: Page):
    random_id = random.randint(1000, 9999)
    username = f"playwrightuser{random_id}"
    email = f"playwright{random_id}@gmail.com"

    page.goto("http://localhost:5000/register")
    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#password", "Test1234")
    page.fill("#confirm_password", "Test1234")
    page.click("#register-submit")
    expect(page).to_have_url("http://localhost:5000/login")


def test_register_short_password(page: Page):
    page.goto("http://localhost:5000/register")
    page.fill("#username", "playwrightuser2")
    page.fill("#email", "playwright2@gmail.com")
    page.fill("#password", "abc")
    page.fill("#confirm_password", "abc")
    page.click("#register-submit")
    expect(page.locator("#flash-message")).to_contain_text("Password must be at least 6 characters")

def test_login_existing_user(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")
    expect(page).to_have_url("http://localhost:5000/dashboard")

def test_register_empty_username(page: Page):
    page.goto("http://localhost:5000/register")
    page.fill("#email", "emptytest@gmail.com")
    page.fill("#password", "Test1234")
    page.fill("#confirm_password", "Test1234")
    page.click("#register-submit")
    expect(page).to_have_url("http://localhost:5000/register")

def test_register_password_mismatch(page: Page):
    page.goto("http://localhost:5000/register")
    page.fill("#username", "mismatchuser")
    page.fill("#email", "mismatchuser@gmail.com")
    page.fill("#password", "Test1234")
    page.fill("#confirm_password", "test321")
    page.click("#register-submit")
    expect(page.locator("#flash-message")).to_contain_text("Passwords do not match")

def test_register_duplicate_username(page: Page):
    page.goto("http://localhost:5000/register")
    page.fill("#username", "qauser")
    page.fill("#email", "qauser@gmail.com")
    page.fill("#password", "Test1234")
    page.fill("#confirm_password", "Test1234")
    page.click("#register-submit")
    expect(page.locator("#flash-message")).to_contain_text("already exists")

def test_login_wrong_password(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "wrongpassword")
    page.click("#login-submit")
    expect(page.locator("#flash-message")).to_contain_text("Invalid username or password")
    expect(page).to_have_url("http://localhost:5000/login")

def test_login_nonexistent_user(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "userdosenotexist999")
    page.fill("#password", "anypassword")
    page.click("#login-submit")
    expect(page.locator("#flash-message")).to_contain_text("Invalid username or password")

def test_create_task_valid(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")
    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "Buy groceries")
    page.click("#task-submit")
    expect(page).to_have_url("http://localhost:5000/dashboard")

def test_create_task_empty_title(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")
    page.goto("http://localhost:5000/task/new")
    page.click("#task-submit")
    expect(page).to_have_url("http://localhost:5000/task/new")

def test_create_task_with_priority(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")
    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "High priority task")
    page.select_option("#priority", "High")
    page.click("#task-submit")
    expect(page).to_have_url("http://localhost:5000/dashboard")

def test_new_task_appears_on_dashboard(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")
    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "Unique Task ABC123")
    page.click("#task-submit")
    expect(page.locator("text=Unique Task ABC123").first).to_be_visible()

def test_edit_task_title(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")

    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "Task to edit unique999")
    page.click("#task-submit")

    page.click("text=Task to edit unique999")
    page.click("a:has-text('Edit')")
    page.fill("#title", "Updated Task Title unique999")
    page.click("#task-submit")

    expect(page.locator("text=Updated Task Title unique999").first).to_be_visible()

def test_edit_task_status(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")

    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "Task for status change unique888")
    page.click("#task-submit")

    page.click("text=Task for status change unique888")
    page.click("a:has-text('Edit')")

    page.select_option("#status", "Completed")
    page.click("#task-submit")

    expect(page.locator(".badge-completed").first).to_be_visible()

def test_delete_task_confirm(page: Page):
    page.on("dialog", lambda dialog: dialog.accept())
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")
    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "Task to delete unique111")
    page.click("#task-submit")
    page.click("text=Task to delete unique111")
    page.click("button:has-text('Delete')")
    expect(page.locator("text=Task to delete unique111")).not_to_be_visible()

def test_delete_task_cancel(page: Page):
    page.on("dialog", lambda dialog: dialog.dismiss())

    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")

    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "Task to keep unique222")
    page.click("#task-submit")

    page.click("text=Task to keep unique222")
    page.click("button:has-text('Delete')")

    expect(page.locator("text=Task to keep unique222").first).to_be_visible()

def test_search_task_by_title(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")

    page.goto("http://localhost:5000/task/new")
    page.fill("#title", "Searchable Task unique333")
    page.click("#task-submit")

    page.goto("http://localhost:5000/dashboard")
    page.fill("#search-input", "Searchable Task unique333")
    page.click("#filter-submit")

    expect(page.locator("text=Searchable Task unique333").first).to_be_visible()

def test_filter_tasks_by_status(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")

    page.goto("http://localhost:5000/dashboard")
    page.select_option("#status-filter", "Pending")
    page.click("#filter-submit")

    expect(page.locator("#task-list")).to_be_visible()

def test_dashboard_inaccessible_after_logout(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")

    page.click("#nav-logout")
    page.wait_for_url("http://localhost:5000/login")

    page.goto("http://localhost:5000/dashboard")
    expect(page).to_have_url("http://localhost:5000/login")


def test_search_no_results(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill("#username", "qauser")
    page.fill("#password", "Test1234")
    page.click("#login-submit")
    page.wait_for_url("http://localhost:5000/dashboard")

    page.fill("#search-input", "ThisTaskDoesNotExistXYZ999")
    page.click("#filter-submit")

    expect(page.locator("#empty-state")).to_be_visible()
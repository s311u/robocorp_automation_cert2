from robocorp.tasks import task
from robocorp import browser
import time
from robot.libraries.String import String
# from RPA.Browser import Browser


from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive
pdf = PDF()


@task
def send_orders():
    """Get orders from website, execute them and make PDFs which will be made into zip archive"""
    browser.configure()
    download_csv_file()
    get_orders()
    open_robot_order_website()
    fill_forms(orders=get_orders())
    archive_receipts()

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    lib = Tables()
    orders = lib.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click("button:text('OK')")

def fill_forms(orders):
    for row in orders:
        select_robot_parts(row)
        # order_new()
        # try:
        #     order_new()
        # except:
        #     pass

def select_robot_parts(row):
    page = browser.page()

    order_id = row["Order number"]
    page.select_option("#head", row["Head"])
    body_id = row["Body"]
    body_id = f"id-body-{body_id}"
    page.click(f"#{body_id}")
    page.get_by_placeholder('Enter the part number for the legs').fill(row["Legs"])
    page.fill("#address", str(row["Address"]))
    robot_preview()
    submit_order(order_id)


def robot_preview():
    """Take a screenshot of the page"""
    page = browser.page()
    page.click("text=Preview")
    time.sleep(2)
    locator = page.locator("#robot-preview-image")
    page.screenshot(path="./output/element-screenshot-robot-preview-image.png", element = locator)
    # page.screenshot(path="output/element-screenshot-robot-preview-image.png")

def submit_order(order_id):
    page = browser.page()
    time.sleep(2)
    page.click("#order")
    store_as_pdf(order_number=order_id)
    check_exists(order_id)


def order_new():
    page = browser.page()
    time.sleep(2)
    page.click("#order-another")
    page.click("button:text('OK')")
    
def check_exists(order_id):
    page = browser.page()
    if "error" in page.content().lower():
        time.sleep(2)
        page.click("#order")
        check_exists(order_id)
    else:
        store_as_pdf(order_number = order_id)
        # ss_to_pdf(ss = "output/element-screenshot-robot-preview-image.png", pdf = pdf)
        order_new()
        # Log the innerHTML
    # except:
    #     store_as_pdf(order_number=order_id)
    #     order_new()

def store_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    page.wait_for_selector("#receipt").get_attribute("role")
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    targ = f"./output/order-receipt-{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, targ)
    ss_to_pdf(ss=["./output/element-screenshot-robot-preview-image.png"], target_document = targ)


def ss_to_pdf(ss, target_document):
    pdf = PDF()
    pdf.add_files_to_pdf(ss, target_document, True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output', 'receipt_archive.zip', include='order-receipt-*.pdf')

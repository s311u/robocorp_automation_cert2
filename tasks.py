from robocorp.tasks import task
from robocorp import browser

from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive





@task
def send_orders():
    """Get orders from website, execute them and make PDFs which will be made into zip archive"""
    browser.configure()
    open_robot_order_website()
    download_csv_file()
    get_orders()
    fill_forms(orders=get_orders())
    archive_receipts()



def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click("button:text('OK')")

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

def fill_forms(orders):
    for row in orders:
        select_robot_parts(row)
        order_new()

def select_robot_parts(row):

    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()

    order_id = row["Order number"]
    page.select_option("#head", row["Head"])
    body_id = row["Body"]
    body_id = f"id-body-{body_id}"
    page.click("#{body_id}")
    page.get_by_placeholder('Enter the part number for the legs').fill(row["Legs"])
    page.fill("#address", str(row["Address"]))
    page.click("text=Preview")
    robot_preview()
    submit_order()
    store_as_pdf(order_number=order_id)



def robot_preview():
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="output/element-screenshot-robot-preview-image.png")

def submit_order():
    page = browser.page()
    page.click("text=Order")
    check_exists()

def check_exists():
    page = browser.page()
    if page.get_by_label("order-completion"):
        return True
    else:
        submit_order()
        check_exists()

def store_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    receipt_html = page.locator("#reciept").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"output/order-receipt-{order_number}.pdf")
    
    ss_to_pdf(ss = "output/element-screenshot-robot-preview-image.png", pdf = pdf)


def log_out():
    """Presses the 'Log out' button"""
    page = browser.page()
    page.click("text=Log out")


def ss_to_pdf(ss, pdf):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files = ss,
        pdf = pdf
    )

def order_new():
    page = browser.page()
    page.click("text=Order another robot")

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output', 'receipt_archive.zip', include='order-receipt-*.pdf')

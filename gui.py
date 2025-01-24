# Celeste Productions © 2023
# Coded by Nauf
import sys, os, shutil, httpx, threading, urllib.request
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from bs4 import BeautifulSoup
from fpdf import fpdf
from PIL import Image

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

class Worker(QObject):
    signal = pyqtSignal(str) # This will recieve the progress messages

    @pyqtSlot(str)
    def run(self):
        # time.sleep(5)
        result = "Some String"
        self.signal.return_signal.emit(result)


class IM_Downloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timeout = httpx.Timeout(5, read=None)
        self.client = httpx.Client(http2=True, timeout=self.timeout, headers=HEADERS)

    def initUI(self):
        self.setGeometry(200, 200, 750, 400)
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))
        self.setWindowTitle("Issuu Mihaaru Downloader (Made by Nauf)")

        self.layout = QVBoxLayout()

        self.label = QtWidgets.QLabel(self)
        self.label.setText("Issuu Mihaaru Downloader")
        self.label.setFont(QFont("Century Gothic", 25))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.move(50,50)
        self.label.adjustSize()
        self.label.setStyleSheet('font-weight: bold;')

        self.textbox = QtWidgets.QTextEdit(self)
        self.textbox.setFont(QFont("Calibri", 16))
        self.textbox.setStyleSheet('margin-bottom: 20px; margin-top: 25px;')
        self.textbox.resize(280,100)
        self.img_required = QCheckBox("Images")
        self.img_required.setStyleSheet('padding: 0px;')
        self.pdf_required = QCheckBox("PDF")
        self.pdf_required.setStyleSheet('padding: 0;')

        self.file_location = QtWidgets.QLineEdit(self)
        self.current_dir = os.getcwd()
        self.file_location.setText(self.current_dir)
        self.file_location.setReadOnly(True)
        self.browse_btn = QtWidgets.QPushButton(self)
        self.browse_btn.setText("Browse")
        self.browse_btn.clicked.connect(self.file_browser)

        self.go_button = QPushButton("Go!")
        self.go_button.resize(50,50)
        self.go_button.adjustSize()
        self.go_button.setFont(QFont("Calibri", 12))
        self.go_button.clicked.connect(self.button_clicked)

        self.pbar_text = QLabel("Progress will be shown below")
        self.pbar_text.setStyleSheet('margin-top: 20px; font-weight: bold;')
        self.progress = QtWidgets.QTextBrowser(self)
        self.progress.setGeometry(100, 100, 100, 100)
        self.progress.setStyleSheet('margin-top: 2px; margin-bottom: 10px;')

        self.checkbox_layout = QHBoxLayout()
        self.checkbox_layout.addWidget(self.img_required)
        self.checkbox_layout.addWidget(self.pdf_required)

        self.browse_layout = QHBoxLayout()
        self.browse_layout.addWidget(self.file_location)
        self.browse_layout.addWidget(self.browse_btn)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.textbox)
        self.layout.addLayout(self.checkbox_layout)
        self.layout.addLayout(self.browse_layout)
        self.layout.addWidget(self.go_button)

        self.layout.addWidget(self.pbar_text)
        self.layout.addWidget(self.progress)
        self.setLayout(self.layout)

    # Progress msgs updating function
    def realtime_updates(self):
        self.progress.append(self.msg)
        print(self.msg)
        QApplication.processEvents()

    def file_browser(self):
        self.new_loc = QFileDialog.getExistingDirectory(self, 'Select Folder', self.current_dir)
        self.file_location.setText(self.new_loc)

    # Processing button function
    def button_clicked(self):
        link = self.textbox.toPlainText()
        img_check = self.img_required.isChecked()
        pdf_check = self.pdf_required.isChecked()
        saving_location = self.file_location.text()
        if link.find("issuu.com/") == -1:
            self.popups(wrong_link=True)
        elif img_check == False and pdf_check == False:
            self.popups(no_tick=True)
        elif os.path.exists(saving_location) == False:
            self.popups(location=True)
        else:
            self.worker = MainBackgroundThread(link=link, img=img_check, pdf=pdf_check, save_loc=saving_location)
            self.go_button.setEnabled(False) # Disables main button when processing starts
            self.worker.start()
            self.worker.finished.connect(lambda: self.popups(finished=True))
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(lambda: self.go_button.setEnabled(True))

    def popups(self, wrong_link = False, no_tick = False, finished = False, location = False, delete = False):
        if wrong_link == True:
            QMessageBox.critical(self, "Wrong Link!", "Please enter a link which is an Issuu publication")
        elif no_tick == True:
            QMessageBox.warning(self, "Choose PDF or Image!", "Please choose how you would like to save the publication that you're downloading")
        elif finished == True:
            QMessageBox.information(self, "Done!", "Finished downloading the link(s)")
        elif location == True:
            QMessageBox.warning(self, "Choose a valid file location", "Please select the place you would like to save the file(s) to")
        elif delete == True:
            QMessageBox.critical(self, "Could not delete the temporary directory. You can delete the folder manually.")
        return

    def images_to_pdf(self, imgs, date, location):
        current_folder = location
        filename = f"{date}.pdf"
        path = f"{current_folder}/{filename}"
        if os.path.exists(path) == False:
            pdf = fpdf.FPDF()
            pdf.set_auto_page_break(0)
            for img_name in imgs:
                pdf.add_page()
                image_path = f"{current_folder}\\{date}\\{img_name}"
                img = Image.open(image_path)
                img = img.convert("RGB")  # Ensure it's in RGB mode
                width, height = img.size  # Image size in pixels

                img.save(image_path, "JPEG")

                # Maintain aspect ratio
                max_width = 180  # Set the maximum width for the image (in mm)
                max_height = 297  # Set the maximum height for the image (in mm)

                # Calculate aspect ratio
                aspect_ratio = width / height

                # Convert pixels to millimeters (1 inch = 25.4 mm, 1 inch = 72 pixels for standard DPI)
                dpi = 72  # Adjust this if your image has a different DPI
                width_mm = width * 25.4 / dpi
                height_mm = height * 25.4 / dpi

                # Resize the image to fit within the max_width and max_height
                if width_mm > max_width or height_mm > max_height:
                    if aspect_ratio > 1:  # Landscape
                        width_mm = max_width
                        height_mm = width_mm / aspect_ratio
                    else:  # Portrait
                        height_mm = max_height
                        width_mm = height_mm * aspect_ratio
                
                pdf.image(image_path, 10, 0, width_mm, height_mm)
            pdf.output(path, "F")
            print(f"Images from '{date}' was compiled to a PDF successfully!\n")
        else:
            print(f"{filename} already exists.")
        return

    def issuu_mihaaru(self, link, location):
        main_url = link.replace("\n", "")
        page = self.client.get(main_url.strip())

        soup = BeautifulSoup(page.content, 'html.parser')

        # date = soup.find(attrs={"name": "twitter:title"})['content'].strip()
        date = soup.find('meta', property="og:title")['content'].strip()
        first_pic = soup.find('meta', property="og:image")['content']

        base_page_link = first_pic.replace('1_social_preview.jpg', '') # removes initial page number

        # seperate pages downloading as images below
        i = 1
        while True:
            page_link = f"{base_page_link}{i}.jpg"
            # check if the page's image exists
            pic_page_status = self.client.get(page_link).status_code
            if pic_page_status == 403:
                print("Finished grabbing all the images from that link\n")
                break
            if not os.path.exists(f"{location}/{date}"):
                os.makedirs(f"{location}/{date}")
            self.file_name = f"{location}/{date}/{date} - Page {i}.jpg"
            self.image_saver(date, page_link, i) # Actually was supposed to be the progress msgs
            # QTimer.singleShot(0, self.realtime_updates)

            # threading.Thread(target=self.progress.append(msg)).start()
            # self.worker2 = SecondBackgroundThread(msg)
            # self.worker2.start()
            # self.worker2.finished.connect(lambda: self.realtime_updates(msg))
            i+=1
        return date

    def image_saver(self, date, page_link, i):
        if not os.path.exists(self.file_name): # Checks for duplicate pages
            urllib.request.urlretrieve(page_link, self.file_name)
            self.msg = f"'{date} - Page {i}.jpg' saved successfully."
        else:
            self.msg = f"'{date} - Page {i}.jpg' already exists."
        print(self.msg)

    def issuu_mihaaru_pdf(self, link, pdf_only, location):
        date = self.issuu_mihaaru(link, location=location)
        directory = f"{location}/{date}"
        images = os.listdir(directory)
        images.sort(key=len)
        self.images_to_pdf(images, date, location)
        if pdf_only == True:
            try:
                shutil.rmtree(directory)
            except PermissionError:
                self.popups(delete=True)
        else:
            return

    def update(self):
        self.label.adjustSize()

class MainBackgroundThread(QThread):
    def __init__(self, link, pdf, img, save_loc):
        QThread.__init__(self)
        self.link = link
        self.pdf = pdf
        self.img = img
        self.save_loc = save_loc

    def run(self):
        all_links = self.link.split(',')
        IM = IM_Downloader()
        for each in all_links:
            if self.pdf == True and self.img == False:
                IM.issuu_mihaaru_pdf(link=each, pdf_only=True, location=self.save_loc)
            elif self.pdf == False and self.img == True:
                IM.issuu_mihaaru(link=each, location=self.save_loc)
            elif self.pdf == True and self.img == True:
                IM.issuu_mihaaru_pdf(link=each, pdf_only=False, location=self.save_loc)



def window():
    app = QApplication(sys.argv)
    win = IM_Downloader()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    window()

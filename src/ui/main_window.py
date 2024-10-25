from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTableWidget, QLabel, QFileDialog,
                            QTextEdit, QTableWidgetItem, QGroupBox, QLineEdit,
                            QSplitter, QMessageBox)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt5.QtGui import QIcon
import pandas as pd
import os
import sys
import json

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        # Handle console messages if needed
        print(f"Console: {message}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhatsApp Bulk Sender")
        self.setGeometry(100, 100, 1500, 800)
        self.media_path = None
        self.setup_web_profile()
        self.initUI()

    def setup_web_profile(self):
        # Create custom profile for WhatsApp Web
        self.profile = QWebEngineProfile("WhatsApp")
        
        # Set persistent storage path
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        storage_path = os.path.join(current_dir, "whatsapp_data")
        self.profile.setPersistentStoragePath(storage_path)
        
        # Enable necessary settings
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        
        # Set user agent to match Chrome 60+
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    def initUI(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Middle panel with message composition and WhatsApp Web
        middle_panel = self.create_middle_panel()
        splitter.addWidget(middle_panel)

        # Right panel
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set initial sizes for splitter
        splitter.setSizes([300, 600, 300])
        main_layout.addWidget(splitter)

        # Check Chrome version
        self.check_chrome_version()

    def create_toolbar(self):
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setSpacing(10)

        # Define toolbar buttons with their actions
        buttons = [
            ("Add Number", self.show_add_number_dialog),
            ("Send Message", self.send_messages),
            ("Import Contacts", self.show_import_dialog),
            ("Schedule", self.show_schedule_dialog),
            ("Settings", self.show_settings),
            ("Help", self.show_help)
        ]

        for text, action in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(action)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        toolbar_widget.setMaximumHeight(60)
        return toolbar_widget

    def create_left_panel(self):
        left_group = QGroupBox("WhatsApp Numbers")
        layout = QVBoxLayout(left_group)

        # Add number input
        number_layout = QHBoxLayout()
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter WhatsApp number")
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_number)
        number_layout.addWidget(self.number_input)
        number_layout.addWidget(add_btn)
        layout.addLayout(number_layout)

        # Numbers table
        self.numbers_table = QTableWidget()
        self.numbers_table.setColumnCount(3)
        self.numbers_table.setHorizontalHeaderLabels(["Name", "Number", "Status"])
        layout.addWidget(self.numbers_table)

        # Import/Export buttons
        button_layout = QHBoxLayout()
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(lambda: self.import_contacts('csv'))
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_contacts)
        button_layout.addWidget(import_btn)
        button_layout.addWidget(export_btn)
        layout.addLayout(button_layout)

        return left_group

    def create_middle_panel(self):
        middle_group = QGroupBox("Message & WhatsApp Web")
        layout = QVBoxLayout(middle_group)

        # Message composition area
        message_group = QGroupBox("Compose Message")
        message_layout = QVBoxLayout(message_group)
        self.message_edit = QTextEdit()
        message_layout.addWidget(self.message_edit)

        # Send options
        send_layout = QHBoxLayout()
        schedule_btn = QPushButton("Schedule Send")
        schedule_btn.clicked.connect(self.show_schedule_dialog)
        send_btn = QPushButton("Send Now")
        send_btn.clicked.connect(self.send_messages)
        send_layout.addWidget(schedule_btn)
        send_layout.addWidget(send_btn)
        message_layout.addLayout(send_layout)
        
        layout.addWidget(message_group)

        # WhatsApp Web View
        whatsapp_group = QGroupBox("WhatsApp Web")
        whatsapp_layout = QVBoxLayout(whatsapp_group)
        
        # Create WebEngine components
        self.web_view = QWebEngineView()
        self.page = CustomWebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.page)
        
        # Load WhatsApp Web
        self.web_view.setUrl(QUrl("https://web.whatsapp.com"))
        
        # Add reload button
        reload_btn = QPushButton("Reload WhatsApp")
        reload_btn.clicked.connect(self.reload_whatsapp)
        whatsapp_layout.addWidget(reload_btn)
        whatsapp_layout.addWidget(self.web_view)
        layout.addWidget(whatsapp_group)

        return middle_group

    def create_right_panel(self):
        right_group = QGroupBox("Attachments")
        layout = QVBoxLayout(right_group)

        # Attachment list
        self.attachment_table = QTableWidget()
        self.attachment_table.setColumnCount(3)
        self.attachment_table.setHorizontalHeaderLabels(["File Name", "Type", "Caption"])
        layout.addWidget(self.attachment_table)

        # Attachment buttons
        attach_layout = QHBoxLayout()
        attach_btn = QPushButton("Add File/Photo")
        attach_btn.clicked.connect(self.attach_media)
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_attachments)
        attach_layout.addWidget(attach_btn)
        attach_layout.addWidget(clear_btn)
        layout.addLayout(attach_layout)

        return right_group

    # Toolbar button actions
    def show_add_number_dialog(self):
        self.number_input.setFocus()

    def show_import_dialog(self):
        self.import_contacts('csv')

    def show_schedule_dialog(self):
        QMessageBox.information(self, "Schedule", "Scheduling feature coming soon!")

    def show_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog coming soon!")

    def show_help(self):
        QMessageBox.information(self, "Help", "Help documentation coming soon!")

    def check_chrome_version(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            version = driver.capabilities['browserVersion']
            driver.quit()
            
            if float(version.split('.')[0]) < 60:
                QMessageBox.warning(self, "Chrome Version Warning",
                                  f"Your Chrome version ({version}) is below 60. WhatsApp Web requires Chrome 60+.")
        except Exception as e:
            QMessageBox.warning(self, "Chrome Check Failed",
                              "Could not verify Chrome version. Please ensure Chrome 60+ is installed.")

    def reload_whatsapp(self):
        self.web_view.reload()

    def add_number(self):
        number = self.number_input.text()
        if number:
            row = self.numbers_table.rowCount()
            self.numbers_table.insertRow(row)
            self.numbers_table.setItem(row, 1, QTableWidgetItem(number))
            self.number_input.clear()

    def attach_media(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Attach Media", "", "All Files (*.*)")
        if file_name:
            self.media_path = file_name
            row = self.attachment_table.rowCount()
            self.attachment_table.insertRow(row)
            self.attachment_table.setItem(row, 0, QTableWidgetItem(file_name.split('/')[-1]))
            self.attachment_table.setItem(row, 1, QTableWidgetItem("File"))

    def clear_attachments(self):
        self.attachment_table.setRowCount(0)
        self.media_path = None

    def import_contacts(self, file_type):
        file_filter = "CSV files (*.csv)" if file_type == 'csv' else "Excel files (*.xlsx)"
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Contacts", "", file_filter)
        if file_name:
            try:
                df = pd.read_csv(file_name) if file_type == 'csv' else pd.read_excel(file_name)
                self.numbers_table.setRowCount(len(df))
                for i, row in df.iterrows():
                    self.numbers_table.setItem(i, 0, QTableWidgetItem(str(row.get('Name', ''))))
                    self.numbers_table.setItem(i, 1, QTableWidgetItem(str(row.get('Number', ''))))
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Error importing file: {str(e)}")

    def export_contacts(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Contacts", "", "CSV files (*.csv)")
        if file_name:
            try:
                data = []
                for row in range(self.numbers_table.rowCount()):
                    name = self.numbers_table.item(row, 0)
                    number = self.numbers_table.item(row, 1)
                    if name and number:
                        data.append({
                            'Name': name.text(),
                            'Number': number.text()
                        })
                df = pd.DataFrame(data)
                df.to_csv(file_name, index=False)
                QMessageBox.information(self, "Export Success", "Contacts exported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Error exporting contacts: {str(e)}")

    def send_messages(self):
        message = self.message_edit.toPlainText()
        numbers = []
        for row in range(self.numbers_table.rowCount()):
            number = self.numbers_table.item(row, 1)
            if number:
                numbers.append(number.text())
        
        if numbers and message:
            current_url = self.web_view.url()
            
            for number in numbers:
                url = f"https://web.whatsapp.com/send?phone={number}&text={message}"
                self.web_view.setUrl(QUrl(url))
                
                self.web_view.page().loadFinished.connect(
                    lambda ok: self.web_view.page().runJavaScript(
                        "document.querySelector('[data-testid=\"send\"]').click();")
                    if ok else None)
            
            self.web_view.setUrl(current_url)
            QMessageBox.information(self, "Success", "Messages sent successfully!")

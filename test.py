import unittest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://localhost:8000"
        # Unique test user to avoid conflicts
        timestamp = str(int(time.time()))
        cls.test_user = {"username": f"testuser_{timestamp}", "password": "Testpass123!"}

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.delete_all_cookies()

    def test_1_home_page_elements(self):
        """Ana sayfa elementlerinin doğru yüklendiğini kontrol eder"""
        self.driver.get(self.base_url)

        # Döviz tablosunun yüklenmesini bekle
        table = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "rates-table"))
        )
        self.assertTrue(table.is_displayed())

        # USD satırının varlığını kontrol et
        usd_row = table.find_element(By.XPATH, ".//tbody/tr[td/text()='USD']")
        self.assertIsNotNone(usd_row)

    def test_2_api_data_endpoint(self):
        """/api/data endpoint’inin beklenen JSON yapısını döndürdüğünü test eder"""
        res = requests.get(f"{self.base_url}/api/data")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for key in ("exchange_rates", "bitcoin_price", "market_news"):  # temel anahtarlar
            self.assertIn(key, data)

    def test_3_user_registration_login(self):
        """Kullanıcı kaydı ve girişi test eder"""
        # Kayıt sayfası
        self.driver.get(f"{self.base_url}/register")
        self.driver.find_element(By.NAME, "username").send_keys(self.test_user["username"])
        self.driver.find_element(By.NAME, "email").send_keys("test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys(self.test_user["password"])
        self.driver.find_element(By.NAME, "confirm").send_keys(self.test_user["password"])
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Başarı mesajı kontrolü
        self.assertIn("Kayıt başarılı!", self.driver.page_source)

        # Çıkış yap ve giriş testini gerçekleştir
        self.driver.find_element(By.LINK_TEXT, "Çıkış").click()
        self.driver.get(f"{self.base_url}/login")
        self.driver.find_element(By.NAME, "username").send_keys(self.test_user["username"])
        self.driver.find_element(By.NAME, "password").send_keys(self.test_user["password"])
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Profil sayfasına yönlendirme kontrolü
        self.assertIn("Profil", self.driver.page_source)

    def test_4_currency_conversion(self):
        """Döviz dönüşüm işlemini test eder"""
        self.driver.get(f"{self.base_url}/converter")
        self.driver.find_element(By.NAME, "amount").send_keys("100")
        self.driver.find_element(By.NAME, "from_currency").send_keys("USD")
        self.driver.find_element(By.NAME, "to_currency").send_keys("EUR")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        result = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-info"))
        )
        self.assertIn("Sonuç:", result.text)

    def test_5_comment_functionality(self):
        """Yorum işlevselliğini test eder"""
        # Giriş yap
        self.driver.get(f"{self.base_url}/login")
        self.driver.find_element(By.NAME, "username").send_keys(self.test_user["username"])
        self.driver.find_element(By.NAME, "password").send_keys(self.test_user["password"])
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Ana sayfaya dönerek yorum formunu kullan
        self.driver.get(self.base_url)
        comment_text = "Test yorumu " + str(time.time())

        textarea = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "comment"))
        )
        textarea.send_keys(comment_text)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Yorumun göründüğünü kontrol et
        self.assertIn(comment_text, self.driver.page_source)

    def test_6_profile_page(self):
        """Profil sayfası işlevselliğini test eder"""
        self.driver.get(f"{self.base_url}/profile/{self.test_user['username']}")
        self.assertIn(self.test_user["username"], self.driver.page_source)
        self.assertIn("Takipçi", self.driver.page_source)
        comments_section = self.driver.find_element(By.CLASS_NAME, "profile-comments")
        self.assertTrue(comments_section.is_displayed())

    def test_7_news_page(self):
        """Haberler sayfası testi"""
        self.driver.get(f"{self.base_url}/news")
        news_items = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "card"))
        )
        self.assertGreater(len(news_items), 0)

    def test_8_analysis_page(self):
        """Analiz sayfası grafik kontrolü"""
        self.driver.get(f"{self.base_url}/analysis")
        charts = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "canvas"))
        )
        self.assertGreaterEqual(len(charts), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)

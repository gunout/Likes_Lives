import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pickle
import json

class TikTokLiveLiker:
    def __init__(self):
        self.driver = None
        self.cookies_file = "tiktok_cookies.pkl"
        self.session_active = False
        self.like_count = 0
        
    def setup_driver(self):
        """Configure le navigateur Selenium"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            options.add_argument("--lang=fr-FR")
            
            # Désactiver les logs inutiles
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            self.driver = webdriver.Chrome(options=options)
            
            # Masquer le WebDriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
        except Exception as e:
            print(f"[!] Erreur lors du démarrage du navigateur: {e}")
            print("[!] Assurez-vous que ChromeDriver est installé et accessible")
            return False
    
    def login_to_tiktok(self):
        """Connecte l'utilisateur à TikTok"""
        print("[~] Ouverture de TikTok...")
        self.driver.get("https://www.tiktok.com")
        time.sleep(3)
        
        # Vérifier si des cookies existants sont disponibles
        if os.path.exists(self.cookies_file):
            print("[~] Chargement des cookies existants...")
            try:
                self.load_cookies()
                self.driver.refresh()
                time.sleep(3)
                
                # Vérifier si la connexion a réussi
                if self.is_logged_in():
                    print("[+] Connecté avec les cookies existants")
                    return True
                else:
                    print("[!] Les cookies sont expirés ou invalides")
                    os.remove(self.cookies_file)  # Supprimer les cookies invalides
            except Exception as e:
                print(f"[!] Erreur lors du chargement des cookies: {e}")
        
        print("[~] Redirection vers la page de connexion...")
        self.driver.get("https://www.tiktok.com/login")
        time.sleep(3)
        
        print("[~] Veuillez vous connecter manuellement à votre compte TikTok")
        print("[~] Méthodes de connexion disponibles:")
        print("    1. QR code")
        print("    2. Nom d'utilisateur/mot de passe")
        print("    3. Autres méthodes (Google, Facebook, etc.)")
        print("\n[~] Une fois connecté, appuyez sur Entrée dans ce terminal")
        
        # Attendre que l'utilisateur se connecte manuellement
        input("Appuyez sur Entrée après vous être connecté...")
        
        # Vérifier à nouveau si connecté
        if self.is_logged_in():
            print("[+] Connexion réussie!")
            # Sauvegarder les cookies pour les sessions futures
            self.save_cookies()
            return True
        else:
            print("[!] Échec de la connexion - Impossible de détecter la connexion")
            print("[!] Conseils:")
            print("    - Assurez-vous d'être bien connecté")
            print("    - Vérifiez que le nom d'utilisateur apparaît en haut à droite")
            print("    - Réessayez en utilisant une autre méthode de connexion")
            return False
    
    def is_logged_in(self):
        """Vérifie si l'utilisateur est connecté avec plusieurs méthodes"""
        try:
            # Méthode 1: Vérifier l'avatar utilisateur
            self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="user-avatar"]')
            return True
        except:
            pass
        
        try:
            # Méthode 2: Vérifier le bouton de profil
            self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="profile-icon"]')
            return True
        except:
            pass
        
        try:
            # Méthode 3: Vérifier le menu utilisateur
            self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="user-menu"]')
            return True
        except:
            pass
        
        try:
            # Méthode 4: Vérifier le nom d'utilisateur dans la navbar
            self.driver.find_element(By.CSS_SELECTOR, '[class*="avatar"]')
            return True
        except:
            pass
        
        # Vérifier si on est sur la page de login (signe qu'on n'est pas connecté)
        try:
            if "login" in self.driver.current_url.lower():
                return False
        except:
            pass
            
        return False
    
    def save_cookies(self):
        """Sauvegarde les cookies de session"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as file:
                pickle.dump(cookies, file)
            print("[+] Cookies sauvegardés pour la prochaine session")
        except Exception as e:
            print(f"[!] Erreur lors de la sauvegarde des cookies: {e}")
    
    def load_cookies(self):
        """Charge les cookies de session"""
        try:
            with open(self.cookies_file, 'rb') as file:
                cookies = pickle.load(file)
            
            self.driver.get("https://www.tiktok.com")
            for cookie in cookies:
                # Nettoyer le domaine des cookies
                if 'domain' in cookie:
                    if '.tiktok.com' in cookie['domain']:
                        self.driver.add_cookie(cookie)
        except Exception as e:
            print(f"[!] Erreur lors du chargement des cookies: {e}")
    
    def expand_live_window(self):
        """Agrandit la fenêtre du live pour mieux voir les éléments"""
        try:
            # Essayez de passer en mode plein écran ou d'agrandir la fenêtre
            self.driver.maximize_window()
            time.sleep(2)
            
            # Essayez de trouver et cliquer sur le bouton plein écran si disponible
            try:
                fullscreen_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="fullscreen-button"]')
                fullscreen_btn.click()
                print("[+] Mode plein écran activé")
            except:
                pass
                
        except Exception as e:
            print(f"[!] Impossible d'agrandir la fenêtre: {e}")
    
    def go_to_live(self, live_url):
        """Se rend sur le live spécifié"""
        try:
            print(f"[~] Navigation vers le live...")
            self.driver.get(live_url)
            
            # Attendre que la page se charge
            time.sleep(5)
            
            # Agrandir la fenêtre pour mieux voir les éléments
            self.expand_live_window()
            
            print("[+] Live chargé avec succès")
            print("[~] Recherche du bouton like...")
            
            return True
            
        except Exception as e:
            print(f"[!] Erreur lors de l'accès au live: {e}")
            return False
    
    def find_like_button(self):
        """Trouve le bouton like dans le live avec plusieurs méthodes"""
        try:
            # Méthode 1: Sélecteur standard
            like_button = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="live-like-icon"]')
            return like_button
        except NoSuchElementException:
            pass
        
        try:
            # Méthode 2: Sélecteur alternatif
            like_button = self.driver.find_element(By.CSS_SELECTOR, '.live-like-icon')
            return like_button
        except NoSuchElementException:
            pass
        
        try:
            # Méthode 3: Recherche par texte/aria-label
            like_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button, div')
            for button in like_buttons:
                text = button.get_attribute('outerHTML') or ''
                if 'like' in text.lower() or 'heart' in text.lower() or '❤' in text:
                    return button
        except:
            pass
            
        print("[!] Bouton like non trouvé - Essayez les solutions suivantes:")
        print("    1. Agrandissez manuellement la fenêtre du live")
        print("    2. Assurez-vous que le live est toujours actif")
        print("    3. Le bouton like peut être caché - déplacez votre souris sur le live")
        return None
    
    def send_like(self):
        """Envoie un like"""
        try:
            like_button = self.find_like_button()
            if like_button:
                # Faire un screenshot pour debug (optionnel)
                # like_button.screenshot('like_button.png')
                
                like_button.click()
                self.like_count += 1
                print(f"[+] Like envoyé ({self.like_count})")
                return True
            return False
        except Exception as e:
            print(f"[!] Erreur lors de l'envoi du like: {e}")
            return False

    def send_multiple_likes(self, count=50):
        """Envoie plusieurs likes rapidement"""
        successful_likes = 0
        for i in range(count):
            if self.send_like():
                successful_likes += 1
                # Petit délai entre chaque like
                time.sleep(0.1)
            else:
                print(f"[!] Échec de l'envoi du like {i+1}")
        return successful_likes
    
    def start_liking(self, live_url, interval=20, like_batch=50):
        """Démarre l'envoi automatique de likes par lots"""
        if not self.setup_driver():
            return
        
        try:
            if not self.login_to_tiktok():
                print("[!] Échec de la connexion - Le bot ne peut pas continuer")
                return
            
            if not self.go_to_live(live_url):
                return
            
            print(f"[+] Démarrage de l'envoi de lots de {like_batch} likes toutes les {interval} secondes...")
            print("[~] IMPORTANT: Gardez la fenêtre du navigateur visible")
            print("[~] Ne minimisez pas la fenêtre pendant l'opération")
            print("[~] Appuyez sur Ctrl+C pour arrêter")
            
            self.session_active = True
            failed_attempts = 0
            
            while self.session_active and failed_attempts < 5:
                successful_likes = self.send_multiple_likes(like_batch)
                print(f"[+] Lot de {successful_likes}/{like_batch} likes envoyés")
                
                if successful_likes > 0:
                    failed_attempts = 0  # Réinitialiser le compteur d'échecs
                    
                    # Attendre avant le prochain lot de likes
                    wait_time = interval
                    print(f"[~] Prochain lot dans {wait_time} secondes...")
                    time.sleep(wait_time)
                else:
                    failed_attempts += 1
                    print(f"[!] Échec de l'envoi du lot de likes ({failed_attempts}/5)")
                    time.sleep(2)
                    
            if failed_attempts >= 5:
                print("[!] Trop d'échecs consécutifs - Arrêt du bot")
                
        except KeyboardInterrupt:
            print("\n[!] Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"[!] Erreur inattendue: {e}")
        finally:
            self.stop_liking()
    
    def stop_liking(self):
        """Arrête l'envoi de likes"""
        self.session_active = False
        if self.driver:
            print(f"[+] Total de likes envoyés: {self.like_count}")
            print("[~] Fermeture du navigateur dans 5 secondes...")
            time.sleep(5)
            self.driver.quit()

def main():
    print("+---------------------------------------------------+")
    print("|         BOT TIKTOK LIVE LIKES (VERSION COMPTE)    |")
    print("|         Likes envoyés depuis votre compte         |")
    print("+---------------------------------------------------+\n")
    
    # Demander l'URL du live
    live_url = input("Entrez l'URL du live TikTok: ").strip()
    
    # Valider l'URL
    if not live_url:
        print("[!] URL invalide")
        return
    
    # Convertir les URLs courtes en URLs complètes si nécessaire
    if "vm.tiktok.com" in live_url or "vt.tiktok.com" in live_url:
        print("[~] Détection d'une URL courte TikTok...")
        try:
            import requests
            response = requests.get(live_url, allow_redirects=False, timeout=10)
            if response.status_code in [301, 302] and 'location' in response.headers:
                live_url = response.headers['location']
                print(f"[+] URL convertie: {live_url}")
        except:
            print("[!] Impossible de convertir l'URL courte")
    
    # Configuration pour 50 likes toutes les 20 secondes
    like_batch = 50
    interval = 20
    
    print(f"[~] Configuration: {like_batch} likes toutes les {interval} secondes")
    
    # Créer et lancer le bot
    bot = TikTokLiveLiker()
    bot.start_liking(live_url, interval, like_batch)

if __name__ == "__main__":
    main()
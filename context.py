import pyautogui
from logger import get_logger
import time
from datetime import datetime
from pyautogui import ImageNotFoundException

class prepareWindow():
    """
    Luokka Paintbrush-ohjelman (MS Paintin korvike Macille) avaamiseen ja valmistelemiseen
    """
    def __init__(self, application_name = 'Paintbrush'):
        self.application_name = application_name
        self.canvas_width = 800
        self.canvas_height = 600
        self.logger = get_logger(__name__)
    
    def open(self):
        """
        Avaa itse Paintbrush-ohjelman
        """
        self.logger.info(f"Opening {self.application_name}")
        # Avataan spotlightin kautta. Hyvin vastaava siis kuin Win + R
        pyautogui.keyDown("command")
        pyautogui.press("space")
        pyautogui.keyUp("command")
        time.sleep(0.5)
        pyautogui.typewrite(self.application_name)
        pyautogui.press('enter')
        return True
    
    def open_new_document(self, region=None):
        """
        Avaa uuden tyhjän dokumentin Paintbrushissa
        """
        self.logger.info("Opening new blank canvas")
        # Paintbrush avaa ensin tiedostoselaimen,
        # avataan sieltä uusi dokumentti
        if not region:
            # Tiedostoselaimen etsiminen
            try:
                file_browser = pyautogui.locateOnScreen('resources/FileBrowser.png', 
                                                        confidence=0.8,
                                                        grayscale=True)
                self.logger.info(f"File browser region found: {file_browser}")
            except:
                self.logger.error("Could not find File Browser region")
                return False

            # New Document -napin etsiminen tiedostoselaimen alueelta
            try:
                center = pyautogui.locateCenterOnScreen('resources/NewDocument.png', 
                                                        region=file_browser,
                                                        confidence=0.8,
                                                        grayscale=True)
                self.logger.info(f"New Document button found: {center}")
            except:
                self.logger.error("Could not find New Document button, the application might already be open")
                return False
    
        # Skaalaataan keskipiste Retinanäytön näyttökoordinaateiksi
        center = pyautogui.Point(center.x/2, center.y/2)

        # Klikataan New Documentia
        time.sleep(1)
        pyautogui.click(center.x, center.y)

        return True

    def define_canvas_size(self):
        """
        Määrittää piirtoalueen koon Paintbrushissa
        """
        self.logger.info(f"Defining canvas size to be {self.canvas_width}x{self.canvas_height}")
        time.sleep(0.5)
        pyautogui.typewrite(str(self.canvas_width))
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.typewrite(str(self.canvas_height))
        pyautogui.press('enter')
        return True

    def prepare_canvas(self):
        """
        Avaa Paintbrushin ja valmistelee uuden piirustusikkunan.
        Kerää siis luokan muut funktiot yhteen ja suorittaa ne oikeassa
        järjestyksessä.
        Käsittelee myös virheet oikealla tavalla niin ettei ohjelman suoritus kaadu.
        """
        screen_width, screen_height = pyautogui.size()
        self.logger.info(f"Display resolution: {screen_width}x{screen_height}")

        # Try to open the program
        if self.open():
            time.sleep(3)
        else:
            self.logger.error("Could not open Paintbrush.")
            return False
        
        # Try to open a new document
        if not self.open_new_document():
            find_window = findWindow(example_window='resources/Paintwindow.png',
                                     confidence=0.4)
            try:
                result = find_window.get_window()
                if not result:
                    self.logger.error("Could not find Paintbrush window or the New Document button")
                    return False
                else:
                    self.logger.info("Paintbrush was most likely already open")
                    return True
            except ImageNotFoundException:
                self.logger.error("Error in opening Paintbrush. Most likely File Browser region was not found.")
                return False
            
        # Define canvas size if the new document was opened
        else:
            time.sleep(1)
            self.define_canvas_size()
        return True

class closeWindow():
    """
    Luokka Paintbrush-ohjelman sulkemiseen
    """
    def __init__(self, application_name = 'Paintbrush'):
        self.application_name = application_name
        self.logger = get_logger(__name__)
    
    def close(self):
        """
        Sulkee Paintbrushin
        """
        self.logger.info(f"Closing {self.application_name}")
        time.sleep(1)

        # Varmistetaan että ohjelma on päällimäisenä esillä
        # samalla tavalla kuin ohjelmaa avatessa prepareWindow-luokassa
        pyautogui.keyDown("command")
        pyautogui.press("space")
        pyautogui.keyUp("command")
        time.sleep(0.5)
        pyautogui.typewrite(self.application_name)
        pyautogui.press('enter')
        time.sleep(1)

        # Suljetaan ohjelma
        pyautogui.hotkey('command', 'q')
        time.sleep(0.5)

        # Tallennetaan piirustukset
        filename = rf"Untitled-Painting-{datetime.now().strftime('%d%m%Y-%H-%M-%S')}.png"
        self.logger.info(f"Saving file as {filename}")
        pyautogui.press('enter') # Tallennus
        time.sleep(0.5)
        pyautogui.typewrite(filename)
        pyautogui.press('enter') # Tallenuksen varmistus
        return True

class findWindow():
    """
    Etsii ikkunan esimerkkikuvan perusteella. Palauttaa löydetyn ikkunan tiedot.
    Käytännössä siis locateOnScreen-wrapperi, jota on siistimpi käyttää mainissa.
    """
    def __init__(self,
                 example_window = None,
                 confidence = None):
        self.actual_window = None
        self.example_window = example_window
        self.confidence = confidence
        self.logger = get_logger(__name__)

    def _find_window(self):
        if self.confidence is None:
            self.actual_window = pyautogui.locateOnScreen(self.example_window)
        else:
            self.actual_window = pyautogui.locateOnScreen(self.example_window, 
                                                          confidence=self.confidence)
        if not self.actual_window:
            self.logger.error(f"Could not find window for {self.example_window}")
        else:
            self.logger.info(f"Found window for {self.example_window}: {self.actual_window}")

    def get_window(self):
        self._find_window()
        return self.actual_window
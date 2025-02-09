import pyautogui
from pyscreeze import ImageNotFoundException
from logger import get_logger
import math
import time

class CountSquaresInWindow:
    """
    Luokka neliöiden määrän laskemiseen annetun
    näyttöalueen sisällä (window). 

    Hyödyntää pyautogui:n locate-funktioita.
    Kaikki löydetyt neliöt klusteroidaan, jonka avulla voidaan tunnistaa
    ns merkittävimmät klusterit, joissa todennäköisesti on oikea neliö.

    Tunnistaa myös erikokoisia neliöitä.
    """
    def __init__(self, window=None, confidence=0.5):
        self.window = window
        self.logger = get_logger(__name__)
        self.confidence = confidence
        self.hit_threshold = 2 # Kuinka monta neliötä yhdessä klusterissa pitää olla jotta se lasketaan
        self.prominent_squares = []

    def _square_overlap(self, square1, square2):
        """
        Tarkistaa meneekö kaksi neliötä päällekkäin
        """
        x1, y1, x2, y2 = square1
        x3, y3, x4, y4 = square2
        if x1 < x4 and x2 > x3 and y1 < y4 and y2 > y3:
            return True
        return False
    
    def _remove_overlapping_squares(self, squares):
        """
        Klusteroi pyautogui:n tunnistamat potentiaaliset neliöt jotka menevät päällekkäin ja valitsee niistä keskimmäisimmän.
        Vaatii self.threshold määrän tunnistettuja neliöitä tietylle alueelle jotta se lasketaan.
        """
        # Muunnetaan jokainen neliö muodosta (vasen, ylä, leveys, korkeus) 
        # sen rajoiksi ja keskipisteeksi.
        square_data = []
        for s in squares:
            left, top, width, height = s
            bounds = (left, top, left + width, top + height)
            center = (left + width / 2, top + height / 2)
            square_data.append((bounds, center, s))

        clusters = []
        # Klusteroidaan neliöt, jotka osuvat samalla alueelle
        for bounds, center, orig in square_data:
            added = False
            for cluster in clusters:
                # Jos neliö osuu mihinkään klusterin neliöön, lisätään se ko klusteriin
                if any(self._square_overlap(bounds, other_bounds) for other_bounds, _, _ in cluster):
                    cluster.append((bounds, center, orig))
                    added = True
            if not added:
                clusters.append([(bounds, center, orig)])

        result = []
        # Katsotaan onko klustereissa tarpeeksi neliöitä,
        # jos on niin valitaan klusterin keskimmäisin neliö
        for cluster in clusters:
            if len(cluster) >= self.hit_threshold:
                # Lasketaan ns klusterin keskipiste
                avg_x = sum(item[1][0] for item in cluster) / len(cluster)
                avg_y = sum(item[1][1] for item in cluster) / len(cluster)
                # Valitaan tunnistettuista neliöstä se, joka on lähimpänä klusterin keskipistettä
                central_square = min(cluster, key=lambda item: math.hypot(item[1][0] - avg_x, item[1][1] - avg_y))
                result.append(central_square[2]) # indeksi 2 = alkuperäinen neliö, ks. rivi 47

        return result

    def count_squares(self):
        """
        Laskee neliöiden määrän luokalle määritellyn näyttöalueen sisällä.
        """
        # Katsotaan onko näyttöaluetta määritelty, muuten koko näyttö
        region = self.window if self.window else None
        self.logger.info(f"Looking for squares in region {region}")

        # Etsitään neliöt
        try:
            # Konenäkötaikaa
            squares = list(pyautogui.locateAllOnScreen('resources/Square.png', 
                                                       region=region, 
                                                       confidence=self.confidence,
                                                       grayscale=True))
            
            # Klusterointi ja päällekkäisten neliöiden poisto
            self.prominent_squares = self._remove_overlapping_squares(squares)
            self.logger.info(f"Found {len(self.prominent_squares)} squares in the region")
            self.logger.info(f"Square coordinates: {self.prominent_squares}")
        
        except ImageNotFoundException:
            self.logger.error(f"Could not find any squares with confidence {self.confidence}")
            self.prominent_squares = []

        return self.prominent_squares
    
    def set_window(self, window):
        """
        Käyttäjä voi siirellä ikkunaa esimerkiksi vahingossa
        piirtelyn aikana, joten ikkunan sijainti pitää päivittää
        aina ennen laskentaa. Sijainti saadaan mainista.
        """
        self.window = window

    def point_squares_on_display(self):
        """
        Käy kaikki löydetyt neliöt läpi hiirellä.
        Käytetään pääasiassa debuggaukseen, mutta toisaalta on myös ihan turvaannuttavaa nähdä mistä skripti on tunnistanut neliöt :)
        """
        if len(self.prominent_squares) == 0:
            return
        
        self.logger.info("Going through found square positions with the mouse")
        for square in self.prominent_squares:
            left, top, width, height = square
            center = (left + width, top + height)
            pyautogui.moveTo(center[0]/2, center[1]/2, duration=0.5)
            self.logger.info(f"Square at {center[0]/2} {center[1]/2} with size {width/2}x{height/2}")
            time.sleep(1)
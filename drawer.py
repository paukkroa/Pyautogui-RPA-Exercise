import pyautogui
import random
from logger import get_logger

class SquareDrawer():
    """
    Luokka neliöiden piirtelyyn.

    Piirtää neliöt annetulle piirtoalueelle.
    Neliöiden määrä voidaan arpoa tai määrittää manuaalisesti. Jos manuaalisesti, tulee luokalle syöttää neliöiden määrä parametrina.
    """
    def __init__(self, 
                 canvas_location = None, 
                 amount_of_squares = None):
        self.canvas_location = canvas_location # Piirtoalueen sijainti
        self.amount_of_squares = amount_of_squares # Voidaan halutessaan määrittää neliöiden määrä manuaalisesti
        self.distance_buffer = 75 # Neliöiden väliin jätettävä etäisyys pikseleinä.
                                  # Retinanäytöllä yksi näyttökoordinaatti == 4 pikseliä, joten esimerkiksi 100 pikseliä on 25 pyautogui:n koordinaattia
        self.draw_duration = 0.5 # Piirtämisen kesto yhtä viivaa kohti
        self.movement_duration = 0.5 # Hiiren liikkeen kesto paikasta toiseen siirryttäessä
        self.edge_buffer = False # lasketaanko neliöiden koko niin, että reunoille jää marginaali (True), 
                                 # vai voivatko neliöt sijoittua reunasta reunaan (False). True tarkoittaa siis käytännössä pienempiä neliöitä.
        self.side_size_limit = 100 # Neliöiden sivun maksimikoko
        self.logger = get_logger(__name__)
    
    def _set_canvas_location(self, canvas_location):
        """
        Tällä asetetaan piirustusruudun sijainti tarvittaessa, pitäisi kuitenkin tulla initissä (olettaen että alue ei muutu piirtäessä).
        Jos tätä luokkaa käytettäisiin esimerkiksi useiden piirustusalueiden kanssa, niin silloin tästä voi olla hyötyä.
        """
        self.canvas_location = canvas_location

    def _set_mouse_to_center(self, duration=None):
        """
        Asettaa hiiren keskelle piirustusruutua
        """
        if not self.canvas_location:
            raise ValueError("Canvas location not set")
        if not duration:
            duration = self.movement_duration
        center = pyautogui.center(self.canvas_location)
        pyautogui.moveTo(center)

    def _set_mouse_to_position(self, position, duration=None):
        """
        Asettaa hiiren haluttuun paikkaan
        """
        if not duration:
            duration = self.movement_duration
        pyautogui.moveTo(position, duration=duration)

    def _randomize_amount_of_squares(self):
        """
        Arvotaan neliöiden määrä
        """
        if not self.amount_of_squares or type(self.amount_of_squares) != int:
            self.amount_of_squares = random.randint(2, 5)
            self.logger.info(f"\033[1;33mPicked amount of squares to be {self.amount_of_squares}\033[0m")
        else:
            self.logger.info(f"\033[1;33mUse custom amount of squares {self.amount_of_squares}\033[0m")

    def _draw_square(self, lines, move_duration=None, draw_duration=None):
        """
        Piirtää neliön annettujen viivojen mukaan
        """
        if not draw_duration:
            draw_duration = self.draw_duration
        
        if not move_duration:
            move_duration = self.movement_duration

        for line in lines:
            pyautogui.moveTo(line[0], line[1], duration=move_duration)
            pyautogui.dragTo(line[2], line[3], duration=draw_duration, button='left')

    def draw_square_at_position(self, position, side_size, duration):
        """
        Piirtää neliön haluttuun kohtaan
        Neliö piirretään kursorista alas ja oikealle
        """
        # Rajataan neliön sivun maksimikoko
        side_size = min(side_size, self.side_size_limit)
        side_size = side_size / 2

        # Neliön vastakkaiset kulmapisteet
        # Jaetaan kahdella Retinanäytön skaalauksen takia, 
        # toisin sanoen muutetaan pikseleistä näyttökoordinaateiksi
        x0 = position[0] / 2
        y0 = position[1] / 2
        x1 = x0 + side_size # oikealle
        y1 = y0 + side_size # alas

        self.logger.info(f"Drawing square at:\nx0: {x0}, y0: {y0}\nx1: {x1}, y1: {y1}")

        # Neliön reunaviivat
        lines = [(x0, y0, x1, y0), # oikealle
                 (x1, y0, x1, y1), # alas
                 (x1, y1, x0, y1), # vasemmalle
                 (x0, y1, x0, y0) # takaisin ylös
                 ]
        
        # Piirtofunkkari
        self._draw_square(lines, duration)

    def _calculate_max_square_side_size(self):
        """
        Lasketaan kuinka isot neliön sivut voidaan maksimissaan piirtää. 
        Pienennetään neliöiden kokoa myös bufferin verran, jotta saadaan neliöt
        erilleen toisistaan ja paremmin sekoitettuihin sijainteihin. Toisin sanoen, 
        tämä funktio palauttaa vähän pienemmät koot, kuin mitä teoreettisesti voisi olla.
        """
        if not self.canvas_location:
            raise ValueError("Canvas location not set")

        canvas_width = self.canvas_location[2]
        canvas_height = self.canvas_location[3]
        buffer_multiplier = 1 if self.edge_buffer else -1
        buffer = self.distance_buffer * (self.amount_of_squares + buffer_multiplier) # Kokonaisbufferi, yksinkertaistaa laskuja myöhemmin

        # Teoreettinen maksimikoko huvikseen
        theoretical_max_size_row = canvas_width // self.amount_of_squares
        theoretical_max_size_col = canvas_height // self.amount_of_squares
        self.theoretical_max_square_side_size = min(theoretical_max_size_row, theoretical_max_size_col) / 2 # Jaetaan kahdella retina-näytön takia

        # Realistinen maksimikoko
        # Eli toisin sanoen, niin että neliöt mahtuvat ruudulle ja niiden väliin jää pieni väli
        # Lisäksi, edge_bufferin mukaan reunoillekin voidaan jättää marginaali
        max_size_row = (canvas_width - buffer) // self.amount_of_squares
        max_size_col = (canvas_height - buffer) // self.amount_of_squares
        self.max_square_side_size = min(max_size_row, max_size_col) / 2 # Jaetaan kahdella retina-näytön takia
        self.logger.info(f"Calculated max square side size to be {self.max_square_side_size}. Theoretical maximum would be {self.theoretical_max_square_side_size}")
        if self.max_square_side_size > self.side_size_limit:
            self.logger.info(f"Max square side size is over the limit of {self.side_size_limit}, we will use the limit in the drawings")

    def _create_square_positions(self):
        """
        Arvotaan neliöille sijainnit niin, että ne eivät mene toistensa päälle.

        Päätin laskea neliöiden sijainnit etukäteen, sillä esimerkiksi suoraan konenäöllä mahdollisia sijainteja
        skannatessa joutuisi joka tapauksessa luomaan ns vapaat sijainnit sekä valitsemaan niistä lopullisen sijainnin 
        jollain vastaavalla menetelmällä. Konenäkö myös toisi omat epävarmuustekijänsä, jotka saadaan tällä tavoin
        poistettua.
        """
        # Otetaan piirtoalueen tiedot ja lasketaan yhden "piirtosolun" koko
        # Neliöt piirretään solujen sisälle, niin että yhdessä solussa voi olla maksimissaan yksi neliö
        canvas_x, canvas_y, canvas_width, canvas_height = self.canvas_location
        cell_size = self.max_square_side_size + self.distance_buffer

        # Luodaan ns gridi, jonne neliöt voidaan sijoittaa, siten että neliöiden väliin jää solun bufferi
        cols = int(canvas_width / cell_size)
        rows = int(canvas_height / cell_size) 
        
        # Loopataan kaikkien gridin ruutujen läpi
        possible_cells = []
        for row in range(rows):
            # Skipataan reunimmaiset rivit ja sarakkeet, koska 
            # konenäkö tyypillisesti laskee esimerkiksi yläpalkin piirtoalueeksi
            if row == 0 or row == rows - 1:
                continue
            for col in range(cols):
                if col == 0 or col == cols - 1:
                    continue
                # Ruudun vasemman yläkulman koordinaatit
                x0 = int(canvas_x + col * cell_size)
                y0 = int(canvas_y + row * cell_size)
                # Lisätään mahdollisten sijaintien listaan
                possible_cells.append((x0, y0))
        
        # Arvotaan neliöille sijainnit gridin ruuduista
        # Jokainen saa siis uniikin ruudun ja täten ne eivät voi mennä päällekkäin
        random.shuffle(possible_cells)
        positions = []
        
        # Neliöt sijoitetaan ruutujen sisälle ja niiden sijainti ruudun sisällä voi vaihdella,
        # jotta lopputulos ei näytä ihan liian koneelliselta :)
        for cell in possible_cells[:self.amount_of_squares]:
            max_x_offset = int(cell_size - self.max_square_side_size) - 5 # -5 pyöristää alaspäin ja antaa pienen
                                                                          # marginaalin neliöiden väliin
            max_y_offset = int(cell_size - self.max_square_side_size) - 5  
            max_x_offset = max_x_offset if max_x_offset > 0 else 0 # Offset ei voi olla negatiivinen
            max_y_offset = max_y_offset if max_y_offset > 0 else 0
            offset_x = random.randint(0, max_x_offset)
            offset_y = random.randint(0, max_y_offset)
            positions.append((cell[0] + offset_x, cell[1] + offset_y))
        
        # Lopulliset sijainnit pikseleinä (ei näyttökoordinaatteina)
        self.positions = positions
        self.logger.info(f"Selected square positions (upper left corner): {self.positions}")

    def get_amount_of_squares(self):
        """
        Helpperi jotta voidaan verrata piirrettyjen ja 
        myöhemmin konenäöllä laskettujen neliöiden määrää
        """
        return self.amount_of_squares

    def prepare_to_draw(self):
        """
        Asetetaan tarvittavat muuttujat valmiiksi
        """
        self._randomize_amount_of_squares()
        self._calculate_max_square_side_size()
        self._create_square_positions()
        self._set_mouse_to_center()

    def draw_squares(self):
        """
        Piirretään itse neliöt
        """
        if not self.positions:
            self.prepare_to_draw()

        for position in self.positions:
            self.draw_square_at_position(position, self.max_square_side_size, self.draw_duration)

    
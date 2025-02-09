from context import findWindow, prepareWindow, closeWindow
from drawer import SquareDrawer
from counter import CountSquaresInWindow
from logger import get_logger

logger = get_logger(__name__)

def find_canvas():
    """
    Etsii piirustusikkunan position.

    Etsii ensin piirustusikkunan. Tässä menee omalla tietokoneella 
    yleensä top ja left väärin, mutta koko oikein. 
    -> Etsitään seuraavaksi yläpalkki, tästä saadaan tarkemmin top ja left
    koordinaatit.

    Lopuksi yhdistetään nämä tiedot, jotta saadaan todenmukainen piirtoalue selville.
    """
    # Etsitään piirustusikkuna
    paint = findWindow(example_window='resources/Paintwindow.png',
                       confidence=0.1)
    paint = paint.get_window()

    # Etsitään piirustusikkunan yläpalkki,
    top_bar = findWindow(example_window='resources/Topbar.png',
                         confidence=0.4)
    top_bar = top_bar.get_window()

    # Yhdistetään oikeat koordinaatit ja jätetään pieni marginaali,
    # jotta ei piirrettäisi reunojen yli
    buffer = 40 # 20 pikseliä retinanäytöllä
    paint = (top_bar[0] - buffer, 
             top_bar[1] - buffer, 
             paint[2] - buffer, 
             paint[3] - buffer)

    return paint, top_bar

def prepare_environment():
    """
    Valmistelee piirtoalueen.
    Eli käytännössä avaa Paintbrushin ja avaa uuden tyhjän dokumentin
    """
    preparer = prepareWindow()
    return preparer.prepare_canvas()

def main():
    # Valmistellaan Paintbrush ja katsotaan sen piirtoalueen sijainti konenäöllä
    if not prepare_environment():
        return 1
    canvas,_ = find_canvas()
    print("----------------\n")

    # Valmistellaan piirtäjä löydetylle Paintbrushin piirtoalueelle
    drawer = SquareDrawer(canvas)
    drawer.prepare_to_draw()
    print("----------------\n")

    # Tallennetaan arvottu (tai erikseen määritetty) neliöiden määrä
    # myöhempää vertailua varten
    amount_of_squares = drawer.get_amount_of_squares()

    # Piirretään itse neliöt
    drawer.draw_squares()
    print("----------------\n")

    # Lasketaan neliöiden määrä
    counter = CountSquaresInWindow(window=canvas, confidence=0.4) # Cofidence on suhteellisen matala ja pyautogui tuottaakin
                                                                  # yleensä satoja osumia, mutta klusteroinnilla saadaan hudit 
                                                                  # aika hyvin pois.
    detected_squares = counter.count_squares() # Itse konenäkö- ja klusterointioperaatio
    amount_of_detected_squares = len(detected_squares)
    print("----------------\n")
    
    # Vertaillaan laskettua ja piirrettyä neliöiden määrää
    if amount_of_detected_squares == amount_of_squares:
        print(f"\033[1;92mGot the right amount of squares {amount_of_squares}\033[0m") # Vihreä väri helpottaa tuloksen erottamista
                                                                                       # muista tulosteista
    else:
        print(f"\033[1;91mSquares drawn and counted incorrectly!\033[0m") # Sama kuin ylempänä, mutta punaisena virheen merkiksi :)
        print(f"Expected amount of squares: {amount_of_squares}")
        print(f"Amount of squares counted: {amount_of_detected_squares}")
    
    # Näytetään vielä neliöiden positiot hiirellä (lähinnä debugaamista varten)
    counter.point_squares_on_display()
    print("----------------\n")

    
    # Annetaan käyttäjän piirustaa halutessaan lisää ja lasketaan uudelleen neliöiden määrä
    while True:
        user_input = input("Press /exit to exit, enter to recount the number of squares: ")
        if user_input == "/exit":
            break
        else:
            # Katsotaan onko ikkuna siirtynyt tai suljettu
            canvas,_ = find_canvas()
            counter.set_window(canvas)
            detected_squares = counter.count_squares()
            amount_of_detected_squares = len(detected_squares)
            print(f"\033[1;38;5;208mDetected squares: {amount_of_detected_squares}\033[0m") # Tällä kertaa oranssi, koska ei voida tietää mitä 
                                                                                            # käyttäjä on piirrellyt
            counter.point_squares_on_display()

    # Suljetaan ohjelma
    closer = closeWindow()
    closer.close()

    # Kaikki ok
    return 0

if __name__ == "__main__":
    main()
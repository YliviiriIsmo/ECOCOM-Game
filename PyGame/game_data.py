import json
import os

class GameData:
    SAVE_FILE = "saves.json"

    @staticmethod
    def save_data(name, score, time_elapsed):
        """Tallentaa uuden pelituloksen lisäämällä sen JSON-tiedostoon."""
        data = []
        if os.path.exists(GameData.SAVE_FILE):
            with open(GameData.SAVE_FILE, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []

        # Lisätään uusi tallennus listaan
        new_entry = {"name": name, "score": score, "time_elapsed": time_elapsed}
        if new_entry not in data:  # Varmistetaan, ettei duplicaatteja
            data.append(new_entry)

            # Tallennetaan takaisin tiedostoon
            with open(GameData.SAVE_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            print("Tallennus estetty: Tämä tieto on jo olemassa.")  # DEBUG

    @staticmethod
    def load_data():
        """Lataa tallennetut pelitiedot."""
        if os.path.exists(GameData.SAVE_FILE):
            with open(GameData.SAVE_FILE, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []
    
    def get_top_scores(limit=10):
        """ Lataa ja järjestää top-pisteet laskevassa järjestyksessä. """
        data = GameData.load_data()
        sorted_scores = sorted(data, key=lambda x: x["score"], reverse=True)  # Järjestetään pisteiden mukaan
        return sorted_scores[:limit]  # Palautetaan vain top N tulosta
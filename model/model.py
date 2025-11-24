from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        relazioni=TourDAO.get_tour_attrazioni()
        if relazioni is None:
            return # errore già stampato nella tour_DAO
        else:
            for relazione in relazioni:
                id_tour=relazione['id_tour']
                id_att=relazione['id_attrazione']

                # per ogni valore (tutte le info dei tour) del dizionario tour
                for tour in self.tour_map.values():
                    # Per ogni valore (tutte le info dell'attrazione) del dizionario attrazione
                    for attrazione in self.attrazioni_map.values():
                        # verifico condizioni
                        if attrazione.id==id_att and tour.id==id_tour:
                            tour.attrazioni.add(attrazione)
                            attrazione.tour.add(tour)

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        # PRENDO TUTTI I TOUR (DAI VALORI DEL DIZIONARIO) CHE HANNO LO STESSO ID_REGIONE DELLA REGIONE SELEZIONATA
        self._tour_regione=[regione for regione in self.tour_map.values() if regione.id_regione==id_regione]


        self._max_giorni = max_giorni
        self._max_budget = max_budget

        self._ricorsione(0,[],0,0,0,set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        # PARTE A (ogni volta che richiamo la ricorsione verifico)
        # verifico se il valore_corrente sia migliore del valore_ottimo
        if valore_corrente > self._valore_ottimo:
            # aggiorno i valori
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo=pacchetto_parziale.copy()  # che crea una copia superficiale della lista originale
            self._costo = costo_corrente

        # Loop tour rimanenti
        for i in range (start_index, len(self._tour_regione)):
            tour=self._tour_regione[i]

            # PARTE C considerazione filtri prima della ricorsione
            if ((self._max_budget is None or costo_corrente + tour.costo <= self._max_budget)  # se non è stato inserito max_budget o la somma non supera il massimo costo
                    and (self._max_giorni is None or durata_corrente + tour.durata_giorni <= self._max_giorni) # se non è stato inserito max_giorni o la somma non supera num max giorni
                    and not attrazioni_usate.intersection(tour.attrazioni)): # le attrazioni non sono già presenti

                # PARTE D compute_partial
                pacchetto_parziale.append(tour)
                durata_corrente += tour.durata_giorni
                costo_corrente += tour.costo
                valore_corrente += sum(a.valore_culturale for a in tour.attrazioni) # tour.attrazioni è l'insieme presente nell'oggetto TOUR
                attrazioni_usate.update(tour.attrazioni) # aggiorno le attrazioni

                # PARTE E ricorsione
                self._ricorsione(i+1, pacchetto_parziale, durata_corrente,costo_corrente,valore_corrente,attrazioni_usate)

                # PARTE F back_tracking
                pacchetto_parziale.pop() # elimino tour aggiunto (smonto la lista)
                attrazioni_usate.difference_update(tour.attrazioni)  # rimuovo attrazioni aggiunte

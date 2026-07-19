from src.core import Client, Film, Seance, Ticket
from datetime import datetime

class Cinema:
    def __init__(self, nom="My Cinema"):
        self.__nom     = nom
        self.__films   = []
        self.__clients = []
        self.__seances = []
        self.__tickets = []  
        self.__revenus = 0

    @property
    def nom(self)           : return self.__nom
    @property
    def films(self)         : return self.__films
    @property
    def clients(self)       : return self.__clients
    @property
    def seances(self)       : return self.__seances 
    @property
    def tickets(self)       : return self.__tickets
    @property
    def revenus(self)       : return self.__revenus
    @revenus.setter
    def revenus(self, v)    : self.__revenus = v

    def add_film(self, f)   : self.__films.append(f)    
    def add_client(self, c) : self.__clients.append(c)
    def add_seance(self, s) : self.__seances.append(s)

    def get_client_by_code(self, code):
        for c in self.clients:
            if c.code == code:
                return c
        return None
    
    def get_film_by_code(self, code):
        for f in self.films:
            if f.code == code:
                return f
        return None
    
    def get_seance_by_code(self, code):
        for s in self.seances:
            if s.code == code:
                return s
        return None

    def reserver_ticket(self, codec, codes):
        client = self.get_client_by_code(code=codec)
        seance = self.get_seance_by_code(code=codes)

        if client is not None and seance is not None:
            if seance.seanceDisponible():
                ticket = Ticket(client=client, seance=seance, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
                self.__tickets.append(ticket)
                seance.places_disponibles -= 1
                client.ajouter_achat(seance.film.title, seance.code)
                self.__revenus += seance.price
                return ticket, "ok"
            return None, "no_places"
        return None, "not_found"

    def cancel_ticket(self, codeTicket):
        for t in self.__tickets :
            if t.code == codeTicket :
                if t.etatTicket() == "reserved":
                    t.etat = "canceled"
                    t.seance.places_disponibles = t.seance.places_disponibles + 1
                    self.__revenus -= t.seance.price
                    return True
        return False

    def utiliser_ticket(self, codeTicket):
        for t in self.__tickets:
            if t.code == codeTicket:
                if t.etatTicket() == "reserved":
                    t.etat = "used"
                    return True
        return False

    def seances_disponibles(self):
        return [s for s in self.__seances if s.seanceDisponible()]
    
    def tickets_client(self, code):
        return [t for t in self.__tickets if t.client.code == code]
    
    def stats(self):
        reserve = sum(1 for t in self.__tickets if t.etatTicket() == "reserved")
        annule  = sum(1 for t in self.__tickets if t.etatTicket() == "canceled")
        utilise = sum(1 for t in self.__tickets if t.etatTicket() == "used")
        return {
            'total_clients' : len(self.__clients),
            'total_films'   : len(self.__films),
            'total_seances' : len(self.__seances),
            'total_tickets' : len(self.__tickets),
            'reserved'      : reserve,
            'cancelled'     : annule,
            'used'          : utilise,
            'revenus'       : self.__revenus
        }
    
    @staticmethod
    def reset_counters():
        Client.cpt = 1
        Film.cpt   = 1
        Seance.cpt = 1
        Ticket.cpt = 1


class Ticket:
    cpt = 1
    
    def __init__(self, code=None, client="", seance="", date="", etat="reserved"):
        self.__code    = code
        self.__client  = client
        self.__seance  = seance
        self.__date    = date 
        self.__etat    = etat

    @property
    def client(self)                 : return self.__client
    @property
    def code(self)                   : return self.__code
    @code.setter
    def code(self, v)                : self.__code = v
    @property 
    def seance(self)                 : return self.__seance
    @property
    def date(self)                   : return self.__date
    @property
    def etat(self)                   : return self.__etat
    @etat.setter
    def etat(self, v)                : self.__etat = v

    def etatTicket(self):
        if self.__etat == "reserved":
            return "reserved"
        elif self.__etat == "canceled":
            return "canceled"
        return "used"
    
    def __str__(self) :
        client_str = f"{self.__client.lastname} {self.__client.name}" if hasattr(self.__client, 'lastname') else str(self.__client)
        film_str = self.__seance.film.title if hasattr(self.__seance, 'film') and self.__seance.film else "N/A"
        return f"Ticket {self.__code} | Client: {client_str} | Film: {film_str} | {self.__etat}"


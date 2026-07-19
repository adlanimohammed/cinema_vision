class Seance:
    cpt = 1
    
    def __init__(self, code=None, film=None, date_heure="", nbrt=0, price=0.0, status="active"):
        self.__code       = code
        self.__film       = film
        self.__date_heure = date_heure
        self.__nbrt       = nbrt
        self.__nbrd       = nbrt
        self.__price      = price
        self.__status     = status

    @property
    def code(self)                  : return self.__code
    @code.setter
    def code(self, v)               : self.__code = v
    @property
    def film(self)                  : return self.__film
    @film.setter
    def film(self, v)               : self.__film = v
    @property
    def date_heure(self)            : return self.__date_heure
    @date_heure.setter
    def date_heure(self, v)         : self.__date_heure = v
    @property
    def places_totales(self)        : return self.__nbrt
    @places_totales.setter
    def places_totales(self, v)     : self.__nbrt = v
    @property
    def places_disponibles(self)    : return self.__nbrd
    @places_disponibles.setter
    def places_disponibles(self, v) : self.__nbrd = v
    @property
    def price(self)                  : return self.__price
    @price.setter
    def price(self, v)              : self.__price = v
    @property
    def status(self)                : return self.__status
    @status.setter
    def status(self, v)             : self.__status = v

    def seanceDisponible(self)      : return self.places_disponibles > 0 and self.__status == "active"
    
    def __str__(self): return f"Seance {self.__code}: {self.__film.title if self.__film else 'N/A'} @ {self.__date_heure} | {self.__nbrd}/{self.__nbrt} places | {self.__price} DH"


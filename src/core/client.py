from src.core.personne import Personne
from datetime import datetime

class Client(Personne):
    cpt = 1
    
    def __init__(self, code=None, lastname="", name="", telephone="", date=""):
        self.__code    = code 
        self.__date    = date
        self.__history = []
        super().__init__(lastname, name, telephone)

    @property
    def code(self)         : return self.__code  
    @code.setter
    def code(self, v)      : self.__code = v 
    @property
    def date(self)         : return self.__date
    @date.setter
    def date(self, v)      : self.__date = v
    @property
    def history(self)      : return self.__history
  
    def ajouter_achat(self, film_title, seance_code):
        self.__history.append({
            'film'  : film_title,
            'seance': seance_code,
            'date'  : datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    # ---- make the object subscriptable, so we can use client[key] ----
    def __getitem__(self, key) :
        try : 
            return getattr(self, key) 
        except AttributeError :
            raise KeyError(f"'{key}' is not a valid attribute of client.") 
       
    def __str__(self)     : return f'{self.__code}__{super().__str__()}'

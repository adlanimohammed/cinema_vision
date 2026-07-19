class Film:
    cpt = 1
    
    def __init__(self, code=None, title="", genre="", duree=0, description=""):
        self.__code         = code
        self.__title        = title
        self.__genre        = genre
        self.__duree        = duree
        self.__description  = description
        self.__rating       = 0
        self.__votes        = 0

    @property
    def code(self)           : return self.__code
    @code.setter
    def code(self, v)        : self.__code = v
    @property
    def title(self)          : return self.__title
    @title.setter
    def title(self, v)       : self.__title = v
    @property
    def genre(self)          : return self.__genre
    @genre.setter
    def genre(self, v)       : self.__genre = v
    @property
    def duree(self)          : return self.__duree
    @duree.setter
    def duree(self, v)       : self.__duree = v
    @property
    def description(self)    : return self.__description
    @description.setter
    def description(self, v) : self.__description = v
    @property
    def rating(self)         : return self.__rating

    def add_rating(self, rating):
        total = self.__rating * self.__votes + rating
        self.__votes += 1
        self.__rating = round(total / self.__votes, 1)

    def __str__(self): return f'{self.__code}__{self.__title}__{self.__genre}__{self.__duree}min'


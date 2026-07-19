class Personne:
    def __init__(self, lastname, name, telephone):
        self.__lastname  = lastname
        self.__name      = name
        self.__telephone = telephone

    @property 
    def lastname(self)     : return self.__lastname
    @lastname.setter
    def lastname(self, v)  : self.__lastname = v
    @property
    def name(self)         : return self.__name
    @name.setter
    def name(self, v)      : self.__name = v
    @property
    def telephone(self)    : return self.__telephone
    @telephone.setter
    def telephone(self, v) : self.__telephone = v

    def __str__(self)      : return f"{self.__lastname}__{self.__name}__{self.__telephone}"


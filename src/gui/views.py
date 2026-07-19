# ---- pure UI updates ----
from src.gui import state

class Renderer :
  def __init__(self, tree_clients, tree_seances, tree_films, stats_labels) :
    self.__tree_clients = tree_clients
    self.__tree_seances = tree_seances
    self.__tree_films   = tree_films

    self.__stats_labels = stats_labels
    
  @property
  def tree_clients(self)    : return self.__tree_clients
  @tree_clients.setter
  def tree_clients(self, v) : self.__tree_clients = v
  @property
  def tree_seances(self)    : return self.__tree_seances
  @tree_seances.setter
  def tree_seances(self, v) : self.__tree_seances = v
  @property
  def tree_films(self)      : return self.__tree_films
  @tree_films.setter
  def tree_films(self, v)   : self.__tree_films = v

  @property
  def stats_labels(self)    : return self.__stats_labels
  @stats_labels.setter
  def stats_labels(self, v) : self.__stats_labels = v
  
  # ---- render clients ----
  def render_clients(self, clients_array) :
    # clearing the treeview to prevent duplicate entries.
    for item in self.tree_clients.get_children() :
      self.tree_clients.delete(item)
    # reload the list with current client data.
    for c in clients_array :
      self.tree_clients.insert("", "end", values=(c["code"], c["name"], c["lastname"], c["telephone"]))

  # ---- render seances ----
  def render_seances(self, seances_array) :
    # clearning the treeview to prevent duplicate entries.
    for item in self.tree_seances.get_children() :
      self.tree_seances.delete(item)
    # reload the list with current seance data.
    for s in seances_array :
      self.tree_seances.insert("", "end", values=(s.code, s.film.title, s.date_heure, f"{s.places_disponibles}/{s.places_totales}", f"{s.price} DH"))

  # ---- render films ----
  def render_films(self, films_array) :
    # clearing the treeview to prevent duplicate entries.
    for item in self.tree_films.get_children() :
      self.tree_films.delete(item)
    # reload the list with current film data.
    for f in films_array :
      self.tree_films.insert("", "end", values=(f.code, f.title.strip(), f.genre.strip(), f"{f.duree} min"))

  # ---- refresh stats ----
  def refresh_stats(self) :
    stats = state.cinema.stats() 
    for key, label in self.__stats_labels.items() :
      if key == "revenus" : label.config(text=f"{stats[key]}")
      else                : label.config(text=str(stats[key]))


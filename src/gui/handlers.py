# ---- business logic ----
import tkinter as tk
from tkinter  import ttk, messagebox
from datetime import datetime

from src.core import Client, Seance, Film, Ticket
from src.gui import state 

class AddHandler :
  def __init__(self, client_entries, seance_entries, film_entries) :
    self.__client_entries = client_entries
    self.__seance_entries = seance_entries
    self.__film_entries   = film_entries
    self.__editing        = {"client": None, "seance": None, "film": None}
    self.__revert_callbacks = {"client": None, "seance": None, "film": None}

  @property
  def client_entries(self)    : return self.__client_entries
  @client_entries.setter
  def client_entries(self, v) : self.__client_entries = v
  @property
  def seance_entries(self)    : return self.__seance_entries
  @seance_entries.setter
  def seance_entries(self, v) : self.__seance_entries = v
  @property
  def film_entries(self)      : return self.__film_entries
  @film_entries.setter
  def film_entries(self, v)   : self.__film_entries = v
  @property
  def editing(self)           : return self.__editing

  def set_edit_mode(self, entity, code, revert_callback=None) :
    self.__editing[entity] = code
    self.__revert_callbacks[entity] = revert_callback

  def clear_edit_mode(self, entity) :
    self.__editing[entity] = None
    if self.__revert_callbacks[entity] :
      self.__revert_callbacks[entity]()
      self.__revert_callbacks[entity] = None

  # ---- reset fields ----
  def reset_entries(self, entries_dict) :
    for placeholder, entry in entries_dict.items() :
      if hasattr(entry, 'set_date') :
        entry.set_date(datetime.now().date())
      else :
        entry.delete(0, "end")
        entry.insert(0, placeholder)
        entry.configure(foreground="gray")

  # ---- add client ----
  def add_client(self) :
    lastname, name, tel = self.client_entries["lastname"].get(), self.client_entries["name"].get(), self.client_entries["phone"].get()
    if lastname in ("", "lastname") or name in ("", "name") or tel in ("", "phone") :
      messagebox.showerror(title="error", message="please fill all fields.")
      return
    try :
      if state.renderer is not None and state.db_manager is not None :
        # -- edit mode : update existing client --
        if self.__editing["client"] is not None :
          code = self.__editing["client"]
          state.db_manager.edit_client(codec=code, lastname=lastname, name=name, telephone=tel)
          # -- update in-memory object --
          client = state.cinema.get_client_by_code(code)
          if client :
            client.lastname  = lastname
            client.name      = name
            client.telephone = tel
          messagebox.showinfo(title="success", message=f"client #{code} updated.")
          self.clear_edit_mode("client")
          state.renderer.render_clients(clients_array=state.cinema.clients)
          self.reset_entries(entries_dict=self.client_entries)
          state.renderer.refresh_stats()
          return

        # -- add mode : insert new client --
        date_now = datetime.now().strftime("%Y-%m-%d")
        code     = state.db_manager.insert_client(lastname, name, tel, date_now)
        if code is None :
          messagebox.showerror(title="error", message="failed to add client to database.")
          return
        messagebox.showinfo(title="success", message=f"client added, code: {code}")
        client = Client(code=code, lastname=lastname, name=name, telephone=tel, date=date_now)
        state.cinema.add_client(client)
        state.renderer.render_clients(clients_array=state.cinema.clients)
        self.reset_entries(entries_dict=self.client_entries)
        state.renderer.refresh_stats()

    except Exception as e :
      messagebox.showerror(title="error", message=f"invalid inputs : {e}")

  # ---- add seance ----
  def add_seance(self) :
    film_code, date, time, places, price = self.seance_entries["film code"].get().strip(), self.seance_entries["YYYY-MM-DD"].get().strip(), self.seance_entries["HH:mm"].get().strip(), self.seance_entries["places"].get().strip(), self.seance_entries["price (DH)"].get().strip()
    if film_code in ("", "film code") or time in ("", "HH:mm") or places in ("", "places") or price in ("", "price (DH)") :
      messagebox.showerror(title="error", message="please fill all fields.")
      return

    # ---- validate date ----
    if date in ("", "YYYY-MM-DD") :
      messagebox.showerror(title="error", message="please select a valid date.")
      return
    try :
      parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError :
      messagebox.showerror(title="error", message="invalid date format, use YYYY-MM-DD.")
      return
    if parsed_date < datetime.now().date() :
      messagebox.showerror(title="error", message="date cannot be in the past.")
      return

    try :
      datetime.strptime(time, "%H:%M")
    except ValueError :
      try :
        datetime.strptime(time, "%H:%M:%S")
      except ValueError :
        messagebox.showerror(title="error", message="invalid time format, use HH:mm.")
        return

    try :
      film_code  = int(film_code)
      price      = float(price)
      places     = int(places)

      if places <= 0 :
        messagebox.showerror(title="error", message="places must be greater than 0.")
        return

      date_heure = f"{date}|{time}"

      film_exists = state.cinema.get_film_by_code(film_code)
      if film_exists is None :
        messagebox.showerror(title="error", message=f"there's no film with this code : {film_code}")
        return

      if state.renderer is not None and state.db_manager is not None :
        # -- edit mode : update existing seance --
        if self.__editing["seance"] is not None :
          code = self.__editing["seance"]
          seance = state.cinema.get_seance_by_code(code)
          if seance is None :
            messagebox.showerror(title="error", message="seance not found.")
            return
          reserved = seance.places_totales - seance.places_disponibles
          if places < reserved :
            messagebox.showerror(title="error", message=f"cannot reduce places below {reserved} (already reserved).")
            return
          # -- update in-memory object --
          seance.film               = film_exists
          seance.date_heure         = date_heure
          seance.places_totales     = places
          seance.places_disponibles = places - reserved
          seance.price              = price
          # -- update database --
          state.db_manager.edit_seance(codes=code, film_code=film_code, date_heure=date_heure, nbrt=places, price=price, nbrd=places - reserved)
          messagebox.showinfo(title="success", message=f"seance #{code} updated.")
          self.clear_edit_mode("seance")
          state.renderer.render_seances(state.cinema.seances)
          self.reset_entries(entries_dict=self.seance_entries)
          state.renderer.refresh_stats()
          return

        # -- add mode : insert new seance --
        code = state.db_manager.insert_seance(film=film_exists, date_heure=date_heure, nbrt=places, price=price) 
        if code is None :
          messagebox.showerror(title="error", message="failed to add seance to database.")
          return
        messagebox.showinfo(title="success", message=f"seance added, code : {code}")
        seance = Seance(code=code, film=film_exists, date_heure=date_heure, nbrt=places, price=price)
        state.cinema.add_seance(seance)
        state.renderer.render_seances(state.cinema.seances)
        self.reset_entries(entries_dict=self.seance_entries)
        state.renderer.refresh_stats()

    except Exception as e :
      messagebox.showerror(title="error", message=f"invalid inputs : {e}")

  # ---- add film ----
  def add_film(self) :
    title, genre, duration = self.film_entries["film title"].get(), self.film_entries["genre"].get(), self.film_entries["duration (min)"].get()
    if title in ("", "film title") or genre in ("", "genre") or duration in ("", "duration (min)") :
      messagebox.showerror(title="error", message="please fill all fields.")
      return
    try :
      if state.renderer is not None and state.db_manager is not None :
        # -- edit mode : update existing film --
        if self.__editing["film"] is not None :
          code = self.__editing["film"]
          state.db_manager.edit_film(codef=code, title=title, genre=genre, duree=int(duration))
          # -- update in-memory object --
          film = state.cinema.get_film_by_code(code)
          if film :
            film.title = title
            film.genre = genre
            film.duree = int(duration)
          messagebox.showinfo(title="success", message=f"film #{code} updated.")
          self.clear_edit_mode("film")
          state.renderer.render_films(films_array=state.cinema.films)
          self.reset_entries(entries_dict=self.film_entries)
          state.renderer.refresh_stats()
          return

        # -- add mode : insert new film --
        code = state.db_manager.insert_film(title=title, genre=genre, duree=int(duration))
        if code is None :
          messagebox.showerror(title="error", message="failed to add film to database.")
          return
        messagebox.showinfo(title="success", message=f"film added, code : {code}")
        film = Film(code=code, title=title, genre=genre, duree=int(duration))
        state.cinema.add_film(film)
        state.renderer.render_films(films_array=state.cinema.films)
        self.reset_entries(entries_dict=self.film_entries)
        state.renderer.refresh_stats()

    except Exception as e :
      messagebox.showerror(title="error", message=f"invalid inputs : {e}")

class SearchHandler :
  def __init__(self, search_vars) :
    self.__search_vars = search_vars

  @property
  def search_vars(self)    : return self.__search_vars
  @search_vars.setter
  def search_vars(self, v) : self.__search_vars = v
    
  def get_clean_query(self, key) :
    query = self.search_vars[key].get().lower().strip()
    # ignore the default placeholder text.
    return "" if query == "search..." else query

  # ---- filter clients ----
  def filter_clients(self) :
    search = self.get_clean_query(key="clients")

    clients = state.cinema.clients
    if search :
      clients = [c for c in clients if search in c.name.lower() or search in c.lastname.lower() or search in c.telephone.lower() or str(c.code) == search]

    state.renderer.render_clients(clients_array=clients)

  # ---- filter seances ----
  def filter_seances(self) :
    search = self.get_clean_query(key="seances")
    
    # get the unfiltered array.
    seances = state.cinema.seances
    if search :
      seances = [s for s in seances if str(s.code) == search or search in s.film.title.lower() or search in s.date_heure.lower() or search in f"{str(s.places_disponibles)}/{str(s.places_totales)}" or str(s.price) == search]

    state.renderer.render_seances(seances_array=seances)

  # ---- filter films ----
  def filter_films(self) :
    search = self.get_clean_query(key="films")
    
    # get the unfiltered array.
    films = state.cinema.films
    if search :
      films = [f for f in films if str(f.code) == search or search in f.title.lower() or search in f.genre.lower() or str(f.duree) == search ]

    state.renderer.render_films(films_array=films)

class SelectHandler :
  def __init__(self, client_treeview, seance_treeview, film_treeview) :
    self.__client_treeview = client_treeview
    self.__seance_treeview = seance_treeview
    self.__film_treeview   = film_treeview

  @property 
  def client_treeview(self)    : return self.__client_treeview
  @client_treeview.setter
  def client_treeview(self, v) : self.__client_treeview = v
  @property
  def seance_treeview(self)    : return self.__seance_treeview
  @seance_treeview.setter
  def seance_treeview(self, v) : self.__seance_treeview = v
  @property
  def film_treeview(self)      : return self.__film_treeview
  @film_treeview.setter
  def film_treeview(self, v)   : self.__film_treeview = v
    
  def on_client_select(self, client_id_entry, event=None) :
    selected = self.client_treeview.selection()
    if selected :
      code = self.client_treeview.item(selected[0], "values")[0]
      client_id_entry.delete(0, "end")
      client_id_entry.insert(0, str(code))
      client_id_entry.configure(foreground="black")

  def on_seance_select(self, seance_id_entry, event=None) :
    selected = self.seance_treeview.selection()
    if selected :
      code = self.seance_treeview.item(selected[0], "values")[0]
      seance_id_entry.delete(0, "end")
      seance_id_entry.insert(0, str(code))
      seance_id_entry.configure(foreground="black")

  def on_film_select(self, film_id_entry, event=None) :
    selected = self.film_treeview.selection()
    if selected :
      code = self.film_treeview.item(selected[0], "values")[0]
      film_id_entry.delete(0, "end")
      film_id_entry.insert(0, str(code))
      film_id_entry.configure(foreground="black")

class RemoveHandler :
  def __init__(self, client_treeview, seance_treeview, film_treeview) :
    self.__client_treeview = client_treeview
    self.__seance_treeview = seance_treeview
    self.__film_treeview   = film_treeview

  @property
  def client_treeview(self)    : return self.__client_treeview
  @client_treeview.setter
  def client_treeview(self, v) : self.__client_treeview = v
  @property
  def seance_treeview(self)    : return self.__seance_treeview
  @seance_treeview.setter
  def seance_treeview(self, v) : self.__seance_treeview = v
  @property
  def film_treeview(self)      : return self.__film_treeview
  @film_treeview.setter
  def film_treeview(self, v)   : self.__film_treeview = v

  def remove_selected_clients(self) :
    selected_items = self.client_treeview.selection()
    if not selected_items :
      messagebox.showwarning(title="warning", message="please select at least one client to remove.")
      return
    
    if messagebox.askyesno(title="confirm", message=f"remove {len(selected_items)} client(s)?") :
      for item in selected_items :
        code = int(self.client_treeview.item(item, "values")[0])

        # ---- restore seats and revenue for removed tickets ----
        affected_seances = {}
        for t in state.cinema.tickets :
          if t.client.code == code and t.etatTicket() == "reserved" :
            t.seance.places_disponibles += 1
            state.cinema.revenus -= t.seance.price
            affected_seances[t.seance.code] = t.seance.places_disponibles
        # -- remove from database --
        if state.db_manager is not None :
          for t in state.cinema.tickets :
            if t.client.code == code :
              state.db_manager.remove_ticket(codet=t.code)
          state.db_manager.remove_client(codec=code)
          # ---- update nbrd in DB for affected seances ----
          for sc, nbrd in affected_seances.items() :
            state.db_manager.update_seance_nbrd(code=sc, nbrd=nbrd)
        # ---- remove from arrays ----
        state.cinema.tickets[:] = [t for t in state.cinema.tickets if t.client.code != code]
        state.cinema.clients[:] = [c for c in state.cinema.clients if c.code != code]
      
      # ---- refresh list & stats ----
      state.renderer.render_clients(clients_array=state.cinema.clients)
      state.renderer.render_seances(seances_array=state.cinema.seances)
      state.renderer.refresh_stats()

  def remove_selected_seances(self) :
    selected_items = self.seance_treeview.selection()
    if not selected_items : 
      messagebox.showwarning(title="warning", message="please select at least one seance to remove.")
      return
    
    if messagebox.askyesno(title="confirm", message=f"remove {len(selected_items)} seance(s)?") :
      for item in selected_items :
        code = int(self.seance_treeview.item(item, "values")[0])

        # ---- restore seats and revenue for removed tickets ----
        for t in state.cinema.tickets :
          if t.seance.code == code and t.etatTicket() == "reserved" :
            t.seance.places_disponibles += 1
            state.cinema.revenus -= t.seance.price
        # -- remove from database --
        if state.db_manager is not None :
          for t in state.cinema.tickets :
            if t.seance.code == code :
              state.db_manager.remove_ticket(codet=t.code)
          state.db_manager.remove_seance(codes=code)
        # ---- remove from arrays ----
        state.cinema.tickets[:] = [t for t in state.cinema.tickets if t.seance.code != code]
        state.cinema.seances[:] = [s for s in state.cinema.seances if s.code != code]
      
      # ---- refresh list & stats ----
      state.renderer.render_seances(seances_array=state.cinema.seances)
      state.renderer.refresh_stats()

  def remove_selected_films(self) :
    selected_items = self.film_treeview.selection()
    if not selected_items :
      messagebox.showwarning(title="warning", message="please select at least one film to remove.") 
      return
    
    if messagebox.askyesno(title="confirm", message=f"remove {len(selected_items)} film(s) ?") :
      for item in selected_items :
        code = int(self.film_treeview.item(item, "values")[0])

        # ---- get linked seances codes ----
        linked_seance_codes     = {s.code for s in state.cinema.seances if s.film.code == code}
        # ---- restore seats and revenue for removed tickets ----
        for t in state.cinema.tickets :
          if t.seance.code in linked_seance_codes and t.etatTicket() == "reserved" :
            t.seance.places_disponibles += 1
            state.cinema.revenus -= t.seance.price
        # -- remove from database --
        if state.db_manager is not None :
          for t in state.cinema.tickets :
            if t.seance.code in linked_seance_codes :
              state.db_manager.remove_ticket(codet=t.code)
          for sc in linked_seance_codes :
            state.db_manager.remove_seance(codes=sc)
          state.db_manager.remove_film(codef=code)
        # --- remove from arrays ----
        state.cinema.tickets[:] = [t for t in state.cinema.tickets if t.seance.code not in linked_seance_codes]
        state.cinema.seances[:] = [s for s in state.cinema.seances if s.code not in linked_seance_codes]
        state.cinema.films[:]   = [f for f in state.cinema.films if f.code != code]
      
      # ---- refresh list & stats ----
      state.renderer.render_films(films_array=state.cinema.films)
      state.renderer.render_seances(seances_array=state.cinema.seances)
      state.renderer.refresh_stats()

class ReservationHandler :
  def __init__(self, client_id_entry, seance_id_entry, ticket_id_entry) :
    self.__client_id_entry = client_id_entry
    self.__seance_id_entry = seance_id_entry
    self.__ticket_id_entry = ticket_id_entry

  @property
  def client_id_entry(self)    : return self.__client_id_entry
  @client_id_entry.setter
  def client_id_entry(self, v) : self.__client_id_entry = v
  @property
  def seance_id_entry(self)    : return self.__seance_id_entry
  @seance_id_entry.setter
  def seance_id_entry(self, v) : self.__seance_id_entry = v
  @property
  def ticket_id_entry(self)    : return self.__ticket_id_entry
  @ticket_id_entry.setter
  def ticket_id_entry(self, v) : self.__ticket_id_entry = v

  def reserve_ticket(self, treeview_clients) :
    try :
      client_code = int(self.client_id_entry.get())
      seance_code = int(self.seance_id_entry.get())

      ticket, status = state.cinema.reserver_ticket(codec=client_code, codes=seance_code)

      if status == "ok" and ticket :
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # ----
        code = state.db_manager.insert_ticket(client=client_code, seance=seance_code, date=now)
        # ----
        if code is None :
          # ---- rollback in-memory state ----
          state.cinema.tickets.pop()
          seance_obj = state.cinema.get_seance_by_code(seance_code)
          client_obj = state.cinema.get_client_by_code(client_code)
          if seance_obj :
            seance_obj.places_disponibles += 1
            state.cinema.revenus -= seance_obj.price
          if client_obj and client_obj.history :
            client_obj.history.pop()
          messagebox.showerror(title="error", message="failed to add ticket to database.")
          return
        ticket.code = code
        # ---- update nbrd in DB ----
        if state.db_manager is not None :
          seance_obj = state.cinema.get_seance_by_code(seance_code)
          if seance_obj :
            state.db_manager.update_seance_nbrd(code=seance_code, nbrd=seance_obj.places_disponibles)
        messagebox.showinfo(title="success", message=f"reserved, ticket : #{code}")
        state.renderer.render_seances(seances_array=state.cinema.seances)
        # ---- refresh stats ----
        state.renderer.refresh_stats()
        # ---- resest fields ----
        self.client_id_entry.delete(0, "end")
        self.client_id_entry.insert(0, "client ID")
        self.client_id_entry.configure(foreground="gray")
        self.seance_id_entry.delete(0, "end")
        self.seance_id_entry.insert(0, "seance ID")
        self.seance_id_entry.configure(foreground="gray")
        # ---- unselect the client treeview after reservation ----
        treeview_clients.selection_set()

      elif status == "no_places" :
        messagebox.showerror(title="error", message="no places available.")
      else :
        messagebox.showerror(title="error", message="client or seance not found.")

    except Exception as e :
      messagebox.showerror(title="error", message=f"enter valid numbers : {e}")

  def cancel_ticket(self) :
    try :
      ticket_code = int(self.ticket_id_entry.get())

      if state.cinema.cancel_ticket(codeTicket=ticket_code) :
        if state.db_manager is not None :
          state.db_manager.edit_ticket(codet=ticket_code, etat="canceled")
          # ---- update nbrd in DB ----
          for t in state.cinema.tickets :
            if t.code == ticket_code :
              state.db_manager.update_seance_nbrd(code=t.seance.code, nbrd=t.seance.places_disponibles)
              break
        messagebox.showinfo(title="success", message=f"ticket #{ticket_code} cancelled.")
        # ---- refresh stats ----
        state.renderer.refresh_stats()
        state.renderer.render_seances(seances_array=state.cinema.seances)
        # ---- reset fields ----
        self.ticket_id_entry.delete(0, "end")
        self.ticket_id_entry.insert(0, "ticket ID")
        self.ticket_id_entry.configure(foreground="gray")
      else :
        messagebox.showerror(title="error", message="ticket not found or already cancelled.")

    except Exception as e :
      messagebox.showerror(title="error", message=f"enter a valid ticket ID : {e}")

class EditHandler :
  def __init__(self, client_treeview, seance_treeview, film_treeview, add_handler, btn_add_client, btn_add_seance, btn_add_film) :
    self.__client_treeview = client_treeview
    self.__seance_treeview = seance_treeview
    self.__film_treeview   = film_treeview
    self.__add_handler     = add_handler
    self.__btn_add_client  = btn_add_client
    self.__btn_add_seance  = btn_add_seance
    self.__btn_add_film    = btn_add_film

  @property
  def client_treeview(self)    : return self.__client_treeview 
  @client_treeview.setter
  def client_treeview(self, v) : self.__client_treeview = v 
  @property
  def seance_treeview(self)    : return self.__seance_treeview
  @seance_treeview.setter
  def seance_treeview(self, v) : self.__seance_treeview = v
  @property
  def film_treeview(self)      : return self.__film_treeview
  @film_treeview.setter
  def film_treeview(self, v)   : self.__film_treeview = v

  def _enter_edit_mode(self, btn, label) :
    btn.configure(text=f"✎ update {label}", style="Edit.TButton")

  def _exit_edit_mode(self, btn, label) :
    btn.configure(text=f"+ add {label}", style="Add.TButton")

  def edit_selected_client(self, client_entries) :
    # -- if already editing, cancel --
    if self.__add_handler.editing["client"] is not None :
      self.__add_handler.clear_edit_mode("client")
      self.__add_handler.reset_entries(entries_dict=client_entries)
      return

    selected_clients = self.client_treeview.selection()
    if len(selected_clients) < 1 :
      messagebox.showerror(title="error", message="please select a client to edit.")
    elif len(selected_clients) > 1 :
      messagebox.showerror(title="error", message="please select just one client to edit.")
    elif len(selected_clients) == 1 :
      item  = selected_clients[0]
      code  = int(self.client_treeview.item(item, "values")[0])
      name     = self.client_treeview.item(item, "values")[1]
      lastname = self.client_treeview.item(item, "values")[2]
      phone    = self.client_treeview.item(item, "values")[3]

      client_entries["name"].delete(0, "end")
      client_entries["name"].insert(0, name)
      client_entries["name"].configure(foreground="black")

      client_entries["lastname"].delete(0, "end")
      client_entries["lastname"].insert(0, lastname)
      client_entries["lastname"].configure(foreground="black")
      
      client_entries["phone"].delete(0, "end")
      client_entries["phone"].insert(0, phone)
      client_entries["phone"].configure(foreground="black")

      self.__add_handler.set_edit_mode("client", code, revert_callback=lambda: self._exit_edit_mode(self.__btn_add_client, "client"))
      self._enter_edit_mode(self.__btn_add_client, "client")

  def edit_selected_seance(self, seance_entries) :
    # -- if already editing, cancel --
    if self.__add_handler.editing["seance"] is not None :
      self.__add_handler.clear_edit_mode("seance")
      self.__add_handler.reset_entries(entries_dict=seance_entries)
      return

    selected_seances = self.seance_treeview.selection()
    if len(selected_seances) < 1 :
      messagebox.showerror(title="error", message="please select a seance to edit.")
    elif len(selected_seances) > 1 :
      messagebox.showerror(title="error", message="please select just one seance to edit.")
    elif len(selected_seances) == 1 :
      item   = selected_seances[0]
      code   = int(self.seance_treeview.item(item, "values")[0])
      seance = state.cinema.get_seance_by_code(code)
      if seance is None :
        messagebox.showerror(title="error", message="seance not found.")
        return

      film_code = str(seance.film.code)
      date_heure = seance.date_heure
      places = str(seance.places_totales)
      price  = str(seance.price)

      seance_entries["film code"].delete(0, "end")
      seance_entries["film code"].insert(0, film_code)
      seance_entries["film code"].configure(foreground="black")

      if hasattr(seance_entries["YYYY-MM-DD"], 'set_date') :
        try :
          date_str = date_heure.split("|")[0] if "|" in date_heure else date_heure.split(" ")[0]
          try :
            parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
          except ValueError :
            parsed = datetime.strptime(date_str, "%d-%m-%y").date()
          seance_entries["YYYY-MM-DD"].set_date(parsed)
        except (ValueError, IndexError) as e :
          messagebox.showwarning(title="warning", message=f"could not parse date: {e}")
      else :
        date_part = date_heure.split("|")[0] if "|" in date_heure else date_heure.split(" ")[0]
        seance_entries["YYYY-MM-DD"].delete(0, "end")
        seance_entries["YYYY-MM-DD"].insert(0, date_part)
        seance_entries["YYYY-MM-DD"].configure(foreground="black")

      seance_entries["HH:mm"].delete(0, "end")
      if "|" in date_heure :
        seance_entries["HH:mm"].insert(0, date_heure.split("|")[1])
      elif " " in date_heure :
        seance_entries["HH:mm"].insert(0, date_heure.split(" ")[1])
      else :
        seance_entries["HH:mm"].insert(0, "")
      seance_entries["HH:mm"].configure(foreground="black")

      seance_entries["places"].delete(0, "end")
      seance_entries["places"].insert(0, places)
      seance_entries["places"].configure(foreground="black")

      seance_entries["price (DH)"].delete(0, "end")
      seance_entries["price (DH)"].insert(0, price)
      seance_entries["price (DH)"].configure(foreground="black")

      self.__add_handler.set_edit_mode("seance", code, revert_callback=lambda: self._exit_edit_mode(self.__btn_add_seance, "seance"))
      self._enter_edit_mode(self.__btn_add_seance, "seance")

  def edit_selected_film(self, film_entries) :
    # -- if already editing, cancel --
    if self.__add_handler.editing["film"] is not None :
      self.__add_handler.clear_edit_mode("film")
      self.__add_handler.reset_entries(entries_dict=film_entries)
      return

    selected_films = self.film_treeview.selection()
    if len(selected_films) < 1 :
      messagebox.showerror(title="error", message="please select a film to edit.")
    elif len(selected_films) > 1 :
      messagebox.showerror(title="error", message="please select just one film to edit.")
    elif len(selected_films) == 1 :
      item  = selected_films[0]
      code  = int(self.film_treeview.item(item, "values")[0])
      title    = self.film_treeview.item(item, "values")[1]
      genre    = self.film_treeview.item(item, "values")[2]
      duration = self.film_treeview.item(item, "values")[3].replace(" min", "")

      film_entries["film title"].delete(0, "end")
      film_entries["film title"].insert(0, title)
      film_entries["film title"].configure(foreground="black")

      film_entries["genre"].delete(0, "end")
      film_entries["genre"].insert(0, genre)
      film_entries["genre"].configure(foreground="black")

      film_entries["duration (min)"].delete(0, "end")
      film_entries["duration (min)"].insert(0, duration)
      film_entries["duration (min)"].configure(foreground="black")

      self.__add_handler.set_edit_mode("film", code, revert_callback=lambda: self._exit_edit_mode(self.__btn_add_film, "film"))
      self._enter_edit_mode(self.__btn_add_film, "film")
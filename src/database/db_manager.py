import os
import threading
from tkinter import messagebox
from supabase import create_client

from src.core import Client, Film, Seance, Ticket
from src.gui import state

class DatabaseManager :
  def __init__(self, root) :
    self.__root = root
    url = os.environ.get("SUPABASE_URL") or "https://uxkhckyypfsdoclxxyfa.supabase.co"
    key = os.environ.get("SUPABASE_KEY") or "sb_publishable_YqzXyD44U_ZkDNeycTw5HA_0wCegTk8"
    self.__supabase = create_client(url, key)

  @property
  def supabase(self) : return self.__supabase

  def setup_data(self) :
    def _fetch() :
      try :
        clients_data  = self.supabase.table(table_name="clients").select("*").execute().data
        films_data    = self.supabase.table(table_name="films").select("*").execute().data
        seances_data  = self.supabase.table(table_name="seances").select("*").execute().data
        tickets_data  = self.supabase.table(table_name="tickets").select("*").execute().data
        self.__root.after(0, lambda: self._render_all(clients_data, films_data, seances_data, tickets_data))
      except Exception as e :
        self.__root.after(0, lambda e=e: messagebox.showerror(title="error", message=f"failed to load data: {e}"))

    threading.Thread(target=_fetch, daemon=True).start()

  def _render_all(self, clients_data, films_data, seances_data, tickets_data=None) :
    if tickets_data is None :
      tickets_data = []
    # -- clients --
    for c in clients_data :
       client = Client(code=c["code"], lastname=c["lastname"], name=c["name"], telephone=c["telephone"], date=c.get("date") or "")
       state.cinema.add_client(client)
    if state.renderer is not None :
      state.renderer.render_clients(clients_array=state.cinema.clients)

    # -- films --
    for f in films_data :
      film = Film(code=f["code"], title=f["title"], genre=f["genre"], duree=f["duree"], description=f.get("description", ""))
      state.cinema.add_film(film)
    if state.renderer is not None :
      state.renderer.render_films(films_array=state.cinema.films)

    # -- seances --
    film_map = {f.code: f for f in state.cinema.films}
    for s in seances_data :
      matching_film = film_map.get(s["film"])
      if matching_film is not None :
        seance = Seance(code=s["code"], film=matching_film, date_heure=s["date_heure"].replace("T", "|"), nbrt=int(s["nbrt"]), price=float(s["price"]), status=s.get("status") or "active")
        state.cinema.add_seance(seance)
    # -- tickets --
    client_map = {c.code : c for c in state.cinema.clients}
    seance_map = {s.code : s for s in state.cinema.seances}
    max_ticket_code = 0
    for t in tickets_data :
      client_ref = client_map.get(t["client"])
      seance_ref = seance_map.get(t["seance"])
      if client_ref is not None and seance_ref is not None :
        etat = t.get("etat", "reserved")
        ticket = Ticket(code=t["code"], client=client_ref, seance=seance_ref, date=t.get("date", ""), etat=etat)
        state.cinema.tickets.append(ticket)
        if etat == "reserved" :
          seance_ref.places_disponibles -= 1
          state.cinema.revenus += seance_ref.price
        if t["code"] > max_ticket_code :
          max_ticket_code = t["code"]
    Ticket.cpt = max_ticket_code + 1

    # -- sync nbrd in DB for all seances (recalculated from tickets) --
    if state.db_manager is not None :
      for seance in state.cinema.seances :
        state.db_manager.update_seance_nbrd(code=seance.code, nbrd=seance.places_disponibles)

    if clients_data :
      Client.cpt = max(c["code"] for c in clients_data) + 1
    if films_data :
      Film.cpt = max(f["code"] for f in films_data) + 1
    if seances_data :
      Seance.cpt = max(s["code"] for s in seances_data) + 1

    # -- re-render seances after tickets so seats are correct --
    if state.renderer is not None :
      state.renderer.render_seances(seances_array=state.cinema.seances)

    # -- refresh stats --
    if state.renderer is not None :
      state.renderer.refresh_stats()

  def insert_client(self, lastname, name, tel, date_now) :
    response = self.supabase.table(table_name="clients").insert({"lastname":lastname, "name":name, "telephone":tel, "date":date_now}).execute()
    if response.data :
      inserted_client = response.data[0]
      return inserted_client.get("code")
    return None

  def insert_seance(self, film, date_heure, nbrt, price) :
    response = self.supabase.table(table_name="seances").insert({"film":film.code, "date_heure":date_heure, "nbrt":nbrt, "nbrd":nbrt, "price":price}).execute()
    if response.data :
      inserted_seance = response.data[0]
      return inserted_seance.get("code")
    return None

  def insert_film(self, title, genre, duree) :
    response = self.supabase.table(table_name="films").insert({"title":title, "genre":genre, "duree":duree}).execute()
    if response.data :
      inserted_film = response.data[0]
      return inserted_film.get("code")
    return None

  def insert_ticket(self, client, seance, date) :
    response = self.supabase.table(table_name="tickets").insert({"client":client, "seance":seance, "date":date}).execute()
    if response.data :
      inserted_ticket = response.data[0]
      return inserted_ticket.get("code")
    return None

  def remove_client(self, codec) :
    self.supabase.table(table_name="clients").delete().eq("code", codec).execute()

  def remove_seance(self, codes) :
    self.supabase.table(table_name="seances").delete().eq("code", codes).execute()

  def remove_film(self, codef) :
    self.supabase.table(table_name="films").delete().eq("code", codef).execute()

  def edit_client(self, codec, lastname, name, telephone) :
    self.supabase.table(table_name="clients").update({"lastname":lastname, "name":name, "telephone":telephone}).eq("code", codec).execute()

  def edit_seance(self, codes, film_code, date_heure, nbrt, price, nbrd=None) :
    data = {"film":film_code, "date_heure":date_heure, "nbrt":nbrt, "price":price}
    if nbrd is not None :
      data["nbrd"] = nbrd
    self.supabase.table(table_name="seances").update(data).eq("code", codes).execute()

  def edit_film(self, codef, title, genre, duree) :
    self.supabase.table(table_name="films").update({"title":title, "genre":genre, "duree":duree}).eq("code", codef).execute()

  def edit_ticket(self, codet, etat) :
    self.supabase.table(table_name="tickets").update({"etat":etat}).eq("code", codet).execute()

  def remove_ticket(self, codet) :
    self.supabase.table(table_name="tickets").delete().eq("code", codet).execute()

  def update_seance_nbrd(self, code, nbrd) :
    self.supabase.table(table_name="seances").update({"nbrd":nbrd}).eq("code", code).execute()


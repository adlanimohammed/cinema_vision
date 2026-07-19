import tkinter as tk
from tkinter  import ttk
try :
  from tkcalendar import DateEntry
except ImportError :
  DateEntry = None

from src.gui import state
from src.gui.views import Renderer

from src.gui.handlers import AddHandler, SearchHandler, SelectHandler, RemoveHandler, EditHandler, ReservationHandler
from src.gui.widgets import on_entry_click, on_focus_out

from src.database.db_manager import DatabaseManager

class CinemaApp :
  def __init__(self) :
    # ---- main window setup ----
    self.root = tk.Tk()
    self.root.title("cinema vision")
    self.root.geometry("1400x850")
    self.root.configure(bg="#FFAE6E")

    # ---- configure UI styles ----
    self.setup_styles()

    # ---- build layout ----
    self.build_header()
    self.build_tabs()
    self.build_manager_columns()

    # ---- build sub-panels ----
    self.build_client_panel()
    self.build_seance_panel()
    self.build_film_panel()
    self.build_action_panel()

    self.build_stats_panel()

    # ---- instantiate Handlers & Observers ----
    self.init_handlers()

    # --- setup data (deferred so window renders first) ---
    self.root.after(100, state.db_manager.setup_data)

  def setup_styles(self) :
    self.style = ttk.Style(self.root)
    self.style.theme_use('clam')
    # add Hover for Buttons.
    self.style.map("Cancel.TButton",  background=[("active", "#C0392B")])
    self.style.map("Delete.TButton",  background=[("active", "#C0392B")])
    self.style.map("Edit.TButton",    background=[("active", "#222222")], foreground=[("active", "#ccc")])
    self.style.map("Reserve.TButton", background=[("active", "#8FDDDF")])
    self.style.map("Add.TButton",     background=[("active", "#FFAE6E")])
    # add style for inputs.
    self.style.configure("TEntry", foreground="gray", bordercolor="#CCCCCC", lightcolor="#CCCCCC", darkcolor="#CCCCCC")
    self.style.map("TEntry", bordercolor=[("focus", "#EC6530")], lightcolor=[("focus", "#EC6530")], darkcolor=[("focus", "#EC6530")])

    self.style.configure("Seance.Vertical.TScrollbar",
        gripcount=0,
        background="#EC6530",      # Cinema Orange thumb
        troughcolor="#f5f6fa",     # Track background
        bordercolor="#f5f6fa",     # Track border
        arrowcolor="#2f3542"       # Arrow heads
    )

    self.style.map("Seance.Vertical.TScrollbar",
        background=[
            ('pressed', '#B84518'),  # Darker orange on click
            ('active',  '#FF8252')   # Brighter orange on hover
        ],
        arrowcolor=[
            ('pressed', '#ffffff'),  # White arrows on click
            ('active',  '#ffffff')   # White arrows on hover
        ]
    )

    # --- client scrollbar ---
    self.style.configure("Client.Vertical.TScrollbar",
      gripcount=0, background="#8ECA3C", troughcolor="#f5f6fa", bordercolor="#f5f6fa", arrowcolor="#2f3542"    )
    self.style.map("Client.Vertical.TScrollbar",
        background=[('pressed', '#629322'), ('active', '#A2DE4E')],
        arrowcolor=[('pressed', '#ffffff'), ('active', '#ffffff')]
    )

    # --- film scrollbar ---
    self.style.configure("Film.Vertical.TScrollbar",
        gripcount=0, background="#2EA2DB", troughcolor="#f5f6fa", bordercolor="#f5f6fa", arrowcolor="#2f3542"
    )
    self.style.map("Film.Vertical.TScrollbar",
        background=[('pressed', '#1B6F98'), ('active', '#52BEF5')],
        arrowcolor=[('pressed', '#ffffff'), ('active', '#ffffff')]
    )

    # ----  
    self.style.map("Seance.Treeview", background=[("selected", "#FFCA95")], foreground=[("selected", "black")])
    self.style.map("Client.Treeview", background=[("selected", "#C2F185")], foreground=[("selected", "black")])
    self.style.map("Film.Treeview",   background=[("selected", "#A2E1FC")], foreground=[("selected", "black")])

  def build_header(self) :
    self.header = tk.Frame(self.root, height=85, bg="#EC6530")
    self.header.pack(fill="x")
    
    self.title_label = tk.Label(self.header, text="cinema vision", font=("Segoe UI", 40, "bold"), fg="#ecf0f1", bg="#EC6530")
    self.title_label.pack(expand=True)

  def build_tabs(self) :
    self.notebook = ttk.Notebook(self.root)
    self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    self.tab_cinema  = ttk.Frame(self.notebook)
    self.tab_statics = ttk.Frame(self.notebook)
    
    self.notebook.add(self.tab_cinema, text="cinema manager")
    self.notebook.add(self.tab_statics, text="statistics")
    # ---
    self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

  def build_manager_columns(self) :
    self.tab_cinema.columnconfigure(0, weight=1, uniform="col")
    self.tab_cinema.columnconfigure(1, weight=1, uniform="col")
    self.tab_cinema.columnconfigure(2, weight=1, uniform="col")
    self.tab_cinema.rowconfigure(0, weight=1)

    self.left = ttk.Frame(self.tab_cinema)
    self.left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
    
    self.middle = ttk.Frame(self.tab_cinema)
    self.middle.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
   
    self.right = ttk.Frame(self.tab_cinema)
    self.right.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)

  def build_client_panel(self) :
    # frame layout.
    self.client_frame = ttk.LabelFrame(self.left, text="add client")
    self.client_frame.pack(fill="x", padx=5, pady=(0, 10), ipady=5)

    self.inner = ttk.Frame(self.client_frame)
    self.inner.pack(fill="x", padx=10, pady=5)

    self.row1 = ttk.Frame(self.inner)
    self.row1.pack(fill="x")

    # fields.
    self.client_lastname = ttk.Entry(self.row1)
    self.client_lastname.pack(side="left", fill="x", expand=True, padx=(0, 5))
    self.client_lastname.insert(0, "lastname")
    # set placeholder.
    self.client_lastname.bind("<FocusIn>",  lambda e : on_entry_click(self.client_lastname, "lastname"))
    self.client_lastname.bind("<FocusOut>", lambda e : on_focus_out(self.client_lastname, "lastname"))
    # set autofocus.
    self.client_lastname.focus_set()

    self.client_name = ttk.Entry(self.row1)
    self.client_name.pack(side="left", fill="x", expand=True)
    self.client_name.insert(0, "name")
    # set placeholder.
    self.client_name.bind("<FocusIn>",  lambda e : on_entry_click(self.client_name, "name"))
    self.client_name.bind("<FocusOut>", lambda e : on_focus_out(self.client_name, "name"))

    self.client_tel = ttk.Entry(self.inner)
    self.client_tel.pack(fill="x")
    self.client_tel.insert(0, "phone")
    # set placeholder.
    self.client_tel.bind("<FocusIn>",  lambda e : on_entry_click(self.client_tel, "phone"))
    self.client_tel.bind("<FocusOut>", lambda e : on_focus_out(self.client_tel, "phone"))

    # ---- entry dictionary references for AddHandler mapping ----
    self.client_entries = {
      "name"     : self.client_name,
      "lastname" : self.client_lastname,
      "phone"    : self.client_tel
    }
    # -------
    self.btn_add_client = ttk.Button(self.client_frame, text="+ add client", style="Add.TButton", command=lambda: self.add_handler.add_client())
    self.btn_add_client.pack(fill="x", padx=10, pady=2)
    
    # ---- tree list display ----
    self.client_list = ttk.Frame(self.left)
    self.client_list.pack(fill="both", expand=True, padx=5)

    self.header_top = ttk.Frame(self.client_list)
    self.header_top.pack(fill="x", pady=(0, 5))

    ttk.Label(self.header_top, text="clients", style="Header.TLabel").pack(side="left")

    self.client_search_var = tk.StringVar()

    self.client_search_entry = ttk.Entry(self.header_top, textvariable=self.client_search_var, width=20)
    self.client_search_entry.pack(side="left", padx=15)
    self.client_search_entry.insert(0, "search...")
    # set placeholder for search input.
    self.client_search_entry.bind("<FocusIn>",  lambda e : on_entry_click(self.client_search_entry, "search..."))
    self.client_search_entry.bind("<FocusOut>", lambda e : on_focus_out(self.client_search_entry, "search..."))

    # add edit/delete buttons.
    ttk.Button(self.header_top, text="🗑", width=3, style="Delete.TButton", command=lambda : self.remove_handler.remove_selected_clients()).pack(side="right")
    ttk.Button(self.header_top, text="✎", width=3, style="Edit.TButton", command=lambda: self.edit_handler.edit_selected_client(client_entries=self.client_entries)).pack(side="right")

    self.columns = ("code", "name", "lastname", "phone")
    self.tree_clients = ttk.Treeview(self.client_list, style="Client.Treeview", columns=self.columns, show="headings")
    self.tree_clients.heading("code",     text="code")
    self.tree_clients.heading("name",     text="name")
    self.tree_clients.heading("lastname", text="lastname")
    self.tree_clients.heading("phone",    text="phone")

    self.tree_clients.column("code",     width=50,  anchor="center")
    self.tree_clients.column("name",     width=100, anchor="center")
    self.tree_clients.column("lastname", width=100, anchor="center")
    self.tree_clients.column("phone",    width=100, anchor="center")

    self.scrollbar = ttk.Scrollbar(self.client_list, style="Client.Vertical.TScrollbar", orient=tk.VERTICAL, command=self.tree_clients.yview)
    self.tree_clients.configure(yscroll=self.scrollbar.set)

    self.tree_clients.pack(side="left", fill="both", expand=True)
    self.scrollbar.pack(side="right", fill="y")

    # update the client ID entry field of quick reserve with the selected client's code from the treeview 
    self.tree_clients.bind("<<TreeviewSelect>>", lambda e : self.select_handler.on_client_select(client_id_entry=self.reserve_client))

  def build_seance_panel(self) :
    # frame layout.
    self.seance_frame = ttk.LabelFrame(self.middle, text="add seance")
    self.seance_frame.pack(fill="x", pady=(0, 10), padx=5, ipady=5)

    self.inner = ttk.Frame(self.seance_frame)
    self.inner.pack(fill="x", padx=10, pady=5)

    self.row1 = ttk.Frame(self.inner)
    self.row1.pack(fill="x")

    # fields.
    self.seance_film = ttk.Entry(self.row1)
    self.seance_film.pack(side="left", fill="x", expand=True, padx=(0, 5))
    self.seance_film.insert(0, "film code")
    # set placeholder.
    self.seance_film.bind("<FocusIn>",  lambda e : on_entry_click(self.seance_film, "film code"))
    self.seance_film.bind("<FocusOut>", lambda e : on_focus_out(self.seance_film, "film code"))

    if DateEntry is not None :
      self.seance_time = DateEntry(self.row1, date_pattern='yyyy-MM-dd')
    else :
      self.seance_time = ttk.Entry(self.row1)
      self.seance_time.insert(0, "YYYY-MM-DD")
      self.seance_time.bind("<FocusIn>",  lambda e : on_entry_click(self.seance_time, "YYYY-MM-DD"))
      self.seance_time.bind("<FocusOut>", lambda e : on_focus_out(self.seance_time, "YYYY-MM-DD"))
    self.seance_time.pack(side="left")

    self.seance_time_hm = ttk.Entry(self.row1)
    self.seance_time_hm.pack(side="left")
    self.seance_time_hm.insert(0, "HH:mm")
    # set placeholder.
    self.seance_time_hm.bind("<FocusIn>",  lambda e : on_entry_click(self.seance_time_hm, "HH:mm"))
    self.seance_time_hm.bind("<FocusOut>", lambda e : on_focus_out(self.seance_time_hm, "HH:mm"))

    self.row2 = ttk.Frame(self.inner)
    self.row2.pack(fill="x")

    self.seance_places = ttk.Entry(self.row2)
    self.seance_places.pack(side="left", fill="x", expand=True, padx=(0, 5))
    self.seance_places.insert(0, "places")
    # set placeholder.
    self.seance_places.bind("<FocusIn>",  lambda e : on_entry_click(self.seance_places, "places"))
    self.seance_places.bind("<FocusOut>", lambda e : on_focus_out(self.seance_places, "places"))

    self.seance_price = ttk.Entry(self.row2)
    self.seance_price.pack(side="left", fill="x", expand=True)
    self.seance_price.insert(0, "price (DH)")
    # set placeholder.
    self.seance_price.bind("<FocusIn>",  lambda e : on_entry_click(self.seance_price, "price (DH)"))
    self.seance_price.bind("<FocusOut>", lambda e : on_focus_out(self.seance_price, "price (DH)"))

    # ---- entry dictionary ----
    self.seance_entries = {
      "film code"  : self.seance_film,
      "YYYY-MM-DD" : self.seance_time,
      "HH:mm"      : self.seance_time_hm,
      "places"     : self.seance_places,
      "price (DH)" : self.seance_price
    }
    # ----------
    self.btn_add_seance = ttk.Button(self.seance_frame, text="+ add seance", style="Add.TButton", command=lambda: self.add_handler.add_seance())
    self.btn_add_seance.pack(fill="x", padx=10, pady=2)

    # ---- display list ----
    self.seances_list = ttk.Frame(self.middle)
    self.seances_list.pack(fill="both", expand=True, padx=5)

    self.header_top = ttk.Frame(self.seances_list)
    self.header_top.pack(fill="x", pady=(0, 5))

    ttk.Label(self.header_top, text="seances", style="Header.TLabel").pack(side="left")

    self.seances_search_var = tk.StringVar()

    self.seances_search_entry = ttk.Entry(self.header_top, textvariable=self.seances_search_var, width=20)
    self.seances_search_entry.pack(side="left", padx=15)
    self.seances_search_entry.insert(0, "search...")
    # set placeholder for search input.
    self.seances_search_entry.bind("<FocusIn>",  lambda e : on_entry_click(self.seances_search_entry, "search..."))
    self.seances_search_entry.bind("<FocusOut>", lambda e : on_focus_out(self.seances_search_entry, "search..."))

    # add edit/delete buttons.
    ttk.Button(self.header_top, text="🗑", width=3, style="Delete.TButton", command=lambda : self.remove_handler.remove_selected_seances()).pack(side="right")
    ttk.Button(self.header_top, text="✎", width=3, style="Edit.TButton", command=lambda: self.edit_handler.edit_selected_seance(seance_entries=self.seance_entries)).pack(side="right")

    self.columns = ("code", "film", "time", "places", "price")
    self.tree_seances = ttk.Treeview(self.seances_list, columns=self.columns, show="headings", style="Seance.Treeview")
    self.tree_seances.heading("code",   text="code")
    self.tree_seances.heading("film",   text="film")
    self.tree_seances.heading("time",   text="time")
    self.tree_seances.heading("places", text="places")
    self.tree_seances.heading("price",  text="price")

    self.tree_seances.column("code",   width=50,  anchor="center")
    self.tree_seances.column("film",   width=120, anchor="center")
    self.tree_seances.column("time",   width=80,  anchor="center")
    self.tree_seances.column("places", width=80,  anchor="center")
    self.tree_seances.column("price",  width=80,  anchor="center")

    self.scrollbar = ttk.Scrollbar(self.seances_list, orient=tk.VERTICAL, style="Seance.Vertical.TScrollbar", command=self.tree_seances.yview)
    self.tree_seances.configure(yscroll=self.scrollbar.set)

    self.tree_seances.pack(side="left", fill="both", expand=True)
    self.scrollbar.pack(side="right", fill="y")

    # update the seance ID field of quick reserve with the selected seance's code from the treeview.
    self.tree_seances.bind("<<TreeviewSelect>>", lambda e : self.select_handler.on_seance_select(seance_id_entry=self.reserve_seance))  

  def build_film_panel(self) :
    # frame layout.
    self.film_frame = ttk.LabelFrame(self.right, text="add film")
    self.film_frame.pack(fill="x", pady=(0, 10), padx=5, ipady=5)
    
    self.inner = ttk.Frame(self.film_frame)
    self.inner.pack(fill="x", padx=10, pady=5)

    self.row1 = ttk.Frame(self.inner)
    self.row1.pack(fill="x")

    self.film_title = ttk.Entry(self.row1)
    self.film_title.pack(fill="x")
    self.film_title.insert(0, "film title")
    # set placeholder.
    self.film_title.bind("<FocusIn>",  lambda e : on_entry_click(self.film_title, "film title"))
    self.film_title.bind("<FocusOut>", lambda e : on_focus_out(self.film_title, "film title"))

    self.row2 = ttk.Frame(self.inner)
    self.row2.pack(fill="x")

    self.film_genre = ttk.Entry(self.row2)
    self.film_genre.pack(side="left", fill="x", expand=True, padx=(0, 5))
    self.film_genre.insert(0, "genre")
    # set placeholder.
    self.film_genre.bind("<FocusIn>",  lambda e : on_entry_click(self.film_genre, "genre"))
    self.film_genre.bind("<FocusOut>", lambda e : on_focus_out(self.film_genre, "genre"))

    self.film_duration = ttk.Entry(self.row2)
    self.film_duration.pack(side="left", fill="x", expand=True)
    self.film_duration.insert(0, "duration (min)")
    # set placeholder.
    self.film_duration.bind("<FocusIn>",  lambda e : on_entry_click(self.film_duration, "duration (min)"))
    self.film_duration.bind("<FocusOut>", lambda e : on_focus_out(self.film_duration, "duration (min)"))

    # ---- entry dictionary ----
    self.film_entries = {
      "film title"     : self.film_title,
      "genre"          : self.film_genre,
      "duration (min)" : self.film_duration
    }
    # ----------
    self.btn_add_film = ttk.Button(self.film_frame, text="+ add film", style="Add.TButton", command=lambda: self.add_handler.add_film())
    self.btn_add_film.pack(fill="x", padx=10, pady=2)

    # ---- display list ----
    self.film_list = ttk.Frame(self.right)
    self.film_list.pack(fill="both", expand=True, padx=5)

    self.header_top = ttk.Frame(self.film_list)
    self.header_top.pack(fill="x", pady=(0, 5))

    ttk.Label(self.header_top, text="film catalog", style="Header.TLabel").pack(side="left")

    self.film_search_var = tk.StringVar()

    self.film_search_entry = ttk.Entry(self.header_top, textvariable=self.film_search_var, width=20)
    self.film_search_entry.pack(side="left", padx=15)
    self.film_search_entry.insert(0, "search...")
    # set placeholder for search input.
    self.film_search_entry.bind("<FocusIn>",  lambda e : on_entry_click(self.film_search_entry, "search..."))
    self.film_search_entry.bind("<FocusOut>", lambda e : on_focus_out(self.film_search_entry, "search..."))

    # ---
    ttk.Button(self.header_top, text="🗑", width=3, style="Delete.TButton", command=lambda : self.remove_handler.remove_selected_films()).pack(side="right")
    ttk.Button(self.header_top, text="✎", width=3, style="Edit.TButton", command=lambda: self.edit_handler.edit_selected_film(film_entries=self.film_entries)).pack(side="right")

    self.columns = ("code", "title", "genre", "duration")
    self.tree_films = ttk.Treeview(self.film_list, style="Film.Treeview", columns=self.columns, show="headings")
    self.tree_films.heading("code",     text="code")
    self.tree_films.heading("title",    text="title")
    self.tree_films.heading("genre",    text="genre")
    self.tree_films.heading("duration", text="duration")

    self.tree_films.column("code",     width=50,  anchor="center")
    self.tree_films.column("title",    width=150, anchor="center")
    self.tree_films.column("genre",    width=100, anchor="center")
    self.tree_films.column("duration", width=80,  anchor="center")

    self.scrollbar = ttk.Scrollbar(self.film_list, style="Film.Vertical.TScrollbar", orient=tk.VERTICAL, command=self.tree_films.yview)
    self.tree_films.configure(yscroll=self.scrollbar.set)

    self.tree_films.pack(side="left", fill="both", expand=True)
    self.scrollbar.pack(side="right", fill="y")

    # update the film ID entry field of add seance with the selected film's code from the treeview 
    self.tree_films.bind("<<TreeviewSelect>>", lambda e : self.select_handler.on_film_select(film_id_entry=self.seance_film))

  def build_action_panel(self) :
    # ---- create bottom middle frame ----
    self.bottom_middle = ttk.Frame(self.middle)
    self.bottom_middle.pack(fill="x", pady=(10, 0))
    # ---- create bottom right frame ----
    self.bottom_right = ttk.Frame(self.right)
    self.bottom_right.pack(fill="x", pady=(10, 0))

    # ---- quick reserve ----
    self.reserve_frame = ttk.LabelFrame(self.bottom_middle, text="quick reserve")
    self.reserve_frame.pack(side="left", fill="both", expand=True, padx=(5, 2))

    self.inner = ttk.Frame(self.reserve_frame)
    self.inner.pack(fill="x", padx=10, pady=10)

    self.reserve_client = ttk.Entry(self.inner)
    self.reserve_client.pack(fill="x")
    self.reserve_client.insert(0, "client ID")
    # set placeholder.
    self.reserve_client.bind("<FocusIn>",  lambda e : on_entry_click(self.reserve_client, "client ID"))
    self.reserve_client.bind("<FocusOut>", lambda e : on_focus_out(self.reserve_client, "client ID"))

    self.reserve_seance = ttk.Entry(self.inner)
    self.reserve_seance.pack(fill="x")
    self.reserve_seance.insert(0, "seance ID")
    # set placeholder.
    self.reserve_seance.bind("<FocusIn>",  lambda e : on_entry_click(self.reserve_seance, "seance ID"))
    self.reserve_seance.bind("<FocusOut>", lambda e : on_focus_out(self.reserve_seance, "seance ID"))

    ttk.Button(self.reserve_frame, text="+ reserve", style="Reserve.TButton", command=lambda : self.reservation_handler.reserve_ticket(treeview_clients=self.tree_clients)).pack(fill="x", padx=10, pady=2)

    # ---- cancel ticket frame -----
    self.cancel_ticket_frame = ttk.LabelFrame(self.bottom_right, text="cancel ticket")
    self.cancel_ticket_frame.pack(side="left", fill="both", expand=True)

    self.inner = ttk.Frame(self.cancel_ticket_frame)
    self.inner.pack(fill="x", padx=10, pady=10)

    self.cancel_ticket = ttk.Entry(self.inner)
    self.cancel_ticket.pack(fill="x")
    self.cancel_ticket.insert(0, "ticket ID")
    # set placeholder.
    self.cancel_ticket.bind("<FocusIn>",  lambda e : on_entry_click(self.cancel_ticket, "ticket ID"))
    self.cancel_ticket.bind("<FocusOut>", lambda e : on_focus_out(self.cancel_ticket, "ticket ID"))

    ttk.Button(self.cancel_ticket_frame, text="✕ cancel ticket", style="Cancel.TButton", command=lambda : self.reservation_handler.cancel_ticket()).pack(fill="x", padx=10, pady=2)

  def build_stats_panel(self) :
    self.stats_labels = {}

    main_frame = ttk.Frame(self.tab_statics)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    cards_row1 = [
      ("total clients", "total_clients", "#9b59b6"),
      ("total films",   "total_films",   "#2ecc71"),
      ("total seances", "total_seances", "#f1c40f"),
      ("total tickets", "total_tickets", "#3498db")
    ]
    cards_row2 = [
      ("reserved",     "reserved",  "#27ae60"),
      ("cancelled",    "cancelled", "#e74c3c"),
      ("used",         "used",      "#2ecc71"),
      ("revenue (DH)", "revenus",   "#f39c12")
    ]

    row1_frame = ttk.Frame(main_frame)
    row1_frame.pack(fill="both", expand=True, pady=(0, 10))

    for i in range(4) :
      row1_frame.columnconfigure(i, weight=1, uniform="cards_row1")
      row1_frame.rowconfigure(0, weight=1)

    for i, (label, key, color) in enumerate(cards_row1):
        card = tk.Frame(row1_frame, bg="white", highlightbackground="#ccc", highlightthickness=1)
        card.grid(row=0, column=i, sticky="nsew", padx=10)

        value_label = tk.Label(card, text="0", font=("Segoe UI", 50, "bold"), fg=color, bg="white")
        value_label.pack(expand=True)

        name_label = tk.Label(card, text=label, font=("Segoe UI", 15, "bold"), fg="white", bg=color)
        name_label.pack(fill="x", side="bottom")

        self.stats_labels[key] = value_label

    row2_frame = ttk.Frame(main_frame)
    row2_frame.pack(fill="both", expand=True, pady=(0, 10))

    for i in range(4) :
      row2_frame.columnconfigure(i, weight=1, uniform="cards_row2")
      row2_frame.rowconfigure(0, weight=1)

    for i, (label, key, color) in enumerate(cards_row2) :
      card = tk.Frame(row2_frame, bg="white", highlightbackground="#ccc", highlightthickness=1)
      card.grid(row=0, column=i, sticky="nsew", padx=10)

      value_label = tk.Label(card, text="0", font=("Segoe UI", 50, "bold"), fg=color, bg="white")
      value_label.pack(expand=True)

      name_label = tk.Label(card, text=label, font=("Segoe UI", 15, "bold"), fg="white", bg=color)
      name_label.pack(fill="x", side="bottom")

      self.stats_labels[key] = value_label

  def init_handlers(self) :
    # ---- initialize Renderer to central state module ----
    state.renderer = Renderer(tree_clients=self.tree_clients, tree_seances=self.tree_seances, tree_films=self.tree_films, stats_labels=self.stats_labels)
    # ---- instatiate handlers passing the instance maps ----
    self.add_handler = AddHandler(client_entries=self.client_entries, seance_entries=self.seance_entries, film_entries=self.film_entries)
    # ----------
    self.search_vars = {
      "clients" : self.client_search_var,
      "seances" : self.seances_search_var,
      "films"   : self.film_search_var
    }

    self.search_handler = SearchHandler(search_vars=self.search_vars)
    # ---- add observers ----
    self.client_search_var.trace_add("write",  lambda *args : self.search_handler.filter_clients())
    self.seances_search_var.trace_add("write", lambda *args : self.search_handler.filter_seances())
    self.film_search_var.trace_add("write",    lambda *args : self.search_handler.filter_films())
    # ----  
    self.select_handler = SelectHandler(client_treeview=self.tree_clients, seance_treeview=self.tree_seances, film_treeview=self.tree_films)
    # ----
    self.remove_handler = RemoveHandler(client_treeview=self.tree_clients, seance_treeview=self.tree_seances, film_treeview=self.tree_films)
    # ----
    self.edit_handler = EditHandler(client_treeview=self.tree_clients, seance_treeview=self.tree_seances, film_treeview=self.tree_films, add_handler=self.add_handler, btn_add_client=self.btn_add_client, btn_add_seance=self.btn_add_seance, btn_add_film=self.btn_add_film)
    # ----
    self.reservation_handler = ReservationHandler(client_id_entry=self.reserve_client, seance_id_entry=self.reserve_seance, ticket_id_entry=self.cancel_ticket)
    # ----
    try :
      state.db_manager = DatabaseManager(root=self.root)
    except EnvironmentError as e :
      from tkinter import messagebox
      messagebox.showerror(title="setup required", message=str(e))
      self.root.destroy()

  def on_tab_changed(self, event) :
    current_tab = self.notebook.index(self.notebook.select())
    if current_tab == 0 :
      self.title_label.configure(text="cinema vision")
    elif current_tab == 1 :
      self.title_label.configure(text="statistics dashboard")

  def run(self) :
    self.root.mainloop()


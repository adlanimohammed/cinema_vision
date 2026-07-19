# Cinema Vision

A desktop cinema management application built with Python and Tkinter, backed by Supabase for data persistence.

## Features

- **Client Management**    -- Add, edit, search, filter, and remove cinema clients
- **Film Catalog**         -- Add, edit, search, filter, and remove films with genre and duration
- **Seance Scheduling**    -- Create and edit screenings linked to films with date/time, seat capacity, and pricing (DH)
- **Ticket Reservation**   -- Quick reserve tickets by linking clients to seances
- **Ticket Cancellation**  -- Cancel reserved tickets with automatic seat and revenue restoration (persisted to DB)
- **Edit Mode**            -- Toggle-based edit UI for clients, films, and seances (fill fields, update, revert)
- **Input Validation**     -- Date format validation, past date rejection, time format (HH:mm) validation
- **Real-time Search**     -- Instant filtering across clients, films, and seances
- **Statistics Dashboard** -- Live stats on total counts, reserved/cancelled/used tickets, and revenue
- **Data Persistence**     -- All data (clients, films, seances, tickets) stored in Supabase and persists across sessions

## Getting Started

### Requirements

- Python 3.10+
- Tkinter (included with standard Python installations)
- A Supabase project with `clients`, `films`, `seances`, and `tickets` tables

### Installation

```bash
git clone https://github.com/adlanimohammed/cinema_vision.git
cd cinema_vision
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Debian/Ubuntu users:** If you get `externally-managed-environment` error, run `sudo apt install python3-venv` first.

### Environment Setup

Create a `.env` file in the project root with your Supabase credentials:

```
SUPABASE_URL="your-project-url"
SUPABASE_KEY="your-anon-key"
```

### Supabase Setup

Create the following tables in your Supabase project:

**clients**
| Column    | Type                              |
|-----------|-----------------------------------|
| code      | int (primary key, auto-increment) |
| lastname  | text                              |
| name      | text                              |
| telephone | text                              |
| date      | text                              |

**films**
| Column      | Type                              |
|-------------|-----------------------------------|
| code        | int (primary key, auto-increment) |
| title       | text                              |
| genre       | text                              |
| duree       | int                               |
| description | text (optional)                   |

**seances**
| Column     | Type                              |
|------------|-----------------------------------|
| code       | int (primary key, auto-increment) |
| film       | int (foreign key -> films.code)   |
| date_heure | text                              |
| nbrt       | int                               |
| nbrd       | int                               |
| price      | float                             |
| status     | text (default: "active")          |

**tickets**
| Column | Type                              |
|--------|-----------------------------------|
| code   | int (primary key, auto-increment) |
| client | int (foreign key -> clients.code) |
| seance | int (foreign key -> seances.code) |
| date   | text                              |
| etat   | text (default: "reserved")        |

### Running

```bash
python3 main.py
```

## Project Structure

```
cinema_vision/
├── main.py                        # Entry point
├── .env                           # Supabase credentials (not committed)
├── requirements.txt               # Python dependencies
└── src/
    ├── core/                      # Domain models (MVC - Model)
    │   ├── __init__.py
    │   ├── personne.py            # Personne base class
    │   ├── client.py              # Client (inherits Personne)
    │   ├── film.py                # Film model
    │   ├── seance.py              # Seance/screening model
    │   ├── ticket.py              # Ticket model
    │   └── cinema.py              # Cinema orchestrator (business logic)
    ├── database/                  # Database layer (Supabase)
    │   ├── __init__.py
    │   └── db_manager.py          # CRUD operations and data loading
    └── gui/                       # GUI layer (MVC - View + Controller)
        ├── __init__.py
        ├── app.py                 # Main window, layout, and tab building
        ├── views.py               # Treeview rendering and stats refresh
        ├── handlers.py            # Event handlers (Add, Edit, Remove, Search, Reserve)
        ├── state.py               # Shared application state (Cinema, Renderer, DB)
        └── widgets.py             # Placeholder helper functions
```

## Architecture

The application follows an **MVC-inspired** pattern:

| Layer      | Location                             | Responsibility                                                                      |
|------------|--------------------------------------|-------------------------------------------------------------------------------------|
| Model      | `src/core/`                          | Domain classes (`Client`, `Film`, `Seance`, `Ticket`) and business logic (`Cinema`) |
| View       | `src/gui/app.py`, `src/gui/views.py` | Tkinter layout and Treeview rendering                                               |
| Controller | `src/gui/handlers.py`                | Event handlers bridging user actions to domain logic                                |
| State      | `src/gui/state.py`                   | Shared global `Cinema` instance and `Renderer` reference                            |
| Database   | `src/database/db_manager.py`         | Supabase CRUD operations and async data loading                                     |

## Tech Stack

- **Language:**     Python 3.10+
- **GUI:**          Tkinter / ttk
- **Database:**     Supabase (PostgreSQL)
- **Dependencies:** python-dotenv, supabase, tkcalendar

## License

This project is open source and available for educational use.

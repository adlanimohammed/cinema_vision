def on_entry_click(entry, placeholder) :
  if entry.get() == placeholder or entry.get() == "search..." :
    entry.delete(0, "end")
    entry.configure(foreground="black")

def on_focus_out(entry, placeholder) :
  if entry.get() == "" :
    entry.insert(0, placeholder)
    entry.configure(foreground="gray")

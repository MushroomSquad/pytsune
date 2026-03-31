from __future__ import annotations

try:
    import tkinter as tk
except ImportError:  # pragma: no cover - optional system dependency
    tk = None


class MainView:
    def __init__(self, presenter: object) -> None:
        self._presenter = presenter
        self._root = None
        self._listbox = None

        if tk is None:
            return

        try:
            root = tk.Tk()
            root.title("Template GUI")
            listbox = tk.Listbox(root, width=40)
            listbox.pack(padx=16, pady=16)
            self._root = root
            self._listbox = listbox
            self.render_items()
        except tk.TclError:
            self._root = None
            self._listbox = None

    def render_items(self) -> None:
        if self._listbox is None:
            return
        self._listbox.delete(0, tk.END)
        for item in self._presenter.load_items():
            self._listbox.insert(tk.END, item)

    def mainloop(self) -> None:
        if self._root is not None:
            self._root.mainloop()

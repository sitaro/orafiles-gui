"""List manager widget with Add/Edit/Delete/Duplicate buttons."""

from __future__ import annotations
import customtkinter as ctk
from typing import Callable


class ListManager(ctk.CTkFrame):
    """A listbox-like widget with management buttons."""

    def __init__(
        self,
        master,
        title: str = "",
        on_select: Callable[[int], None] | None = None,
        on_add: Callable[[], None] | None = None,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_duplicate: Callable[[int], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._on_select = on_select
        self._on_add = on_add
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_duplicate = on_duplicate
        self._items: list[str] = []
        self._selected_index: int = -1

        if title:
            lbl = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(weight="bold"))
            lbl.pack(fill="x", padx=5, pady=(5, 2))

        # Scrollable list
        self._scroll = ctk.CTkScrollableFrame(self, width=200)
        self._scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self._buttons_list: list[ctk.CTkButton] = []

        # Button bar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkButton(btn_frame, text="Add", width=60, command=self._do_add).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Edit", width=60, command=self._do_edit).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Dup", width=60, command=self._do_duplicate).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Del", width=60, command=self._do_delete).pack(side="left", padx=2)

    def set_items(self, items: list[str]) -> None:
        self._items = list(items)
        self._rebuild()

    def get_selected_index(self) -> int:
        return self._selected_index

    def select_index(self, index: int) -> None:
        if 0 <= index < len(self._items):
            self._selected_index = index
            self._highlight()
            if self._on_select:
                self._on_select(index)

    def _rebuild(self):
        for btn in self._buttons_list:
            btn.destroy()
        self._buttons_list.clear()

        for i, text in enumerate(self._items):
            btn = ctk.CTkButton(
                self._scroll,
                text=text,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                command=lambda idx=i: self._select(idx),
            )
            btn.pack(fill="x", pady=1)
            self._buttons_list.append(btn)

        if self._selected_index >= len(self._items):
            self._selected_index = len(self._items) - 1
        self._highlight()

    def _select(self, index: int):
        self._selected_index = index
        self._highlight()
        if self._on_select:
            self._on_select(index)

    def _highlight(self):
        for i, btn in enumerate(self._buttons_list):
            if i == self._selected_index:
                btn.configure(fg_color=("gray75", "gray35"))
            else:
                btn.configure(fg_color="transparent")

    def _do_add(self):
        if self._on_add:
            self._on_add()

    def _do_edit(self):
        if self._on_edit and self._selected_index >= 0:
            self._on_edit(self._selected_index)

    def _do_duplicate(self):
        if self._on_duplicate and self._selected_index >= 0:
            self._on_duplicate(self._selected_index)

    def _do_delete(self):
        if self._on_delete and self._selected_index >= 0:
            self._on_delete(self._selected_index)

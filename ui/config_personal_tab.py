import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ConfigPersonalTab(ttk.Frame):
    def __init__(self, parent, config_file="config_personal.json", on_save_callback=None):
        super().__init__(parent)
        self.config_file = config_file
        self.on_save_callback = on_save_callback
        self.data = {
            "lista_personal_recibe": [],
            "lista_personal_visto_bueno": []
        }
        self._load_data()
        self._create_widgets()
        self._populate_trees()

    def _load_data(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            else:
                self.data = {"lista_personal_recibe": [], "lista_personal_visto_bueno": []}
        except Exception as e:
            print(f"Error cargando configuración: {e}")

    def _save_data(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", "Configuración de personal guardada correctamente")
            if self.on_save_callback:
                self.on_save_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="Configuración de Personal", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Personal recibe compra
        frame_recibe = ttk.LabelFrame(self, text="Personal que Recibe la Compra")
        frame_recibe.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self._build_section(frame_recibe, "lista_personal_recibe", 
                            ["Grado_recibio_la_compra", "Nombre_recibio_la_compra", "Matricula_recibio_la_compra"],
                            ["Grado", "Nombre", "Matrícula"])

        # Personal Visto Bueno
        frame_vobo = ttk.LabelFrame(self, text="Personal con Visto Bueno")
        frame_vobo.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        self._build_section(frame_vobo, "lista_personal_visto_bueno", 
                            ["Grado_Vo_Bo", "Nombre_Vo_Bo", "Matricula_Vo_Bo"],
                            ["Grado", "Nombre", "Matrícula"])
        
        # Guardar
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="💾 Guardar Configuración", command=self._save_data).pack()

    def _build_section(self, parent_frame, list_key, field_names, col_names):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)

        tree = ttk.Treeview(parent_frame, columns=col_names, show="headings", selectmode="browse")
        for c in col_names:
            tree.heading(c, text=c)
            # Adapt width
            width = 150 if c == "Nombre" else 100
            tree.column(c, width=width)
            
        tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        scroll = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        setattr(self, f"tree_{list_key}", tree)

        btn_frame = ttk.Frame(parent_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(btn_frame, text="➕ Agregar", command=lambda: self._add_item(list_key, field_names, tree)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Editar", command=lambda: self._edit_item(list_key, field_names, col_names, tree)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Eliminar", command=lambda: self._delete_item(list_key, tree)).pack(side="left", padx=5)

    def _populate_trees(self):
        for key in ["lista_personal_recibe", "lista_personal_visto_bueno"]:
            tree = getattr(self, f"tree_{key}")
            # Limpiar
            for item in tree.get_children():
                tree.delete(item)
            # Llenar
            for i, data_dict in enumerate(self.data.get(key, [])):
                vals = list(data_dict.values())
                tree.insert("", "end", iid=str(i), values=vals)

    def _add_item(self, list_key, field_names, tree):
        self._show_form_dialog("Agregar Personal", list_key, field_names, tree)

    def _edit_item(self, list_key, field_names, col_names, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un elemento para editar.")
            return
        idx = int(selected[0])
        current_data = self.data[list_key][idx]
        self._show_form_dialog("Editar Personal", list_key, field_names, tree, idx, current_data)

    def _show_form_dialog(self, title, list_key, field_names, tree, edit_idx=None, current_data=None):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("400x200")
        dlg.grab_set()

        entries = {}
        # Make a nicer form
        form_frame = ttk.Frame(dlg, padding=10)
        form_frame.pack(fill="both", expand=True)
        form_frame.columnconfigure(1, weight=1)

        labels = ["Grado:", "Nombre:", "Matrícula:"]
        for i, field_key in enumerate(field_names):
            ttk.Label(form_frame, text=labels[i]).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            ent = ttk.Entry(form_frame)
            if current_data:
                ent.insert(0, current_data.get(field_key, ""))
            ent.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            entries[field_key] = ent

        def on_save():
            new_item = {k: v.get() for k, v in entries.items()}
            if edit_idx is not None:
                self.data[list_key][edit_idx] = new_item
            else:
                if list_key not in self.data:
                    self.data[list_key] = []
                self.data[list_key].append(new_item)
            self._populate_trees()
            dlg.destroy()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Aceptar", command=on_save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dlg.destroy).pack(side="left", padx=5)

    def _delete_item(self, list_key, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un elemento para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este registro?"):
            idx = int(selected[0])
            del self.data[list_key][idx]
            self._populate_trees()

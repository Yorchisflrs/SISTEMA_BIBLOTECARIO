import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
import pandas as pd
import io
import magic


DATABASE = 'biblioteca.db'

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def execute_query(query, params=()):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

def init_db():
    create_tables_script = '''
    CREATE TABLE IF NOT EXISTS Libros (
        id_libro INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        edicion TEXT NOT NULL,
        categoria TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Prestamos (
        id_prestamo INTEGER PRIMARY KEY AUTOINCREMENT,
        id_libro INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        fecha_prestamo TEXT NOT NULL,
        fecha_devolucion TEXT,
        devuelto BOOLEAN NOT NULL CHECK (devuelto IN (0, 1)),
        FOREIGN KEY (id_libro) REFERENCES Libros (id_libro),
        FOREIGN KEY (id_usuario) REFERENCES Usuarios (id_usuario)
    );

    CREATE TABLE IF NOT EXISTS Categorias (
        id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Roles (
        id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Autores (
        id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT NOT NULL,
        telefono TEXT,
        correo TEXT NOT NULL,
        foto BLOB
    );
    '''
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for statement in create_tables_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()

def ventana_administrador():
    admin_window = tk.Toplevel(root)
    admin_window.title("Panel de Administrador")
    center_window(admin_window, 1000, 700)

    tab_control = ttk.Notebook(admin_window)

    tab_prestamos = ttk.Frame(tab_control)
    tab_libros = ttk.Frame(tab_control)
    tab_categorias = ttk.Frame(tab_control)
    tab_roles = ttk.Frame(tab_control)
    tab_autores = ttk.Frame(tab_control)
    tab_usuarios = ttk.Frame(tab_control)
    tab_excel = ttk.Frame(tab_control)

    tab_control.add(tab_prestamos, text='Préstamos')
    tab_control.add(tab_libros, text='Libros')
    tab_control.add(tab_categorias, text='Categorías')
    tab_control.add(tab_roles, text='Roles')
    tab_control.add(tab_autores, text='Autores')
    tab_control.add(tab_usuarios, text='Usuarios')
    tab_control.add(tab_excel, text='Ingresar Excel')

    setup_tab_prestamos(tab_prestamos)
    setup_tab_libros(tab_libros)
    setup_tab_categorias(tab_categorias)
    setup_tab_roles(tab_roles)
    setup_tab_autores(tab_autores)
    setup_tab_usuarios(tab_usuarios)
    setup_tab_excel(tab_excel)

    tab_control.pack(expand=1, fill='both')

def ventana_bibliotecario():
    bibliotecario_window = tk.Toplevel(root)
    bibliotecario_window.title("Panel de Bibliotecario")
    center_window(bibliotecario_window, 1000, 700)

    tab_control = ttk.Notebook(bibliotecario_window)

    tab_libros = ttk.Frame(tab_control)
    tab_prestamos = ttk.Frame(tab_control)
    tab_usuarios = ttk.Frame(tab_control)

    tab_control.add(tab_libros, text='Libros')
    tab_control.add(tab_prestamos, text='Préstamos')
    tab_control.add(tab_usuarios, text='Usuarios')

    setup_tab_libros(tab_libros)
    setup_tab_prestamos(tab_prestamos)
    setup_tab_usuarios(tab_usuarios)

    tab_control.pack(expand=1, fill='both')

def ventana_estudiante():
    estudiante_window = tk.Toplevel(root)
    estudiante_window.title("Panel de Estudiante")
    center_window(estudiante_window, 800, 600)

    tk.Label(estudiante_window, text="Libros por Categoría", font=('Arial', 14)).pack(pady=10)

    tk.Button(estudiante_window, text="Libros de Ingenierías", bg='skyblue', command=lambda: mostrar_libros_categoria('Libros de Ingenierías')).pack(pady=5)
    tk.Button(estudiante_window, text="Libros de Sociales", bg='skyblue', command=lambda: mostrar_libros_categoria('Libros de Sociales')).pack(pady=5)
    tk.Button(estudiante_window, text="Libros de Biomédicas", bg='skyblue', command=lambda: mostrar_libros_categoria('Libros de Biomédicas')).pack(pady=5)

def mostrar_libros_categoria(categoria):
    categoria_window = tk.Toplevel(root)
    categoria_window.title(f"Libros de {categoria}")
    center_window(categoria_window, 800, 600)

    tk.Label(categoria_window, text=f"Libros de {categoria}", font=('Arial', 14)).pack(pady=10)

    frame_table = tk.Frame(categoria_window)
    frame_table.pack()

    cols = ('ID Libro', 'Título', 'Autor', 'Edición', 'Categoría')
    tree = ttk.Treeview(frame_table, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack()

    query = "SELECT * FROM Libros WHERE categoria = ?"
    cursor = execute_query(query, (categoria,))
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

def setup_tab_prestamos(tab):
    tk.Label(tab, text="Gestión de Préstamos", font=('Arial', 14)).pack(pady=10)
    
    frame_form = tk.Frame(tab)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="ID Libro:").grid(row=0, column=0)
    id_libro_entry = tk.Entry(frame_form)
    id_libro_entry.grid(row=0, column=1)

    tk.Label(frame_form, text="ID Usuario:").grid(row=1, column=0)
    id_usuario_combobox = ttk.Combobox(frame_form, values=[f"{row[0]} - {row[1]} {row[2]}" for row in execute_query("SELECT id_usuario, nombre, apellido FROM Usuarios").fetchall()])
    id_usuario_combobox.grid(row=1, column=1)

    tk.Label(frame_form, text="Fecha Préstamo:").grid(row=2, column=0)
    fecha_prestamo_entry = tk.Entry(frame_form)
    fecha_prestamo_entry.grid(row=2, column=1)

    tk.Label(frame_form, text="Fecha Devolución:").grid(row=3, column=0)
    fecha_devolucion_entry = tk.Entry(frame_form)
    fecha_devolucion_entry.grid(row=3, column=1)

    tk.Button(frame_form, text="Registrar Préstamo", bg='green', fg='white',
              command=lambda: registrar_prestamo(id_libro_entry.get(), id_usuario_combobox.get().split(" ")[0], fecha_prestamo_entry.get(), fecha_devolucion_entry.get())).grid(row=4, columnspan=2, pady=10)

    frame_table = tk.Frame(tab)
    frame_table.pack()

    tk.Label(frame_table, text="Préstamos Realizados", font=('Arial', 12)).pack(pady=10)

    cols = ('ID Préstamo', 'ID Libro', 'ID Usuario', 'Fecha Préstamo', 'Fecha Devolución', 'Devuelto')
    tree = ttk.Treeview(frame_table, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack()
    load_prestamos(tree)

    def buscar_prestamo():
        for i in tree.get_children():
            tree.delete(i)
        query = "SELECT * FROM Prestamos WHERE id_libro LIKE ? OR id_usuario LIKE ?"
        cursor = execute_query(query, ('%' + search_entry.get() + '%', '%' + search_entry.get() + '%'))
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

    def marcar_devolucion():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')
        id_prestamo = values[0]
        execute_query("UPDATE Prestamos SET devuelto = 1 WHERE id_prestamo = ?", (id_prestamo,))
        load_prestamos(tree)

    frame_search = tk.Frame(tab)
    frame_search.pack(pady=10)

    tk.Label(frame_search, text="Buscar Préstamo:").pack(side=tk.LEFT)
    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT)
    tk.Button(frame_search, text="Buscar", command=buscar_prestamo).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Marcar Devolución", command=marcar_devolucion).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Actualizar", command=lambda: load_prestamos(tree)).pack(side=tk.LEFT)

def setup_tab_libros(tab):
    tk.Label(tab, text="Gestión de Libros", font=('Arial', 14)).pack(pady=10)
    
    frame_form = tk.Frame(tab)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Título:").grid(row=0, column=0)
    titulo_entry = tk.Entry(frame_form)
    titulo_entry.grid(row=0, column=1)

    tk.Label(frame_form, text="Autor:").grid(row=1, column=0)
    autor_entry = tk.Entry(frame_form)
    autor_entry.grid(row=1, column=1)

    tk.Label(frame_form, text="Edición:").grid(row=2, column=0)
    edicion_entry = tk.Entry(frame_form)
    edicion_entry.grid(row=2, column=1)

    tk.Label(frame_form, text="Categoría:").grid(row=3, column=0)
    categoria_combobox = ttk.Combobox(frame_form, values=["Libros de Ingenierías", "Libros de Sociales", "Libros de Biomédicas"])
    categoria_combobox.grid(row=3, column=1)

    tk.Button(frame_form, text="Agregar Libro", bg='green', fg='white',
              command=lambda: agregar_libro(titulo_entry.get(), autor_entry.get(), edicion_entry.get(), categoria_combobox.get())).grid(row=4, columnspan=2, pady=10)

    frame_table = tk.Frame(tab)
    frame_table.pack()

    tk.Label(frame_table, text="Libros Disponibles", font=('Arial', 12)).pack(pady=10)

    cols = ('ID Libro', 'Título', 'Autor', 'Edición', 'Categoría')
    tree = ttk.Treeview(frame_table, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack()
    load_libros(tree)

    def buscar_libro():
        for i in tree.get_children():
            tree.delete(i)
        query = "SELECT * FROM Libros WHERE titulo LIKE ? OR autor LIKE ?"
        cursor = execute_query(query, ('%' + search_entry.get() + '%', '%' + search_entry.get() + '%'))
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

    def eliminar_libro():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')
        id_libro = values[0]
        execute_query("DELETE FROM Libros WHERE id_libro = ?", (id_libro,))
        tree.delete(selected_item)

    frame_search = tk.Frame(tab)
    frame_search.pack(pady=10)

    tk.Label(frame_search, text="Buscar Libro:").pack(side=tk.LEFT)
    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT)
    tk.Button(frame_search, text="Buscar", command=buscar_libro).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Eliminar", command=eliminar_libro).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Actualizar", command=lambda: load_libros(tree)).pack(side=tk.LEFT)

def setup_tab_categorias(tab):
    tk.Label(tab, text="Gestión de Categorías", font=('Arial', 14)).pack(pady=10)
    
    frame_form = tk.Frame(tab)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Nombre Categoría:").grid(row=0, column=0)
    categoria_entry = tk.Entry(frame_form)
    categoria_entry.grid(row=0, column=1)

    tk.Button(frame_form, text="Agregar Categoría", bg='green', fg='white',
              command=lambda: agregar_categoria(categoria_entry.get())).grid(row=1, columnspan=2, pady=10)

    frame_table = tk.Frame(tab)
    frame_table.pack()

    tk.Label(frame_table, text="Categorías", font=('Arial', 12)).pack(pady=10)

    cols = ('ID', 'Nombre')
    tree = ttk.Treeview(frame_table, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack()
    load_categorias(tree)

    def buscar_categoria():
        for i in tree.get_children():
            tree.delete(i)
        query = "SELECT * FROM Categorias WHERE nombre LIKE ?"
        cursor = execute_query(query, ('%' + search_entry.get() + '%',))
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

    def eliminar_categoria():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')
        id_categoria = values[0]
        execute_query("DELETE FROM Categorias WHERE id_categoria = ?", (id_categoria,))
        tree.delete(selected_item)

    frame_search = tk.Frame(tab)
    frame_search.pack(pady=10)

    tk.Label(frame_search, text="Buscar Categoría:").pack(side=tk.LEFT)
    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT)
    tk.Button(frame_search, text="Buscar", command=buscar_categoria).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Eliminar", command=eliminar_categoria).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Actualizar", command=lambda: load_categorias(tree)).pack(side=tk.LEFT)

def setup_tab_roles(tab):
    tk.Label(tab, text="Gestión de Roles", font=('Arial', 14)).pack(pady=10)
    
    frame_form = tk.Frame(tab)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Nombre Rol:").grid(row=0, column=0)
    rol_entry = tk.Entry(frame_form)
    rol_entry.grid(row=0, column=1)

    tk.Button(frame_form, text="Agregar Rol", bg='green', fg='white',
              command=lambda: agregar_rol(rol_entry.get())).grid(row=1, columnspan=2, pady=10)

    frame_table = tk.Frame(tab)
    frame_table.pack()

    tk.Label(frame_table, text="Roles", font=('Arial', 12)).pack(pady=10)

    cols = ('ID', 'Nombre')
    tree = ttk.Treeview(frame_table, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack()
    load_roles(tree)

    def buscar_rol():
        for i in tree.get_children():
            tree.delete(i)
        query = "SELECT * FROM Roles WHERE nombre LIKE ?"
        cursor = execute_query(query, ('%' + search_entry.get() + '%',))
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

    def eliminar_rol():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')
        id_rol = values[0]
        execute_query("DELETE FROM Roles WHERE id_rol = ?", (id_rol,))
        tree.delete(selected_item)

    frame_search = tk.Frame(tab)
    frame_search.pack(pady=10)

    tk.Label(frame_search, text="Buscar Rol:").pack(side=tk.LEFT)
    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT)
    tk.Button(frame_search, text="Buscar", command=buscar_rol).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Eliminar", command=eliminar_rol).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Actualizar", command=lambda: load_roles(tree)).pack(side=tk.LEFT)

def setup_tab_autores(tab):
    tk.Label(tab, text="Gestión de Autores", font=('Arial', 14)).pack(pady=10)
    
    frame_form = tk.Frame(tab)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Nombre Autor:").grid(row=0, column=0)
    autor_entry = tk.Entry(frame_form)
    autor_entry.grid(row=0, column=1)

    tk.Button(frame_form, text="Agregar Autor", bg='green', fg='white',
              command=lambda: agregar_autor(autor_entry.get())).grid(row=1, columnspan=2, pady=10)

    frame_table = tk.Frame(tab)
    frame_table.pack()

    tk.Label(frame_table, text="Autores", font=('Arial', 12)).pack(pady=10)

    cols = ('ID', 'Nombre')
    tree = ttk.Treeview(frame_table, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack()
    load_autores(tree)

    def buscar_autor():
        for i in tree.get_children():
            tree.delete(i)
        query = "SELECT * FROM Autores WHERE nombre LIKE ?"
        cursor = execute_query(query, ('%' + search_entry.get() + '%',))
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

    def eliminar_autor():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')
        id_autor = values[0]
        execute_query("DELETE FROM Autores WHERE id_autor = ?", (id_autor,))
        tree.delete(selected_item)

    frame_search = tk.Frame(tab)
    frame_search.pack(pady=10)

    tk.Label(frame_search, text="Buscar Autor:").pack(side=tk.LEFT)
    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT)
    tk.Button(frame_search, text="Buscar", command=buscar_autor).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Eliminar", command=eliminar_autor).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Actualizar", command=lambda: load_autores(tree)).pack(side=tk.LEFT)

def setup_tab_usuarios(tab):
    tk.Label(tab, text="Gestión de Usuarios", font=('Arial', 14)).pack(pady=10)
    
    frame_form = tk.Frame(tab)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Nombre:").grid(row=0, column=0)
    nombre_entry = tk.Entry(frame_form)
    nombre_entry.grid(row=0, column=1)

    tk.Label(frame_form, text="Apellido:").grid(row=1, column=0)
    apellido_entry = tk.Entry(frame_form)
    apellido_entry.grid(row=1, column=1)

    tk.Label(frame_form, text="DNI:").grid(row=2, column=0)
    dni_entry = tk.Entry(frame_form)
    dni_entry.grid(row=2, column=1)

    tk.Label(frame_form, text="Teléfono:").grid(row=3, column=0)
    telefono_entry = tk.Entry(frame_form)
    telefono_entry.grid(row=3, column=1)

    tk.Label(frame_form, text="Correo:").grid(row=4, column=0)
    correo_entry = tk.Entry(frame_form)
    correo_entry.grid(row=4, column=1)

    tk.Button(frame_form, text="Agregar Usuario", bg='green', fg='white',
              command=lambda: agregar_usuario(nombre_entry.get(), apellido_entry.get(), dni_entry.get(), telefono_entry.get(), correo_entry.get(), imagen_usuario)).grid(row=5, columnspan=2, pady=10)

    frame_foto = tk.Frame(tab)
    frame_foto.pack(pady=10)

    tk.Label(frame_foto, text="Foto:").pack(side=tk.LEFT)
    btn_subir_foto = tk.Button(frame_foto, text="Subir Foto", command=subir_foto)
    btn_subir_foto.pack(side=tk.LEFT)

    frame_table = tk.Frame(tab)
    frame_table.pack()

    tk.Label(frame_table, text="Usuarios", font=('Arial', 12)).pack(pady=10)

    cols = ('ID', 'Nombre', 'Apellido', 'DNI', 'Teléfono', 'Correo', 'Foto')
    tree = ttk.Treeview(frame_table, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack()
    load_usuarios(tree)

    def buscar_usuario():
        for i in tree.get_children():
            tree.delete(i)
        query = "SELECT * FROM Usuarios WHERE nombre LIKE ? OR apellido LIKE ?"
        cursor = execute_query(query, ('%' + search_entry.get() + '%', '%' + search_entry.get() + '%'))
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

    def eliminar_usuario():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')
        id_usuario = values[0]
        execute_query("DELETE FROM Usuarios WHERE id_usuario = ?", (id_usuario,))
        tree.delete(selected_item)

    frame_search = tk.Frame(tab)
    frame_search.pack(pady=10)

    tk.Label(frame_search, text="Buscar Usuario:").pack(side=tk.LEFT)
    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT)
    tk.Button(frame_search, text="Buscar", command=buscar_usuario).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Eliminar", command=eliminar_usuario).pack(side=tk.LEFT)
    tk.Button(frame_search, text="Actualizar", command=lambda: load_usuarios(tree)).pack(side=tk.LEFT)

def setup_tab_excel(tab):
    tk.Label(tab, text="Ingresar Datos desde Excel", font=('Arial', 14)).pack(pady=10)
    
    frame_form = tk.Frame(tab)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Seleccionar Archivo Excel:").grid(row=0, column=0)
    tk.Button(frame_form, text="Buscar Archivo", bg='blue', fg='white',
              command=cargar_excel).grid(row=0, column=1, pady=10)

def registrar_prestamo(id_libro, id_usuario, fecha_prestamo, fecha_devolucion):
    query = "INSERT INTO Prestamos (id_libro, id_usuario, fecha_prestamo, fecha_devolucion, devuelto) VALUES (?, ?, ?, ?, 0)"
    execute_query(query, (id_libro, id_usuario, fecha_prestamo, fecha_devolucion))
    messagebox.showinfo("Préstamo Registrado", f"Préstamo del libro {id_libro} al usuario {id_usuario} registrado con éxito")

def agregar_libro(titulo, autor, edicion, categoria):
    query = "INSERT INTO Libros (titulo, autor, edicion, categoria) VALUES (?, ?, ?, ?)"
    execute_query(query, (titulo, autor, edicion, categoria))
    messagebox.showinfo("Libro Agregado", f"Libro {titulo} agregado con éxito")

def agregar_categoria(nombre):
    query = "INSERT INTO Categorias (nombre) VALUES (?)"
    execute_query(query, (nombre,))
    messagebox.showinfo("Categoría Agregada", f"Categoría {nombre} agregada con éxito")

def agregar_rol(nombre):
    query = "INSERT INTO Roles (nombre) VALUES (?)"
    execute_query(query, (nombre,))
    messagebox.showinfo("Rol Agregado", f"Rol {nombre} agregado con éxito")

def agregar_autor(nombre):
    query = "INSERT INTO Autores (nombre) VALUES (?)"
    execute_query(query, (nombre,))
    messagebox.showinfo("Autor Agregado", f"Autor {nombre} agregado con éxito")

def agregar_usuario(nombre, apellido, dni, telefono, correo, foto):
    query = "INSERT INTO Usuarios (nombre, apellido, dni, telefono, correo, foto) VALUES (?, ?, ?, ?, ?, ?)"
    execute_query(query, (nombre, apellido, dni, telefono, correo, foto))
    messagebox.showinfo("Usuario Agregado", f"Usuario {nombre} {apellido} agregado con éxito")

def cargar_excel():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if filepath:
        df = pd.read_excel(filepath)
        messagebox.showinfo("Archivo Cargado", f"Archivo {filepath} cargado con éxito")
        # Aquí puedes añadir lógica para procesar los datos del DataFrame `df`

def subir_foto():
    global imagen_usuario
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if filepath:
        with open(filepath, 'rb') as f:
            imagen_usuario = f.read()
        messagebox.showinfo("Foto Cargada", f"Foto cargada con éxito")

def load_prestamos(tree):
    for i in tree.get_children():
        tree.delete(i)
    for row in execute_query("SELECT * FROM Prestamos").fetchall():
        tree.insert('', 'end', values=row)

def load_libros(tree):
    for i in tree.get_children():
        tree.delete(i)
    for row in execute_query("SELECT * FROM Libros").fetchall():
        tree.insert('', 'end', values=row)

def load_categorias(tree):
    for i in tree.get_children():
        tree.delete(i)
    for row in execute_query("SELECT * FROM Categorias").fetchall():
        tree.insert('', 'end', values=row)

def load_roles(tree):
    for i in tree.get_children():
        tree.delete(i)
    for row in execute_query("SELECT * FROM Roles").fetchall():
        tree.insert('', 'end', values=row)

def load_autores(tree):
    for i in tree.get_children():
        tree.delete(i)
    for row in execute_query("SELECT * FROM Autores").fetchall():
        tree.insert('', 'end', values=row)

def load_usuarios(tree):
    for i in tree.get_children():
        tree.delete(i)
    for row in execute_query("SELECT * FROM Usuarios").fetchall():
        tree.insert('', 'end', values=row)

def verificar_admin(usuario, contraseña):
    if usuario == "yorchflrs" and contraseña == "george777":
        messagebox.showinfo("Login Exitoso", "Bienvenido Administrador")
        ventana_administrador()
    else:
        messagebox.showerror("Login Fallido", "Usuario o contraseña incorrectos")

def verificar_bibliotecario(usuario, contraseña):
    messagebox.showinfo("Login Exitoso", "Bienvenido Bibliotecario")
    ventana_bibliotecario()

def login_admin():
    admin_login_window = tk.Toplevel(root)
    admin_login_window.title("Login Administrador")
    center_window(admin_login_window, 300, 150)

    tk.Label(admin_login_window, text="Usuario:", bg='lightblue').grid(row=0, column=0)
    user_entry = tk.Entry(admin_login_window)
    user_entry.grid(row=0, column=1)

    tk.Label(admin_login_window, text="Contraseña:", bg='lightblue').grid(row=1, column=0)
    password_entry = tk.Entry(admin_login_window, show="*")
    password_entry.grid(row=1, column=1)

    tk.Button(admin_login_window, text="Ingresar", command=lambda: verificar_admin(user_entry.get(), password_entry.get())).grid(row=2, column=1)

def login_bibliotecario():
    bibliotecario_login_window = tk.Toplevel(root)
    bibliotecario_login_window.title("Login Bibliotecario")
    center_window(bibliotecario_login_window, 300, 150)

    tk.Label(bibliotecario_login_window, text="Usuario:", bg='lightblue').grid(row=0, column=0)
    user_entry = tk.Entry(bibliotecario_login_window)
    user_entry.grid(row=0, column=1)

    tk.Label(bibliotecario_login_window, text="Contraseña:", bg='lightblue').grid(row=1, column=0)
    password_entry = tk.Entry(bibliotecario_login_window, show="*")
    password_entry.grid(row=1, column=1)

    tk.Button(bibliotecario_login_window, text="Ingresar", command=lambda: verificar_bibliotecario(user_entry.get(), password_entry.get())).grid(row=2, column=1)

def main_window():
    global root, imagen_usuario
    imagen_usuario = None
    root = tk.Tk()
    root.title("Sistema Bibliotecario")
    center_window(root, 400, 300)

    root.configure(background='lightgrey')

    tk.Button(root, text="Administrador", command=login_admin, bg='blue', fg='white').pack(fill=tk.X)
    tk.Button(root, text="Bibliotecario", command=login_bibliotecario, bg='blue', fg='white').pack(fill=tk.X)
    tk.Button(root, text="Estudiante", command=ventana_estudiante, bg='blue', fg='white').pack(fill=tk.X)
    root.mainloop()

if __name__ == "__main__":
    init_db()
    main_window()
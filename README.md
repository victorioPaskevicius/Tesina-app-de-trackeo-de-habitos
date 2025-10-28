# Tesina Habit Tracker App
### Ejecución de la aplicación

1. **Instalar dependencias**  
   - Asegúrate de tener Python y pip instalados.
   - Instala las dependencias con:  
     ```
     pip install -r requirements.txt
     ```
2. **Configurar la base de datos**
   - Utiliza MySQL y crea la base de datos `habit_tracker`.
   - Configura las credenciales en `app/database/db.py`:
     ```python
     connection = mysql.connector.connect(
         host='localhost',
         user='root',
         password='',
         database='habit_tracker'
     )
     ```
3. **Ejecutar la aplicación**
   - Desde la carpeta raíz, ejecuta:
     ```
     python app/app.py
     ```
   - La app corre en el puerto 3001 por defecto.

### Funcionalidades implementadas

- **Registro y login de usuarios**  
  Validación de datos en el frontend y backend.
- **CRUD de hábitos**  
  - Crear, ver, editar y eliminar hábitos.
  - Marcar como completado.
- **Visualización de usuarios registrados**
- **Temporizador por hábito**

### Tecnologías utilizadas

- **Backend:** Python, Flask, MySQL
- **Frontend:** HTML, CSS, JavaScript

### Conexión a la base de datos

- Asegúrate de que MySQL esté corriendo y la base `habit_tracker` exista.
- Modifica usuario y contraseña en `app/database/db.py` si es necesario.

### Pruebas de funcionalidades CRUD

- **Crear:**  
  Usa el botón "Nuevo hábito" en la interfaz.
- **Leer:**  
  Los hábitos y usuarios se listan en la página principal.
- **Actualizar:**  
  Usa el botón "Editar" junto a cada hábito.
- **Eliminar:**  
  Usa el botón "Eliminar" junto a cada hábito.

### Funcionalidades adicionales

- **Validación de formulario:**  
  El registro valida nombre, email, contraseña y teléfono.
- **Temporizador simple para hábitos.**

---


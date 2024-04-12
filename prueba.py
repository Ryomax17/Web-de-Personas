import tkinter as tk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading

def execute_code():
    # Verificar si alguno de los campos está vacío
    if not invoice_id_entry.get() or not custom_text_entry.get("1.0", "end-1c"):
        status_label.config(text="Error: Campos vacíos", fg="red")
        return

    # Verificar que al menos una casilla de verificación esté marcada
    if not any([var.get() for var in checkbox_vars]):
        status_label.config(text="Error: Debes seleccionar al menos un item", fg="red")
        return

    global current_execution
    current_execution = "clon"  # Para mantener la variable global
    if action_var.get() == "realizar_clon":
        thread = threading.Thread(target=execute_clon_thread)
        thread.start()
    elif action_var.get() == "realizar_split":
        thread = threading.Thread(target=execute_split_thread)
        thread.start()

def execute_split_thread():
    try:
        # Obteniendo las variables ingresadas por el usuario
        invoice_id = invoice_id_entry.get()
        custom_text = custom_text_entry.get("1.0", "end-1c")
        checkbox_selections = [checkbox_var.get() for checkbox_var in checkbox_vars]

        # Configuración de Selenium
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=C:/Users/maxi1/AppData/Local/Google/Chrome/User Data/Default")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--incognito")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        # Página web
        driver.get("https://use1.brightpearlapp.com/admin_login.php?clients_id=tiendamia")

        # Inicio de sesión
        username = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email_address']")))
        username.clear()
        username.send_keys("planning-control@tiendamia.com")
        password = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
        password.clear()
        password.send_keys("z!Kd*uR*6u1ViwLX")
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'submit-admin'))).click()

        # Entrar a PO y accionar
        invoice_url = "https://use1.brightpearlapp.com/patt-op.php?scode=invoice&oID={}".format(invoice_id)
        driver.get(invoice_url)

        # Seleccionar elementos según las selecciones del usuario
        selected_ids = []
        for i, selection in enumerate(checkbox_selections, start=1):
            if selection:
                try:
                    # Encontrar el elemento con la clase data-row-id correspondiente a la selección del usuario
                    elemento = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, f'rowNum{i}')))

                    # Obtener id
                    buscar_id = WebDriverWait(elemento, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']")))
                    id_obtenido = buscar_id.get_attribute("data-value")
                    print(id_obtenido)

                    # Agregar el ID seleccionado a la lista de IDs seleccionados
                    selected_ids.append(id_obtenido)

                except Exception as e:
                    print(f"Error al encontrar el id del elemento {i}: {str(e)}")
        time.sleep(1)

        # Construir la parte de la URL para los IDs seleccionados
        ids_part = "&".join([f"ids[{id}]={id}" for id in selected_ids])

        # Entrar al Split y confirmar
        invoice_url = f"https://use1.brightpearlapp.com/p.php?p=warehouse:split-order-rows-to-back-order&orderId={invoice_id}&{ids_part}&maintainPrice=undefined"
        driver.get(invoice_url)

        button_save = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'submit')))
        button_save.click()
        time.sleep(1)

        # Abrir el split

        p_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-content']//p[contains(text(), 'View new back order')]"))
        )
        back_order_link = WebDriverWait(p_element, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )
        link_text = back_order_link.text.strip()
        new_url = f"https://use1.brightpearlapp.com/patt-op.php?scode=invoice&oID={link_text}"

        # Abrir la nueva URL
        driver.get(new_url)
        time.sleep(1)

        # Pegar las notas

        button_notas = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Notes and payment history')]")))
        button_notas.click()
        textarea = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "note_text")))
        textarea.clear()
        textarea.send_keys(custom_text)

        # Cambiar Status del split

        select_list_status = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "titleOrderStatus")))
        select = Select(select_list_status)

        # Obtener la opción seleccionada
        claim_option = claim_options_var.get()

        # Actualizar el valor seleccionado según la opción del usuario
        select_value = None
        if claim_option == "4.1.3 - Product to be Claim":
            select_value = '279'
        elif claim_option == "4.1 Shipped items return/Cancel":
            select_value = '595'
        elif claim_option == "4.1.2 - Products to be Returned":
            select_value = '169'
        elif claim_option == "4.1.3.1 Product to be claim MKT":
            select_value = '723'
        elif claim_option == "4.5 - Refund Complete":
            select_value = '424'

        if select_value:
            select.select_by_value(select_value)

        # Guardar

        button_save_clon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'save-order-btn'))).click()
        time.sleep(5)

        # Mostrar mensaje de éxito
        status_label.config(text="Accion exitosa", fg="green")
        pass

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        pass

    finally:
        # Limpiar campos de entrada
        invoice_id_entry.delete(0, "end")
        custom_text_entry.delete("1.0", "end")
        for var in checkbox_vars:
            var.set(False)

def execute_clon_thread():

    try:
        # Obteniendo las variables ingresadas por el usuario
        invoice_id = invoice_id_entry.get()
        custom_text = custom_text_entry.get("1.0", "end-1c")
        checkbox_selections = [checkbox_var.get() for checkbox_var in checkbox_vars]

        # Configuración de Selenium
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=C:/Users/maxi1/AppData/Local/Google/Chrome/User Data/Default")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--incognito")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        # Página web
        driver.get("https://use1.brightpearlapp.com/admin_login.php?clients_id=tiendamia")

        # Inicio de sesión
        username = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email_address']")))
        username.clear()
        username.send_keys("planning-control@tiendamia.com")
        password = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
        password.clear()
        password.send_keys("z!Kd*uR*6u1ViwLX")
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'submit-admin'))).click()

        # Entrar a PO y accionar
        invoice_url = "https://use1.brightpearlapp.com/patt-op.php?scode=invoice&oID={}".format(invoice_id)
        driver.get(invoice_url)

        # Obtener precios y seleccionar elementos según las selecciones del usuario
        precios_seleccionados = []

        for i, selection in enumerate(checkbox_selections, start=1):
            if selection:
                try:
                    # Encontrar el elemento con la clase data-row-id correspondiente a la selección del usuario
                    elemento = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, f'rowNum{i}')))

                    # Marcar la casilla de verificación
                    checkbox = WebDriverWait(elemento, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox'][value='1']"))).click()

                except Exception as e:
                    print(f"Error al establecer seleccionar el elemento {i}: {str(e)}")

        for i, selection in enumerate(checkbox_selections, start=1):
            if selection:
                try:
                    # Encontrar el elemento con la clase data-row-id correspondiente a la selección del usuario
                    elemento = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, f'rowNum{i}')))

                    # Obtener el precio del elemento y agregarlo a la lista de precios
                    buscar_value = WebDriverWait(elemento, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='itemnet[]'][name='itemnet[]']")))
                    precio = buscar_value.get_attribute("value")
                    precios_seleccionados.append(precio)
                    print(precios_seleccionados)

                except Exception as e:
                    print(f"Error al obtener precio del elemento {i}: {str(e)}")

        button_clon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Clone to Purchase Order')]"))).click()
        time.sleep(1)

        # Obtener la nueva url
        nueva_url = driver.current_url
        driver.execute_script(f"window.history.pushState('data', 'Title', '{nueva_url}')")
        time.sleep(1)

        # Marcar el estado del claim y wh en la nueva página
        select_list_status = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "target_status_po")))
        select = Select(select_list_status)

        # Obtener la opción seleccionada
        claim_option = claim_options_var.get()

        # Actualizar el valor seleccionado según la opción del usuario
        select_value = None
        if claim_option == "4.1.3 - Product to be Claim":
            select_value = '279'
        elif claim_option == "4.1 Shipped items return/Cancel":
            select_value = '595'
        elif claim_option == "4.1.2 - Products to be Returned":
            select_value = '169'
        elif claim_option == "4.1.3.1 Product to be claim MKT":
            select_value = '723'
        elif claim_option == "4.5 - Refund Complete":
            select_value = '424'

        if select_value:
            select.select_by_value(select_value)

        time.sleep(1)

        select_list_WH = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "deliver_to")))
        select = Select(select_list_WH)
        select.select_by_value('66953')
        time.sleep(1)

        button_save_setting_clon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'submitToClone'))).click()
        time.sleep(1)

        # Obtener la nueva url
        nueva_url = driver.current_url
        driver.execute_script(f"window.history.pushState('data', 'Title', '{nueva_url}')")
        time.sleep(1)

        cantidad_checkbox_marcadas = sum(checkbox_selections)
        print("Cantidad de checkbox marcadas:", cantidad_checkbox_marcadas)

        # Iterar sobre los índices de los checkbox seleccionados
        for i in range(1, cantidad_checkbox_marcadas + 1):  # Comenzar desde 1 y sumar 1 a la cantidad
            try:
                # Encontrar el elemento con la clase data-row-id correspondiente a la selección del usuario
                elemento = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, f'rowNum{i}')))

                # Obtener el campo de precio y pegar el precio correspondiente
                buscar_value = elemento.find_element(By.CSS_SELECTOR, "input[id='itemnet[]'][name='itemnet[]']")
                buscar_value.clear()
                buscar_value.send_keys(precios_seleccionados[i - 1])  # Utilizar i - 1 para obtener el precio correcto

            except Exception as e:
                print(f"Error al establecer precio para elemento {i}: {str(e)}")

        # Pegar las notas

        button_notas = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Notes and payment history')]")))
        button_notas.click()

        textarea = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "note_text")))
        textarea.clear()
        textarea.send_keys(custom_text)

        # Guardar

        button_save_clon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'save-order-btn'))).click()
        time.sleep(5)

        # Mostrar mensaje de éxito
        status_label.config(text="Accion exitosa", fg="green")
        pass

    except Exception as e:
        # Mostrar mensaje de error
        status_label.config(text=f"Error: {str(e)}", fg="red")
        pass
    
    finally:
        # Limpiar campos de entrada
        invoice_id_entry.delete(0, "end")
        custom_text_entry.delete("1.0", "end")
        for var in checkbox_vars:
            var.set(False)

# Creando la ventana Tkinter
root = tk.Tk()
root.title("Planning & Control - Automatización de Brightpearl")
root.geometry("350x730")

# Creando un marco para agrupar los elementos relacionados
frame = tk.Frame(root)
frame.pack(pady=20)

# Creando los elementos de entrada
select_action_label = tk.Label(frame, text="Seleccionar acción:", font=("Arial", 12))
select_action_label.pack(pady=5)

action_var = tk.StringVar(root)
action_var.set("realizar_clon")

clon_checkbox = tk.Radiobutton(frame, text="Realizar Clon", variable=action_var, value="realizar_clon")
clon_checkbox.pack(anchor="w")

split_checkbox = tk.Radiobutton(frame, text="Realizar Split", variable=action_var, value="realizar_split")
split_checkbox.pack(anchor="w")

invoice_id_label = tk.Label(frame, text="Número de PO:", font=("Arial", 12))
invoice_id_label.pack(pady=5)

invoice_id_entry = tk.Entry(frame, width=30, font=("Arial", 12))
invoice_id_entry.pack(pady=5)

custom_text_label = tk.Label(frame, text="Notas y comentarios:", font=("Arial", 12))
custom_text_label.pack(pady=5)

# Cambiando el Entry a Text para el campo de notas
custom_text_entry = tk.Text(frame, height=5, width=30, font=("Arial", 12))
custom_text_entry.pack(pady=5)

checkbox_label = tk.Label(frame, text="Seleccionar items a accionar:", font=("Arial", 12))
checkbox_label.pack(pady=5)

checkbox_vars = []
for i in range(8):
    var = tk.BooleanVar(root, value=False)
    checkbox_vars.append(var)
    checkbox = tk.Checkbutton(frame, text=f"Item {i+1}", variable=var, onvalue=True, offvalue=False)
    checkbox.pack(anchor="w")

claim_options_label = tk.Label(frame, text="Estado del claim:", font=("Arial", 12))
claim_options_label.pack(pady=5)

claim_options = [
    "4.1.3 - Product to be Claim",
    "4.1 Shipped items return/Cancel",
    "4.1.2 - Products to be Returned",
    "4.1.3.1 Product to be claim MKT",
    "4.5 - Refund Complete"
]

claim_options_var = tk.StringVar(root)
claim_options_var.set(claim_options[0])  # Valor por defecto

claim_options_menu = tk.OptionMenu(frame, claim_options_var, *claim_options)
claim_options_menu.pack(pady=5)

# Botón para ejecutar el código
execute_button = tk.Button(root, text="Ejecutar", command=execute_code, font=("Arial", 12))
execute_button.pack(pady=10)

# Etiqueta para mostrar el estado de la acción
status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack()

root.mainloop()
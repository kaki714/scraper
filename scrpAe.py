import argparse
import json
import requests
from bs4 import BeautifulSoup
import re

class Producto:
    def __init__(self, id, nombre, precio, href):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.href = href

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'href': self.href
            
        }
    
def cargar_lista_json(archivo_json):
    try:
        with open(archivo_json, 'r', encoding='utf-8') as json_file:
            productos_data = json.load(json_file)
            # Crear instancias de Producto a partir de los datos almacenados
            return [Producto(item['id'], item['nombre'], item['precio'], item['href']) for item in productos_data]
    except FileNotFoundError:
        return []

def producto_existe(producto, lista):
    # Verificar si el producto ya existe en la lista
    return any(item.nombre == producto.nombre and  item.href == producto.href for item in lista)

def obtener_ultimo_id(productos):
    # Obtener el último valor del campo 'id' en la lista
    ids = []
    for producto in productos:
        id = producto.id
        ids.append(id) 
    
    return max(ids,default=0)
  
def truncar_url_hasta_html(url):
    # Buscar la cadena ".html" en la URL
    if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

    match = re.search(r'(.html)', url)
    if match:
        # Si se encuentra, truncar la URL hasta ese punto
        truncated_url = url[:match.end()]
        return truncated_url
    else:
        # Si no se encuentra ".html" en la URL, devolver la URL original
        return url


def obtener_productos(url, archivo_json):
    # Realizar la solicitud HTTP y obtener el contenido HTML
    response = requests.get(url)
    html_content = response.content

    # Crear un objeto BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    

    lista_existente = cargar_lista_json(archivo_json)
    

   

 # Obtener el último valor del campo 'id' en la lista
 
    ultimo_id = obtener_ultimo_id(lista_existente)
    
    # Buscar los elementos div con la clase "info" que contienen un enlace con target="_blank"
    productos_info = soup.find_all('div', class_='list--gallery--C2f2tvm search-item-card-wrapper-gallery')
   
    id = ultimo_id
    # Obtener y imprimir los atributos href de los enlaces dentro de los elementos "info"
    for producto_info in productos_info:
        enlace = producto_info.find('a', class_='multi--container--1UZxxHY cards--card--3PJxwBm search-card-item')
        div_precio = producto_info.find('div', class_='multi--price-sale--U-S0jtj')
        nombre = producto_info.find('h3', class_='multi--titleText--nXeOvyr')
        if enlace:
            nombre_completo = nombre.text.strip()
            nombre = nombre_completo[:80] if len(nombre_completo) > 80 else nombre_completo.split(',')[0]
            href = enlace.get('href')
            href = truncar_url_hasta_html(href)
            
            strprecio = ''.join(span.text for span in div_precio.find_all('span')[:-1])
            strprecio = strprecio.replace(',', '.')
            precio= float(strprecio)
            
            # Incrementar el valor del 'id' para el nuevo producto
            
            if nombre and precio and href:
                id = ultimo_id+1
                producto = Producto(id, nombre, precio, href)
                if not producto_existe(producto, lista_existente):
                    ultimo_id += 1
                    producto = Producto(ultimo_id, nombre, precio, href)
                    
                    lista_existente.append(producto)
                
        
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        # Convertir los objetos Producto a diccionarios antes de guardar
        productos_data = [producto.to_dict() for producto in lista_existente]
        json.dump(productos_data, json_file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Obtener nombres y href de productos de una URL.')
    parser.add_argument('url', type=str, help='URL de la página web')
    parser.add_argument('output_file', type=str, help='Nombre del archivo JSON de salida')

    # Obtener la URL proporcionada como argumento
    args = parser.parse_args()
    url = args.url
    output_file = args.output_file

    # Llamar a la función con la URL proporcionada
    obtener_productos(url, output_file)

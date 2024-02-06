import argparse
import requests
import json
from bs4 import BeautifulSoup

def cargar_lista_json(archivo_json):
    try:
        with open(archivo_json, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []

def obtener_productos_y_actualizar_json(url, archivo_json):
    # Realizar la solicitud HTTP y obtener el contenido HTML
    response = requests.get(url)
    html_content = response.content

    # Crear un objeto BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Cargar la lista existente desde el archivo JSON
    lista_existente = cargar_lista_json(archivo_json)

    # Buscar los elementos div con la clase "info" que contienen un enlace con target="_blank"
    productos_info = soup.find_all('div', class_='card_info list-card-layout__info')

    # Obtener y agregar la información de los productos a la lista existente
    for producto_info in productos_info:
        enlace = producto_info.find('a', {'target': '_blank'})
        if enlace:
            nombre = producto_info.text.strip()
            href = enlace.get('href')
            if nombre and href:
                lista_existente.append({'nombre': nombre, 'href': href})

    # Guardar la lista actualizada en el archivo JSON
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        json.dump(lista_existente, json_file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Obtener y actualizar información de productos en un archivo JSON.')
    parser.add_argument('url', type=str, help='URL de la página web')
    parser.add_argument('output_file', type=str, help='Nombre del archivo JSON de salida')

    # Obtener la URL y el nombre del archivo JSON proporcionados como argumentos
    args = parser.parse_args()
    url = args.url
    output_file = args.output_file

    # Llamar a la función con la URL y el nombre del archivo JSON proporcionados
    obtener_productos_y_actualizar_json(url, output_file)

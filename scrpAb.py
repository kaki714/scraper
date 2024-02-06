import argparse
import json
import requests
from bs4 import BeautifulSoup


def cargar_lista_json(archivo_json):
    try:
        with open(archivo_json, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []


def obtener_productos(url, archivo_json):
    # Realizar la solicitud HTTP y obtener el contenido HTML
    response = requests.get(url)
    html_content = response.content

    # Crear un objeto BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    

    lista_existente = cargar_lista_json(archivo_json)

    # Buscar los elementos div con la clase "info" que contienen un enlace con target="_blank"
    productos_info = soup.find_all('div', class_='card-info list-card-layout__info')
   

    # Obtener y imprimir los atributos href de los enlaces dentro de los elementos "info"
    for producto_info in productos_info:
        enlace = producto_info.find('a', {'target': '_blank'})
        if enlace:
            href = enlace.get('href')
            nombre = producto_info.text.strip()
            if href:
                print(f'Nombre: {nombre}, Href: {href}')
                lista_existente.append(f"nombre: {nombre} , url: {href}")
    
     # Guardar la lista actualizada en el archivo JSON
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        json.dump(lista_existente, json_file, ensure_ascii=False, indent=2)


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

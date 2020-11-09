import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import unicodedata

# Preparamos variables
url_list = list()
productos = list()

#
# Comenzaremos descargando el mapa de la pagina desde  https://www.expert.es/sitemap_index.xml
url = "https://www.expert.es/sitemap_index.xml"

# Para evitar los bloqueos simularemos ser un navegador e incluso cambiaremos de user_agent para
# evitar los bloqueos en las paginas de los productos.
# Informacion de los user agent obtenida de https://developers.whatismybrowser.com/useragents/explore/
# User-Agent: Mozilla/<version> (<system-information>) <platform> (<platform-details>) <extensions>
user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]

print("Iniciamos web scraping...")

# Generamos la consulta
user_agent = random.choice(user_agent_list)
headers = {'User-Agent': user_agent}
page = requests.get(url,headers=headers)

if (page.status_code == 200):

    # Esperamos un tiempo para simular el usuario
    time.sleep(1)
    # Extraemos las etiquetas loc de los enlaces a las paginas
    soup = BeautifulSoup(page.content, 'html.parser')
    url_sitemap = soup.findAll("loc")
    #print(url_sitemap)

    # Recorremos cada una de las paginas buscando enlaces a paginas de productos.
    print("...Recorremos las paginas")
    for each_site in url_sitemap:
        
        # Generamos la consulta
        user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}
        page = requests.get(each_site.text,headers=headers)
        print ("%s , %i" %(each_site.text, page.status_code))

        if (page.status_code == 200):
            print("...Buscamos productos")
            soup = BeautifulSoup(page.content, 'html.parser')
            #print(soup)
            full_tag = soup.findAll("loc")
            #print(full_tag)
            
            for each_tag in full_tag:
                # Filtramos para quedarnos solo con las del dominio /producto
                if each_tag.text.find('https://www.expert.es/producto/') != -1:
                    print(each_tag.text)
                    url_list.append(each_tag.text)
    
        # Esperamos un tiempo aleatorio entre peticiones del bucle
        time.sleep(1 + random.randrange(5))
    
    # Comprobamos
    print ("...Se han encontrado %i enlaces" %len(url_list))
    #print(url_list)

else:
    print("La pagina solicitada no responde!")
    print("......Respuesta de la pagina : ", page.status_code)

# ------------------------------------------------------------------------------------------
if len(url_list) == 0:
     
    # Como hemos sido "Baneados" cargo un fichero de texto obtenido de las paginas 
    # https://www.expert.es/product-sitemap1.xml
    # https://www.expert.es/product-sitemap1.xml
    # https://www.expert.es/product-sitemap3.xml
    # antes del bloqueo, y continuamos el script como si lo hubieramos obtenido de la web.
    
    print("Leemos el fichero de texto...")
    url_list = list()
    url_file = open('sites.txt')
    for linea in url_file:
        url_list.append(linea.replace("\n",""))
    print ("...Se han encontrado %i enlaces" %len(url_list))
# -------------------------------------------------------------------------------------------

# Recorremos cada una de las paginas del producto obteniendo la descripcion y el precio.    
print("Recorremos los sites...")

f =  open('electrodata.csv', 'w', newline='',encoding="utf-8")
f.write("Descripcion,Precio,Agotado,Categoria\n")

descripcion = ""
precio = ""
agotado = "NO"
categoria = ""

for url in url_list:
    
     # Generamos la consulta
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    page = requests.get(url,headers=headers)
    print ("%s , %i" %(url, page.status_code))
    
    if (page.status_code == 200):
        
        #time.sleep(1)
        
        print("...Buscamos los datos de los productos")
        soup = BeautifulSoup(page.content, 'html.parser')
        #print(soup)
        
        try:
            # Nombre/Titulo del producto
            # Ejemplo:
            # <h1 class="product_title entry-title" itemprop="name">ENCIMERA GAS ELECTROLUX EGT6633NOK</h1>
            #print ("...Obtenemos los nombres")
            tags = soup.find('h1', class_='product_title entry-title')
            descripcion = tags.getText()
            # Forzamos la normalización
            descripcion=unicodedata.normalize("NFKD",descripcion)
            
            # Precio del producto
            # Ejemplo:
            # #<span class="product-price"><span class="woocommerce-Price-amount amount">550<span class="woocommerce-Price-currencySymbol">€</span></span></span>
            #print ("...Obtenemos los precios")
            # Reemplazamos la coma por el punto y eliminamos el caracter €
            tags = soup.find('span', class_='product-price')
            precio = tags.getText()
            precio = precio.replace(",",".")
            precio = precio.replace('€','')
             # Forzamos la normalización
            precio=unicodedata.normalize("NFKD",precio)
            
            # Categoria del producto
            #print ("...Obtenemos la categoria")
            ##tags=soup.find('div', class_='col-wrapper title-wrapper')
            tags = soup.find('nav', class_= 'like-h1-style woocommerce-breadcrumb')
            categoria = tags.getText()
            # Recortamos la cadena
            categoria = categoria[1:categoria.find("|")]
            # Forzamos la normalización
            categoria=unicodedata.normalize("NFKD",categoria)
            
            # Existencia del producto
            # En algunos productos hemos encontrado este flag
            # que queremos registar tambien.
            #print("....Miramos si está agotado")
            tags=None
            agotado = "NO"
            tags=soup.find('div', class_='out-of-stock-flag')
            if (tags):
                agotado="SI"
             # Forzamos la normalización
            agotado=unicodedata.normalize("NFKD",agotado)
            
            print ("%s,%s,%s,%s" %(descripcion, precio, agotado, categoria))
            f.write("%s,%s,%s,%s\n" %(descripcion, precio, agotado, categoria))   
        
        except:
            print("...No se pudo encontrar alguno de los datos.")

    time.sleep(1)
    #time.sleep(1 + random.randrange(5))

f.close()

# TEST Ábaco Latam

Test para el proceso de selección empresa Ábaco Latam

## Usage

Renombrar archivo `.env.example` a `.env` y sustituir con las credenciales reales
```bash
python -m virutalenv
```
```bash
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
```bash
python main.py
```

## Decisiones

### Autenticación
Para el proceso de login, en un primer momento se intentó directamente haciendo las peticiones en python, pero la web tiene un captcha, por lo que aún siendo menos eficiente, era necesario hacerlo con puppeteer. Una vez obtenidas las cookies, cerramos el browser y estas se ponen en una session. A partir de entonces se trabaja solo con esta session.
Con la librería `retrying`, concretamente con el decorador de `retry`, en caso de que salte alguna excepción durante la función de login, esta se ejecutará de nuevo, con las condiciones que le marco en los parámetros.

### Estructura de classes
Se ha cambiado ligeramente la classe abstracta proporcionada, para que reciba el username y la password en la constructora de esta, ya que se necesitavan estos valores en otras funciones y consideré que quedaba más ordenado.
Se ha creado la classe `BandCampScrapper` que implementa la classe abstracta llamada `AbstractScrappingClass`. La classe `BandCampScrapper` tiene diferentes métodos privados para obtener los datos de manera mas limpia.

### Obtención de datos
Una vez realizado el login, la información que buscamos se obtiene haciendo las peticiones con la session y después parseando el contenido con la ayuda de la libreria `BeautifulSoup`.

### Estructuras de datos
En relación a las estructuras de datos usadas, solo tenemos listas y un set. El set se usa para guardar los géneros que se siguen, en principio no deberían haber repetidos de la manera en que los obtenemos, pero dado que es seguro que no se puede seguir un genero 2 veces, el set nos permite mantener este control sin hacer comprobaciones a parte.
Para representar un album, se usa un diccionario, de manera que podemos tener en diferentes atributos los valores que nos interesan.
Por lo demas se usan listas, dado que la muestra era bastante pequeña, es lo más senzillo y cómodo. En caso de que la muestra fuera mucho más grande, se podria estructurar diferente, y buscando mejoras para, por ejemplo, evitar el coste de comprobar si los tags de un album estan dentro de los tags seguidos, etc.


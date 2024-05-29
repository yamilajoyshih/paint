import gamelib
import png

# Colores
colores = {
    "NEGRO": "#000000",
    "BLANCO": "#FFFFFF",
    "ROJO": "#FF0000",
    "VERDE": "#00FF00",
    "AZUL": "#0000FF",
    "AMARILLO": "#FFFF00",
    "ROSA": "#FF00FF"
}

# Dimensiones de la ventana y la imagen
W, H = 600, 700
TOOLBAR = H - W
COLOR_FONDO = colores["BLANCO"]
LINEA_DE_FONDO = True

# Posición del botón en Y
BOTON_Y = H - TOOLBAR // 2 - 25

def colorear(paint, colores):
    for i, (color, hex_code) in enumerate(colores.items()):
        x = 10 + i * 50 
        gamelib.draw_rectangle(x, H - 65, x + 40, H - 45, fill=colores[color])


def obtener_color_seleccionado(ev):
    x= ev.x
    if BOTON_Y - 20 <= ev.y <= BOTON_Y + 60:
        for color, hex_code in colores.items():
            button_x= 10 + list(colores.keys()).index(color) * 50
            button_x_start= button_x
            button_x_end= button_x + 40
            if button_x_start <= x <= button_x_end:
                return hex_code
    return None 

def crear_imagen_vacia(ancho, alto):
    '''inicializa el estado del programa con una imagen vacía de ancho x alto pixels'''
    imagen_vacia = []
    for _ in range(ancho):
        fila = [COLOR_FONDO] * alto
        imagen_vacia.append(fila)
    return imagen_vacia

def dibujar_interfaz(paint, color_seleccionado):
    '''dibuja la interfaz de la aplicación en la ventana'''
    ancho= len(paint[0])
    alto= len(paint)
    gamelib.draw_begin()
    gamelib.draw_rectangle(0, 0, W, H, fill=COLOR_FONDO)
    gamelib.draw_text("NOTA: tecla g: guardar PPM - tecla c: cargar PPM - tecla s: guardar PNG - tecla a: ingresar un color", W // 2, H - 20, size=12, fill=colores["ROJO"])
    gamelib.draw_text(f"Color seleccionado: {color_seleccionado}",TOOLBAR, BOTON_Y, size=14, fill=colores["NEGRO"])
    pixel_size= W// len(paint[0])
    for i in range(alto):
        for j in range(ancho):
            x = j * pixel_size
            y = i * pixel_size
            gamelib.draw_rectangle(x, y, x + pixel_size, y + pixel_size, fill=paint[i][j])
    
    if LINEA_DE_FONDO:
        for i in range(ancho + 1):
            x = i * pixel_size
            gamelib.draw_line(x, 0, x, H - TOOLBAR, fill=colores["NEGRO"], width=2)
        for i in range(alto + 1):
            y = i * pixel_size
            gamelib.draw_line(0, y, W, y, fill=colores["NEGRO"], width=2)
    colorear(paint, colores)
    gamelib.draw_end()


def cargar_ppm(paint, archivo_ppm):
    with open (archivo_ppm, "r") as archivo:
        encabezado= next(archivo).strip()
        if encabezado != "P3":
            raise ValueError("El archivo PPM no tiene formato válido.")
        dimensiones = next(archivo).strip().split()
        ancho, alto = map(int, dimensiones)
        next(archivo)
        imagen=[]
        for _ in range (alto):
            fila=[]
            for _ in range (ancho):
                valores_rgb = next(archivo).split()
                r, g, b = int(valores_rgb[0]), int(valores_rgb[1]), int(valores_rgb[2])
                color= f"#{r:02x}{g:02x}{b:02x}" 
                fila.append(color)
            imagen.append(fila)
    return imagen, ancho, alto

def guardar_ppm(paint, archivo_ppm):
    '''guarda la imagen en un archivo PPM'''
    ancho= len(paint[0])
    alto= len(paint)
    with open(archivo_ppm, 'w') as archivo:
        archivo.write("P3\n")
        archivo.write(f"{ancho} {alto}\n")
        archivo.write("255\n")
        for fila in paint:
            for color in fila:
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                archivo.write(f"{r} {g} {b}\n")

def obtener_paleta(paint):
    paleta = []
    for fila in paint:
        for color in fila:
            if color not in paleta:
                paleta.append(color)
    return paleta

def obtener_imagen(paint, paleta):
    imagen = []
    for fila in paint:
        fil = []
        for color in fila:
            imagenes = paleta.index(color)
            fil.append(imagenes)
        imagen.append(fil)
    return imagen

def transformar_paleta(paleta):
    new = []
    for color in paleta:
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        new.append((r,g,b))
    return new

def guardar_png(paint, archivo_png):
    paleta = obtener_paleta(paint)
    imagen = obtener_imagen(paint, paleta)
    png.escribir(archivo_png, transformar_paleta(paleta), imagen)


def main():
    gamelib.title("AlgoPaint")
    gamelib.resize(W, H)

    paint = crear_imagen_vacia(50, 50)
    pixel_size= W// len(paint[0])
    color_seleccionado = colores["NEGRO"]

    while gamelib.loop(fps=15):
        dibujar_interfaz(paint, color_seleccionado)

        for ev in gamelib.get_events():
            if ev.type == gamelib.EventType.ButtonPress and ev.mouse_button == 1:
                if ev.y < H - TOOLBAR:
                    pixel_x = ev.x // pixel_size
                    pixel_y = ev.y // pixel_size
                    paint[pixel_y][pixel_x] = color_seleccionado
                    dibujar_interfaz(paint, color_seleccionado)
                else:
                    color_seleccionado= obtener_color_seleccionado(ev)
                print(f'Se ha presionado el botón del mouse: {ev.x} {ev.y}')
            
            elif ev.type == gamelib.EventType.KeyPress:
                if ev.key== "c":
                    archivo_ppm= gamelib.input("Ingrese la ruta del archivo PPM: ")
                    if archivo_ppm is not None:
                        try:
                            paint, ancho, alto= cargar_ppm(paint, archivo_ppm)
                        except FileNotFoundError:
                            gamelib.say(f"no se encontró el archivo: {archivo_ppm}")
                    else:
                        gamelib.say("carga de archivo cancelada")

                if ev.key == "g":
                    archivo_ppm= gamelib.input("Ingrese el nombre del archivo PPM para guardar:")
                    if archivo_ppm is not None:
                        try:
                            guardar_ppm(paint, archivo_ppm)
                            gamelib.say("imagen guardada correctamente")
                        except FileNotFoundError:
                            gamelib.say("imagen no guardada")
                    else:
                        gamelib.say("guardar imagen cancelada")   

                if ev.key == "s":
                    archivo_png= gamelib.input("Ingrese el nombre del archivo PNG para guardar:")
                    if archivo_png is not None:
                        try:
                            guardar_png(paint, archivo_png)
                            gamelib.say("imagen guardada correctamente")
                        except FileNotFoundError:
                            gamelib.say("imagen no guardada")
                    else:
                        gamelib.say("guardar imagen cancelada")

                if ev.key == "a":
                    color= gamelib.input("Ingrese un color (formato #rrggbb): ")
                    if len(color) == 7 and color[0]== "#" and all(c in "0123456789abcdef" for c in color[1:].lower()):
                        color_seleccionado= color.lower()
                        if color not in colores:
                            colores[color]= color
                            colorear(paint, colores)
                    else:
                        gamelib.say("el color no esta con el formato correcto")
                    


                print(f'Se ha presionado la tecla: {ev.key}')


gamelib.init(main)
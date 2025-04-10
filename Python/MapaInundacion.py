"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import os
from datetime import datetime
import plotly.graph_objects as go

# Función para generar un gráfico de pastel con Plotly y guardarlo como SVG
def generarGrafico(valores_suma, valores_suma_vulnerable, salida_svg):
    arcpy.AddMessage("Generando gráfico con Plotly...")
    
    # Obtener los nombres de los riesgos
    riesgos = list(valores_suma.keys())
    # Extraer valores para cada categoría de riesgo
    total = [valores_suma[r] for r in riesgos]
    values = list(valores_suma.values())

    # Asignar colores personalizados por categoría
    colores = {
        "Bajo": "#98E600",       # verde
        "Medio": "#E6E600",      # amarillo
        "Alto": "#E64C00",       # naranja oscuro
        "Muy alto": "#E60000"    # rojo intenso
    }
    colors = [colores[cat] for cat in riesgos]

    # Crear el gráfico de pastel
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=riesgos, 
                         values=values, 
                         marker=dict(colors=colors), 
                         textfont=dict(size=30)))
    fig.update_layout(showlegend=False)

    # Guardar gráfico como imagen SVG
    fig.write_image(salida_svg, width=600, height=600)
    arcpy.AddMessage(f"Gráfico guardado en: {salida_svg}")

# Función para calcular los valores agregados desde la capa
def calcularTabla(aprx, nombre_layout):
    arcpy.AddMessage(f"Calculando Valores")
    print(f"Calculando Valores")

    # Nombre del mapa y capa específicos del proyecto
    nombre_mapa = "Inundacion"
    nombre_capa = "Censo población en Riesgo Inundación 2024"

    # Obtener el mapa y la capa
    mapa = aprx.listMaps(nombre_mapa)[0]
    capa = mapa.listLayers(nombre_capa)[0]

    # Obtener el layout
    layout = aprx.listLayouts(nombre_layout)[0]

    # Categorías de riesgo
    riesgos = ["Bajo", "Medio", "Alto", "Muy alto"]

    campo = "riesgo"
    campos_suma = ["pob_vulnerable", "total"]  # Campos a sumar

    # Inicializar diccionarios para guardar sumas
    valores_suma = {r: 0 for r in riesgos}
    valores_suma_vulnerable = {r: 0 for r in riesgos}
    valores_suma_porcentaje = {r: 0 for r in riesgos}

    # Recorrer cada nivel de riesgo y sumar valores
    for riesgo in riesgos:
        where = f"{campo} = '{riesgo}'"
        with arcpy.da.SearchCursor(capa, campos_suma, where) as cursor:
            for row in cursor:
                valores_suma_vulnerable[riesgo] += row[0]
                valores_suma[riesgo] += row[1]

    # Calcular porcentaje por riesgo
    total_poblacion = sum(valores_suma.values())
    for riesgo in riesgos:
        valores_suma_porcentaje[riesgo] = round(valores_suma[riesgo] / total_poblacion * 100, 2)

    return valores_suma, valores_suma_vulnerable, valores_suma_porcentaje

# Función que actualiza textos e imágenes dentro del layout
def modificarElementosLayout(layout, author, valores_suma, valores_suma_vulnerable, valores_suma_porcentaje, svg_output):
    arcpy.AddMessage(f"Modificando elementos")

    for element in layout.listElements("TEXT_ELEMENT"):
        # Asignar autor y fecha
        if "autor" in element.name.lower():
            element.text = f"ELABORADO POR: {author}"
        elif "fecha" in element.name.lower():
            fecha = datetime.now().strftime("%d/%m/%Y")
            element.text = f"FECHA DE ELABORACIÓN: {fecha}"

        # Insertar valores de población vulnerable
        elif 'riesgo_bajo_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Bajo"]
        elif 'riesgo_medio_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Medio"]
        elif 'riesgo_alto_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Alto"]        
        elif 'riesgo_muy_alto_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Muy alto"]

        # Insertar valores totales
        elif 'riesgo_bajo_total' in element.name.lower():
            element.text = valores_suma["Bajo"]
        elif 'riesgo_medio_total' in element.name.lower():
            element.text = valores_suma["Medio"]
        elif 'riesgo_alto_total' in element.name.lower():
            element.text = valores_suma["Alto"]        
        elif 'riesgo_muy_alto_total' in element.name.lower():
            element.text = valores_suma["Muy alto"]

        # Insertar porcentajes
        elif 'riesgo_bajo_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Bajo"]} %'
        elif 'riesgo_medio_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Medio"]} %'
        elif 'riesgo_alto_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Alto"]} %'
        elif 'riesgo_muy_alto_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Muy alto"]} %'

    # Reemplazar el gráfico en el layout
    for imgElement in layout.listElements("PICTURE_ELEMENT"):
        if imgElement.name == 'grafico':
            imgElement.sourceImage = svg_output

# Función principal que genera todo el informe
def imprimir_layout(nombre_salida_pdf, author):
    try:
        arcpy.AddMessage(f"Inicio Proceso")

        # Ruta fija del proyecto
        aprx_path = r"C:\MasterGISXVI_Contenidos\PFM\ProyectoFinal\ProyectoFinal.aprx"
        arcpy.AddMessage(f"Ruta de proyecto: {aprx_path}")

        # Cargar el proyecto
        aprx = arcpy.mp.ArcGISProject(aprx_path)

        # Obtener el layout principal
        nombre_layout = 'MapaRiesgoInundacion'
        layout = aprx.listLayouts(nombre_layout)[0]

        # Calcular totales, vulnerables y porcentajes
        valores_suma, valores_suma_vulnerable, valores_suma_porcentaje = calcularTabla(aprx, nombre_layout)

        # Crear el gráfico SVG en la carpeta temporal
        svg_output = "{0}\grafico.svg".format(arcpy.env.scratchFolder)
        generarGrafico(valores_suma, valores_suma_vulnerable, svg_output)

        # Modificar los elementos del layout con los valores calculados
        modificarElementosLayout(layout, author, valores_suma, valores_suma_vulnerable, valores_suma_porcentaje, svg_output)

        # Exportar el layout como PDF
        salida_pdf = "{0}\{1}.pdf".format(arcpy.env.scratchFolder, nombre_salida_pdf)
        arcpy.AddMessage(f"Ruta de salida: {salida_pdf}")
        layout.exportToPDF(salida_pdf)

        # Devolver la ruta del PDF como salida de herramienta
        arcpy.SetParameterAsText(2, salida_pdf)
        print(f"salida: {salida_pdf}")

    except Exception as e:
        arcpy.AddError(f"Error: {str(e)}")
        print(f"Error: {str(e)}")

# Punto de entrada cuando se ejecuta como herramienta en ArcGIS
if __name__ == '__main__':
    pdf_name = arcpy.GetParameterAsText(0)  # Nombre del archivo PDF de salida
    author = arcpy.GetParameterAsText(1)    # Autor a mostrar en el layout
    imprimir_layout(pdf_name, author)

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
def generarGrafico(valores_suma, valores_suma_vulnerable, salida_svg):
    arcpy.AddMessage("Generando gráfico con Plotly...")
    
    riesgos = list(valores_suma.keys())
    total = [valores_suma[r] for r in riesgos]
    values = list(valores_suma.values())
    # Colores personalizados
    colores = {
        "Muy bajo": "D1FF73",       # verde claro
        "Bajo": "#98E600",       # verde
        "Medio": "#E6E600",      # naranja
        "Alto": "#E64C00",       # rojo
        "Muy alto": "#E60000"    # morado
    }
    colors = [colores[cat] for cat in riesgos]
    fig = go.Figure()
    
    fig.add_trace(go.Pie(labels=riesgos, 
                         values=values, 
                         marker=dict(colors=colors), 
                         textfont=dict(size=30)
                         )
                  )
    fig.update_layout(showlegend=False)
    fig.write_image(salida_svg, width=600, height=600)
    arcpy.AddMessage(f"Gráfico guardado en: {salida_svg}")
    
def calcularTabla(aprx, nombre_layout):
    arcpy.AddMessage(f"Calculando Valores")
    print(f"Calculando Valores")
    # Nombre del mapa y capa a usar
    nombre_mapa = "IslasCalor"  # o el nombre de tu mapa
    nombre_capa = "Censo población en Riesgo Islas de Calor 2024"  # o el nombre de capa
    
    # Obtener el mapa y la capa
    mapa = aprx.listMaps(nombre_mapa)[0]
    capa = mapa.listLayers(nombre_capa)[0]
    # Buscar el layout por nombre
    layout = aprx.listLayouts(nombre_layout)[0]
    riesgos = [
        "Muy bajo",
        "Bajo",
        "Medio",
        "Alto",
        "Muy alto"
    ]
    campo = "impacto_confort_termico"
    campos_suma = ["pob_vulnerable",
    "total",
    ]
    valores_suma = { "Muy bajo": 0,
        "Bajo": 0,
        "Medio": 0,
        "Alto": 0,
        "Muy alto" : 0
        }
    valores_suma_vulnerable = {"Muy bajo": 0, 
        "Bajo": 0,
        "Medio": 0,
        "Alto": 0,
        "Muy alto" : 0
        }
    valores_suma_porcentaje = { "Muy bajo": 0,
        "Bajo": 0,
        "Medio": 0,
        "Alto": 0,
        "Muy alto" : 0
        }
    for riesgo in riesgos:
        where = f"{campo} = '{riesgo}'"
        with arcpy.da.SearchCursor(capa, campos_suma, where) as cursor:
            for row in cursor:
                valores_suma_vulnerable[riesgo] += row[0]
                valores_suma[riesgo] += row[1]
    for riesgo in riesgos:
        valores_suma_porcentaje[riesgo] = round(valores_suma[riesgo] / sum(valores_suma.values()) * 100, 2)
    return valores_suma, valores_suma_vulnerable, valores_suma_porcentaje
def modificarElementosLayout(layout, author, valores_suma, valores_suma_vulnerable, valores_suma_porcentaje, svg_output):
    arcpy.AddMessage(f"Modificando elementos")
    for element in layout.listElements("TEXT_ELEMENT"):
        if "autor" in element.name.lower():
            element.text = f"ELABORADO POR: {author}"
        elif "fecha" in element.name.lower():
            fecha = datetime.now().strftime("%d/%m/%Y")
            element.text = f"FECHA DE ELABORACIÓN: {fecha}"
        elif 'riesgo_muy_bajo_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Muy bajo"]
        elif 'riesgo_bajo_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Bajo"]
        elif 'riesgo_medio_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Medio"]
        elif 'riesgo_alto_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Alto"]        
        elif 'riesgo_muy_alto_vulnerable' in element.name.lower():
            element.text = valores_suma_vulnerable["Muy alto"]
        elif 'riesgo_muy_bajo_total' in element.name.lower():
            element.text = valores_suma["Muy bajo"]
        elif 'riesgo_bajo_total' in element.name.lower():
            element.text = valores_suma["Bajo"]
        elif 'riesgo_medio_total' in element.name.lower():
            element.text = valores_suma["Medio"]
        elif 'riesgo_alto_total' in element.name.lower():
            element.text = valores_suma["Alto"]        
        elif 'riesgo_muy_alto_total' in element.name.lower():
            element.text = valores_suma["Muy alto"]
        elif 'riesgo_bajo_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Bajo"]} %'
        elif 'riesgo_muy_bajo_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Muy bajo"]} %'
        elif 'riesgo_medio_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Medio"]} %'
        elif 'riesgo_alto_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Alto"]} %'
        elif 'riesgo_muy_alto_porcentaje' in element.name.lower():
            element.text = f'{valores_suma_porcentaje["Muy alto"]} %'
    for imgElement in layout.listElements("PICTURE_ELEMENT"):
        if imgElement.name == 'grafico':
            imgElement.sourceImage = svg_output
    
def imprimir_layout(nombre_salida_pdf, author):
    try:
        arcpy.AddMessage(f"Inicio Proceso")
        # Ruta del proyecto
        aprx_path = r"C:\MasterGISXVI_Contenidos\PFM\ProyectoFinal\ProyectoFinal.aprx"
        arcpy.AddMessage(f"Ruta de proyecto: {aprx_path}")
        aprx = arcpy.mp.ArcGISProject(aprx_path)
        
        # Buscar el layout por nombre
        nombre_layout = 'MapaRiesgoIslasCalor'
        layout = aprx.listLayouts(nombre_layout)[0]
        
        valores_suma, valores_suma_vulnerable, valores_suma_porcentaje = calcularTabla(aprx, nombre_layout)
        
        #Generar grafico
        svg_output = "{0}\grafico.svg".format(arcpy.env.scratchFolder)
            
        generarGrafico(valores_suma, valores_suma_vulnerable, svg_output)
        
        # Modificar elementos del layout
        modificarElementosLayout(layout, author, valores_suma, valores_suma_vulnerable, valores_suma_porcentaje, svg_output)
        
        
        # Ruta de salida (como PDF)
        salida_pdf = "{0}\{1}.pdf".format(arcpy.env.scratchFolder, nombre_salida_pdf)# Eliminar el archivo si ya existe
        arcpy.AddMessage(f"Ruta de salida: {salida_pdf}")
        layout.exportToPDF(salida_pdf)
        
        arcpy.SetParameterAsText(2, salida_pdf)  # Para devolver la ruta como salida
        print(f"salida: {salida_pdf}")
    except Exception as e:
        arcpy.AddError(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
# Entradas (como parámetros de herramienta)
if __name__ == '__main__':
    pdf_name = arcpy.GetParameterAsText(0)            # Nombre del archivo PDF
    author = arcpy.GetParameterAsText(1)              # Autor
    
    imprimir_layout(pdf_name, author)

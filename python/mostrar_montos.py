import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tabulate import tabulate
import numpy as np

def process_excel(file_path):
    try:
        # Leer el archivo Excel con manejo de errores
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Mostrar tabla en consola
        print("\nVista previa de los datos:")
        print(tabulate(df.head(), headers='keys', tablefmt='pretty', showindex=False))
        
        # Generar y guardar gráficos
        generate_charts(df)
        
        print("\nGráficos generados como 'grafico_*.png' en el directorio actual")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def generate_charts(df):
    try:
        # Seleccionar y limpiar columnas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            print("Advertencia: No se encontraron columnas numéricas para graficar")
            return
            
        # Limpieza exhaustiva de datos
        df_clean = df[numeric_cols].copy()
        df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
        df_clean = df_clean.dropna()
        
        if len(df_clean) == 0:
            print("Advertencia: No hay datos válidos después de la limpieza")
            return

        # Gráfico de barras
        df_clean.plot(kind='bar')
        plt.title("Gráfico de Barras")
        plt.tight_layout()
        plt.savefig('grafico_barras.png')
        plt.close()
        
        # GRÁFICO DE PIE CON MÁS CONTROL
        plt.figure(figsize=(12, 8))
        
        # Preparar datos para el pie
        pie_data = df_clean[numeric_cols[0]]
        pie_data = pie_data[pie_data > 0]  # Solo valores positivos
        
        if len(pie_data) == 0:
            print("Advertencia: No hay valores positivos para el gráfico de pie")
            return
            
        # Crear explode seguro
        explode = [0.05 for _ in range(len(pie_data))]
        
        # Función de autopct segura
        def safe_autopct(pct):
            try:
                val = pct * sum(pie_data) / 100.0
                return f'{pct:.1f}%\n({val:.2f})' if val > 0 else ''
            except:
                return ''
        
        # Crear el gráfico con verificación adicional
        try:
            wedges, texts, autotexts = plt.pie(
                pie_data,
                labels=pie_data.index if len(pie_data) < 15 else None,
                autopct=safe_autopct,
                explode=explode,
                startangle=90,
                pctdistance=0.8,
                labeldistance=1.1,
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
                textprops={'fontsize': 9}
            )
            
            # Ajustar textos para mejor legibilidad
            plt.setp(autotexts, size=9, weight="bold")
            plt.setp(texts, size=9)
            
            if len(pie_data) >= 15:
                plt.legend(
                    wedges,
                    [f'{idx}: {val:.2f}' for idx, val in zip(pie_data.index, pie_data)],
                    title="Categorías",
                    loc="center left",
                    bbox_to_anchor=(1, 0.5),
                    fontsize=8
                )
            
            plt.title("Gráfico de Pie Mejorado", pad=20)
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig('grafico_pie.png', bbox_inches='tight', dpi=300)
            plt.close()
        except Exception as pie_error:
            print(f"Error al generar gráfico de pie: {str(pie_error)}")
        
        # Gráfico de líneas
        df_clean.plot(kind='line')
        plt.title("Gráfico de Líneas")
        plt.tight_layout()
        plt.savefig('grafico_lineas.png')
        plt.close()
        
    except Exception as e:
        print(f"Error en generate_charts: {str(e)}")

if __name__ == "__main__":
    file_path = input("Introduce la ruta del archivo Excel: ").strip()
    process_excel(file_path)
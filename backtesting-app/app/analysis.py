import pandas as pd
import numpy as np
from datetime import datetime

def load_data(filepath):
    """Carga y prepara los datos del archivo Excel"""
    try:
        # Leer todo el archivo sin asumir encabezados
        df_raw = pd.read_excel(filepath, header=None)
        
        # Encontrar la fila con los encabezados
        header_row = None
        for i in range(min(20, len(df_raw))):
            if 'OPERACIÓN' in df_raw.iloc[i].values:
                header_row = i
                break
        
        if header_row is None:
            raise ValueError("No se encontró la fila con los encabezados")
        
        # Leer nuevamente el archivo con los encabezados correctos
        df = pd.read_excel(filepath, header=header_row)
        
        # Limpiar nombres de columnas
        df.columns = [str(col).strip() for col in df.columns]
        
        # Verificar columnas esenciales
        required_columns = ['OPERACIÓN', 'DIVISA', 'LOTAJE', 'PIPS. TP', 'PIPS SL', 'RESULTADO']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columnas requeridas no encontradas: {missing_cols}")
        
        # Filtrar solo filas con datos válidos
        df = df.dropna(subset=['OPERACIÓN', 'RESULTADO'], how='all')
        df = df[df['RESULTADO'].notna() & (df['RESULTADO'] != '')]
        
        # Limpiar y estandarizar datos
        df['RESULTADO'] = df['RESULTADO'].astype(str).str.strip().str.lower()
        df['LOTAJE'] = pd.to_numeric(df['LOTAJE'], errors='coerce').fillna(0)
        df['PIPS. TP'] = pd.to_numeric(df['PIPS. TP'], errors='coerce').fillna(0)
        df['PIPS SL'] = pd.to_numeric(df['PIPS SL'], errors='coerce').fillna(0)
        
        # Calcular RESULTADO $ si no existe
        if 'RESULTADO $' not in df.columns:
            df['RESULTADO $'] = df.apply(
                lambda row: (row['PIPS. TP'] * row['LOTAJE'] * 10) if 'take profit' in row['RESULTADO'] else
                           (row['PIPS SL'] * row['LOTAJE'] * 10 * -1) if 'stop loss' in row['RESULTADO'] else 0,
                axis=1
            )
        else:
            df['RESULTADO $'] = pd.to_numeric(
                df['RESULTADO $'].astype(str).str.replace('[^\d.-]', '', regex=True),
                errors='coerce'
            ).fillna(0)
        
        # Convertir a fecha si existe columna de fecha
        if 'FECHA' in df.columns:
            df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
        
        # Asegurar que OPERACIÓN sea única
        df['OPERACIÓN'] = df['OPERACIÓN'].astype(str) + '_' + df.index.astype(str)
        
        return df
    
    except Exception as e:
        raise ValueError(f"Error procesando archivo: {str(e)}")

def calculate_drawdown(series):
    """Calcula el drawdown de una serie de profits acumulados"""
    cumulative = series.cumsum()
    peak = cumulative.expanding(min_periods=1).max()
    drawdown = (cumulative - peak)
    return drawdown

def prepare_analysis_data(df):
    """Prepara todos los datos para análisis"""
    try:
        # Datos básicos
        df['RESULTADO_TIPO'] = np.where(df['RESULTADO $'] >= 0, 'Ganancia', 'Pérdida')
        
        # Profit acumulado y drawdown
        df_sorted = df.sort_values('OPERACIÓN')
        df_sorted['PROFIT_ACUMULADO'] = df_sorted['RESULTADO $'].cumsum()
        df_sorted['DRAWDOWN'] = calculate_drawdown(df_sorted['RESULTADO $'])
        
        # Heatmap por hora/día si hay fecha
        heatmap_data = None
        if 'FECHA' in df.columns:
            df['HORA'] = df['FECHA'].dt.hour
            df['DIA_SEMANA'] = df['FECHA'].dt.day_name()
            heatmap_data = df.pivot_table(
                index='DIA_SEMANA',
                columns='HORA',
                values='RESULTADO $',
                aggfunc='sum',
                fill_value=0
            )
        
        return {
            'distribution_data': df,
            'cumulative_data': df_sorted,
            'heatmap_data': heatmap_data
        }
    
    except Exception as e:
        print(f"Error preparando datos: {e}")
        return None

def generate_report_data(df, metrics):
    """Prepara datos para el reporte exportable"""
    try:
        # Datos resumidos
        summary = {
            'Total Operaciones': metrics['total_ops'],
            'Operaciones Ganadoras': metrics['win_ops'],
            'Operaciones Perdedoras': metrics['lose_ops'],
            'Win Rate': f"{metrics['win_rate']:.2%}",
            'Profit Total': f"${metrics['total_profit']:,.2f}",
            'Profit Factor': f"{metrics['profit_factor']:.2f}",
            'Max Drawdown': f"${metrics['max_drawdown']:,.2f}",
            'Fecha Generación': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Datos por divisa
        if 'DIVISA' in df.columns:
            by_currency = df.groupby('DIVISA').agg({
                'RESULTADO $': ['count', 'sum', 'mean'],
                'PIPS. TP': 'mean',
                'PIPS SL': 'mean'
            })
            by_currency.columns = ['Operaciones', 'Profit Total', 'Profit Promedio', 'TP Promedio', 'SL Promedio']
            by_currency = by_currency.reset_index()
        else:
            by_currency = None
        
        return {
            'summary': summary,
            'by_currency': by_currency,
            'raw_data': df
        }
    
    except Exception as e:
        print(f"Error generando reporte: {e}")
        return None
def calculate_metrics(df):
    """Calcula métricas clave de rendimiento"""
    try:
        if 'RESULTADO $' not in df.columns:
            raise ValueError("Columna RESULTADO $ no encontrada")
        
        # Calcular métricas básicas
        winning = df[df['RESULTADO $'] > 0]
        losing = df[df['RESULTADO $'] < 0]
        
        metrics = {
            'total_ops': len(df),
            'win_ops': len(winning),
            'lose_ops': len(losing),
            'win_rate': len(winning) / len(df) if len(df) > 0 else 0,
            'total_profit': df['RESULTADO $'].sum(),
            'avg_win': winning['RESULTADO $'].mean() if len(winning) > 0 else 0,
            'avg_loss': losing['RESULTADO $'].mean() if len(losing) > 0 else 0,
            'profit_factor': abs(winning['RESULTADO $'].sum() / losing['RESULTADO $'].sum()) if losing['RESULTADO $'].sum() != 0 else float('inf'),
            'max_win': df['RESULTADO $'].max(),
            'max_loss': df['RESULTADO $'].min(),
            'avg_tp': df['PIPS. TP'].mean(),
            'avg_sl': df['PIPS SL'].mean()
        }
        
        return metrics
    
    except Exception as e:
        print(f"Error calculando métricas: {e}")
        return {}

def prepare_chart_data(df):
    """Prepara datos para visualización"""
    try:
        # Datos para gráfico de distribución
        df['RESULTADO_TIPO'] = np.where(df['RESULTADO $'] >= 0, 'Ganancia', 'Pérdida')
        
        # Profit acumulado
        df_sorted = df.sort_values('OPERACIÓN')
        df_sorted['PROFIT_ACUMULADO'] = df_sorted['RESULTADO $'].cumsum()
        
        return {
            'distribution_data': df,
            'cumulative_data': df_sorted
        }
    except Exception as e:
        print(f"Error preparando datos: {e}")
        return None
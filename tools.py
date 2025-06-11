import numpy as np
import os

def cargar_matriz_npy(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    return np.load(ruta)



def construir_secuencia(ruta_signo, longitud_secuencia=30):
    secuencia = []
    for i in range(longitud_secuencia):
        ruta_matriz = os.path.join(ruta_signo, f'{i}.npy')
        if os.path.exists(ruta_matriz):
            matriz = cargar_matriz_npy(ruta_matriz)
            matriz = matriz.tolist() 
            secuencia.append(matriz)
        else:
            print(f"Advertencia: No se encontró la matriz {ruta_matriz}, se omitirá.")
    
    dict_json = {"keypoints": secuencia}
    ruta_json = os.path.join(ruta_signo, 'secuencia.json')
    with open(ruta_json, 'w') as f:
        import json
        json.dump(dict_json, f, indent=4)

    return print(f"Secuencia guardada en {ruta_json}")


# construir secuencua a parti de dtaset 
#ruta_signo = './datasets/LSC_words_Data_v2/adios/0/'
ruta_signo = './datasets/LSC_Signos_Data/R/0/'

# Ejemplo de uso
if __name__ == "__main__":
    try:
        construir_secuencia(ruta_signo)
    except Exception as e:
        print(f"Error al construir la secuencia: {e}")

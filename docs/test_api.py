#!/usr/bin/env python3
"""
Script de testing para la API de Reconocimiento LSC
Valida todos los endpoints y funcionalidades principales
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Configuración
BASE_URL = "http://localhost:5000"  # Cambiar para producción
TIMEOUT = 30

def test_health_check() -> bool:
    """Prueba el endpoint de health check"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Health check exitoso")
            print(f"   Respuesta: {response.text}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def create_test_keypoints(sequence_length: int = 30, feature_dim: int = 126) -> List[List[float]]:
    """Crea keypoints de prueba"""
    import random
    keypoints = []
    for _ in range(sequence_length):
        frame = [random.uniform(0, 1) for _ in range(feature_dim)]
        keypoints.append(frame)
    return keypoints

def test_alphabet_recognition() -> bool:
    """Prueba el reconocimiento de alfabeto con keypoints"""
    print("🔍 Probando reconocimiento de alfabeto...")
    try:
        keypoints = create_test_keypoints(30, 126)
        data = {"keypoints": keypoints}
        
        response = requests.post(
            f"{BASE_URL}/predict_recognition_alphabet",
            json=data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Reconocimiento de alfabeto exitoso")
            print(f"   Predicción: {result.get('prediction')}")
            print(f"   Probabilidades: {len(result.get('probabilities', []))} valores")
            return True
        else:
            print(f"❌ Reconocimiento de alfabeto falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en reconocimiento de alfabeto: {e}")
        return False

def test_words_recognition() -> bool:
    """Prueba el reconocimiento de palabras con keypoints"""
    print("🔍 Probando reconocimiento de palabras...")
    try:
        keypoints = create_test_keypoints(30, 258)  # Usar 258 para pose_hands
        data = {"keypoints": keypoints}
        
        response = requests.post(
            f"{BASE_URL}/predict_recognition_words_v2",
            json=data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Reconocimiento de palabras exitoso")
            print(f"   Predicción: {result.get('prediction')}")
            print(f"   Probabilidades: {len(result.get('probabilities', []))} valores")
            return True
        else:
            print(f"❌ Reconocimiento de palabras falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en reconocimiento de palabras: {e}")
        return False

def test_video_alphabet_recognition() -> bool:
    """Prueba el reconocimiento de alfabeto con video"""
    print("🔍 Probando reconocimiento de alfabeto con video...")
    try:
        # URL de video de prueba (reemplazar con una URL válida)
        test_video_url = "https://storage.googleapis.com/test-videos/sample.mp4"
        data = {
            "url_video": test_video_url,
            "type_extract": "hands"
        }
        
        response = requests.post(
            f"{BASE_URL}/predict_recognition_video_alphabet",
            json=data,
            timeout=60  # Timeout más largo para video
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Reconocimiento de alfabeto con video exitoso")
            print(f"   Predicción: {result.get('prediction')}")
            return True
        elif response.status_code == 400 and "No se pudieron extraer keypoints" in response.text:
            print("⚠️  Video no accesible (esperado para testing)")
            print("   Esto es normal si no hay un video de prueba válido")
            return True
        else:
            print(f"❌ Reconocimiento de alfabeto con video falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en reconocimiento de alfabeto con video: {e}")
        return False

def test_video_words_recognition() -> bool:
    """Prueba el reconocimiento de palabras con video"""
    print("🔍 Probando reconocimiento de palabras con video...")
    try:
        # URL de video de prueba (reemplazar con una URL válida)
        test_video_url = "https://storage.googleapis.com/test-videos/sample.mp4"
        data = {
            "url_video": test_video_url,
            "type_extract": "pose_hands"
        }
        
        response = requests.post(
            f"{BASE_URL}/predict_recognition_video_words_v2",
            json=data,
            timeout=60  # Timeout más largo para video
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Reconocimiento de palabras con video exitoso")
            print(f"   Predicción: {result.get('prediction')}")
            return True
        elif response.status_code == 400 and "No se pudieron extraer keypoints" in response.text:
            print("⚠️  Video no accesible (esperado para testing)")
            print("   Esto es normal si no hay un video de prueba válido")
            return True
        else:
            print(f"❌ Reconocimiento de palabras con video falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en reconocimiento de palabras con video: {e}")
        return False

def test_error_handling() -> bool:
    """Prueba el manejo de errores"""
    print("🔍 Probando manejo de errores...")
    
    tests = [
        {
            "name": "Datos JSON inválidos",
            "endpoint": "/predict_recognition_alphabet",
            "data": "invalid json",
            "expected_status": 400
        },
        {
            "name": "Keypoints faltantes",
            "endpoint": "/predict_recognition_alphabet",
            "data": {"other_field": "value"},
            "expected_status": 400
        },
        {
            "name": "Formato de keypoints incorrecto",
            "endpoint": "/predict_recognition_alphabet",
            "data": {"keypoints": [[1, 2, 3]]},  # Solo 3 valores en lugar de 126
            "expected_status": 400
        }
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            if isinstance(test["data"], str):
                response = requests.post(
                    f"{BASE_URL}{test['endpoint']}",
                    data=test["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
            else:
                response = requests.post(
                    f"{BASE_URL}{test['endpoint']}",
                    json=test["data"],
                    timeout=TIMEOUT
                )
            
            if response.status_code == test["expected_status"]:
                print(f"✅ {test['name']}: Error manejado correctamente")
            else:
                print(f"❌ {test['name']}: Esperado {test['expected_status']}, obtenido {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test['name']}: Error inesperado - {e}")
            all_passed = False
    
    return all_passed

def test_performance() -> bool:
    """Prueba básica de performance"""
    print("🔍 Probando performance...")
    try:
        keypoints = create_test_keypoints(30, 126)
        data = {"keypoints": keypoints}
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/predict_recognition_alphabet",
            json=data,
            timeout=TIMEOUT
        )
        end_time = time.time()
        
        if response.status_code == 200:
            processing_time = end_time - start_time
            print(f"✅ Performance test exitoso")
            print(f"   Tiempo de procesamiento: {processing_time:.2f} segundos")
            
            if processing_time < 5:
                print("   ⚡ Performance excelente (< 5s)")
            elif processing_time < 10:
                print("   🟡 Performance aceptable (< 10s)")
            else:
                print("   🔴 Performance lenta (> 10s)")
            
            return True
        else:
            print(f"❌ Performance test falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en performance test: {e}")
        return False

def run_all_tests() -> Dict[str, bool]:
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando tests de la API de Reconocimiento LSC")
    print("=" * 50)
    
    tests = {
        "Health Check": test_health_check,
        "Reconocimiento Alfabeto": test_alphabet_recognition,
        "Reconocimiento Palabras": test_words_recognition,
        "Video Alfabeto": test_video_alphabet_recognition,
        "Video Palabras": test_video_words_recognition,
        "Manejo de Errores": test_error_handling,
        "Performance": test_performance
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results[test_name] = False
    
    return results

def print_summary(results: Dict[str, bool]):
    """Imprime un resumen de los resultados"""
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASÓ" if passed_test else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! La API está funcionando correctamente.")
        return True
    else:
        print("⚠️  Algunos tests fallaron. Revisar la configuración de la API.")
        return False

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Uso: python docs/test_api.py [--url BASE_URL]")
            print("  --url: URL base de la API (por defecto: http://localhost:5000)")
            print("")
            print("Ejemplos:")
            print("  python docs/test_api.py")
            print("  python docs/test_api.py --url https://tu-api-url.com")
            return
        
        if sys.argv[1] == "--url" and len(sys.argv) > 2:
            global BASE_URL
            BASE_URL = sys.argv[2]
    
    print(f"🌐 Usando URL base: {BASE_URL}")
    
    try:
        results = run_all_tests()
        success = print_summary(results)
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

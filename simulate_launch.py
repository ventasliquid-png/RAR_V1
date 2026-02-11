import sys
from launch_protocol import main
from unittest.mock import patch

# Datos simulados para la prueba automática
simulated_inputs = [
    "GUANTES DE SEGURIDAD", # Producto
    "10",                   # Cantidad
    "par",                  # Unidad
    "30693450239",          # CUIT (Debería ser válido o usar uno real de prueba)
    "S",                    # Facturar?
    "EMITIR"                # Confirmación
]

def run_simulation():
    print("=== INICIANDO SIMULACIÓN DE PROTOCOLO ===")
    with patch('builtins.input', side_effect=simulated_inputs):
        try:
            main()
        except StopIteration:
            print("[SIMULACIÓN] Se acabaron los inputs simulados.")
        except Exception as e:
            print(f"[SIMULACIÓN] Error: {e}")

if __name__ == "__main__":
    run_simulation()

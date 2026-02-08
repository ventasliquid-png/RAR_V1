import builtins
import sys
import os

# Mocking input BEFORE importing main
# We know the prompt will ask for CUIT. We return the User's CUIT.
original_input = builtins.input

def mock_input(prompt=""):
    print(f"[MOCK INPUT] Prompt: {prompt}")
    return "20132967572"

builtins.input = mock_input

# Ahora importamos main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import main

if __name__ == "__main__":
    print("=== TEST HARVEST COMMENCING ===")
    # Aseguramos que la DB y el Reporte esten ahi (ya lo estan)
    main.inicializar_cantera()
    main.procesar_reporte()
    print("=== TEST HARVEST COMPLETE ===")

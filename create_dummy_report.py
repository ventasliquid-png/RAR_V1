
encoding = 'latin-1' # Because main.py reads with latin-1
content = '"x","x","TEST_CLI_01","CLIENTE TEST ARCA","x","x","x","PROD_ARCA_01","Producto Test Arca","x"'
with open(r'C:\dev\RAR_V1\REPORTE 2.TXT', 'w', encoding=encoding) as f:
    f.write(content)
print("Updated REPORTE 2.TXT")


import argparse, os, winreg, base64

#------------------------------------------------------------------------------------------------------------------------#

def check_sys():

    """Comprueba que el usuario que ejecuta el script tiene privilegios NT Authority\System"""

    if os.getlogin() != "SYSTEM":
        print("[*] Para ejecutar este programa necesitas privilegios NT authority\system.")
        os._exit(1)

#------------------------------------------------------------------------------------------------------------------------#

def get_controllers():

    """Obtiene las MAC de los controladores Bluetooth presentes en el equipo.
    
    Retorna mac_controllers y num_controllers que contienen:
        [*] MAC de los controladores.
        [*] Numero de controladores.
    """
    
    mac_controllers = []
    num_controllers = 0

    # Dirigirse a la clave del registro adecuada.
    REG_PATH = r'SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys'
    open_subKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,REG_PATH)

    # Obtener la cantidad y MAC de los controladores disponibles.
    i = 0
    while True:
        try:
            x = winreg.EnumKey(open_subKey,i)
            mac_controllers.append(x)
            num_controllers += 1
            i += 1
        except:
            break
    
    # Cerrar la clave del registro.
    winreg.CloseKey(open_subKey)

    if num_controllers != 0:
        return mac_controllers, num_controllers
    else:
        print("[*] No se han encontrado controladores Bluetooth o BLE configurados en este equipo.")
        os._exit(1)

#------------------------------------------------------------------------------------------------------------------------#

def get_devices():

    """Obtiene los dispositivos BLE emparejados.
    
    Retorna mac_devices y num_devices que contienen:
        [*] MAC dispositivos BLE emparejados.
        [*] Numero de dispositvos.
    """
    mac_controllers, num_controller = get_controllers()
    mac_devices = {}
    num_devices = 0

    for a in mac_controllers:

        z = [] 

        # Dirigirse a la clave del registro adecuada.
        REG_PATH = r'SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys\\' + a
        open_subKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,REG_PATH)

        # Obtener la cantidad y MAC de lso dispositivos emparejados.
        i = 0
        while True:
            try:
                x = winreg.EnumKey(open_subKey,i)
                z.append(x)
                i += 1
                num_devices += 1
            except:
                if num_devices == 0:
                    print("[*] No se han encontrado dispositvos BLE emparejados en este equipo.")
                    if num_controller > 1:
                        print("\t[-] Solo se ha obtenido que existen los siguientes controladores configurados y tienen las siguientes MAC -->",mac_controllers)
                    else:
                        print("\t[-] Solo se ha obtenido que existe un controlador configurado y tiene la siguiente MAC -->", mac_controllers)
                    os._exit(0)
                break
        
        # Almaceno la informacion en el diccionario.
        mac_devices.update({a:z})

        # Cierro la clave del registro.
        winreg.CloseKey(open_subKey)
      
    return mac_devices, num_devices

#------------------------------------------------------------------------------------------------------------------------#

def get_parameters_devices():

    """Obtiene los parametros de los dispositivos emparejados.
    
    Retorna info_devices con una matriz ue contiene:
        [*] MAC Controlador ue maneja el dispositvo.
            - LEName --> Nombre del dispositivo BLE.
            - MAC --> Identificador del dispositivo.
            - Services --> Servicios asociados al dispositivo.
            - Parametros de identificacion del dispositivo --> Vendor, Product, Version, Appearance.
    """
    mac_controllers, num_controllers = get_controllers()
    mac_devices, num_devices = get_devices()
    info_devices = {}

    # Almacenar informacion de los dispositivos BLE.
    for a in mac_controllers:
        z = []
        for b in range(len(mac_devices[a])):

            REG_PATH = r'SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Devices\\' + mac_devices[a][b]                
            open_subKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,REG_PATH)

            # Guardar la MAC del dispositivo BLE.
            z.append({'MAC':(mac_devices[a][b]).upper(),'LEName':'','Vendor':'', 'Product':'','Version':'','Appearance':'','Services':''})
                                
            # Guardar el nombre del dispositivo BLE.
            x = winreg.QueryValueEx(open_subKey, 'LEName')
            z[b]['LEName'] = x[0].decode(encoding='ascii',errors='strict').rstrip('\x00')

            # Guardar el Vendor del dispositivo BLE.
            x = winreg.QueryValueEx(open_subKey, 'VID')
            z[b]['Vendor'] = x[0]

            # Guardar el product del dispositivo BLE.
            x = winreg.QueryValueEx(open_subKey, 'PID')
            z[b]['Product'] = x[0]

            # Guardar la Version del dispositivo BLE.
            x = winreg.QueryValueEx(open_subKey, 'Version')
            z[b]['Version'] = x[0]

            # Guardar el Appearance del dispositivo BLE.
            x = winreg.QueryValueEx(open_subKey, 'LEAppearance')
            z[b]['Appearance'] = hex(x[0])

            # Cierro la clave del registro.
            winreg.CloseKey(open_subKey)

            # Guardar los servicios del dispositivo BLE.
            REG_PATH = r'SYSTEM\\CurrentControlSet\\Enum\\BTHLEDevice'
            open_subKey1 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,REG_PATH)

            i = 0
            services = []
            while True:
                try:
                    x = winreg.EnumKey(open_subKey1,i)
                    if mac_devices[a][b] in x:
                        y = x.split('_')
                        services.append((y[0].replace('{',"").replace('}',";")))
                    i += 1
                except:
                    break

            for c in services:
                z[b]['Services'] += str(c)
                    
            # Cierro la clave del registro.
            winreg.CloseKey(open_subKey1)

        info_devices.update({a:z})
                    
    return info_devices      
    
#------------------------------------------------------------------------------------------------------------------------#

def get_keys():

    """Obtiene los siguientes secretos de emparejamiento -> LTK, EDIV, ERand, KeyLenght"""

    mac_controllers, num_controllers = get_controllers()
    mac_devices, num_devices = get_devices()
    keys_devices = {}

    # Almacenar las claves de los dispositivos BLE.
    for a in mac_controllers:
        z = []
        for b in range(len(mac_devices[a])):

            REG_PATH = r'SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys\\' + a + '\\' + mac_devices[a][b]                
            open_subKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,REG_PATH)

            # Guardar la MAC de dispositivo BLE.
            z.append({'MAC':(mac_devices[a][b]).upper(),'LTK':'','EDIV':'', 'Erand':'','KeyLenght':''})

            # Guardar la LTK.                        
            x = winreg.QueryValueEx(open_subKey, 'LTK')
            z[b]['LTK'] = x[0].hex().upper()

            # Guardar el EDIV. 
            x = winreg.QueryValueEx(open_subKey, 'EDIV')
            z[b]['EDIV'] = x[0]

            # Guardar el Erand.
            x = winreg.QueryValueEx(open_subKey, 'Erand')
            z[b]['Erand'] = x[0]

            # Guardar el KeyLenght.
            x = winreg.QueryValueEx(open_subKey, 'KeyLength')
            z[b]['KeyLenght'] = x[0]

            # Cierro la clave del registro.
            winreg.CloseKey(open_subKey)

        keys_devices.update({a:z})

    return keys_devices

#------------------------------------------------------------------------------------------------------------------------#

def linuxCommand():
    
    """Compone un comando de Bash que crea la estructura de directorios y el archivo info con la configuracion del dispositivo BLE"""

    mac_controllers, num_controller = get_controllers()
    mac_devices, num_devices = get_devices()
    keys_devices = get_keys()
    info_devices = get_parameters_devices()

    if num_devices > 1:
        print("\n[*] Estos son los comandos que tienes que ejecutar en tu sistema para crear la estructura de directorios y el fichero \"info\" de cada dispositivo BLE.")
        print("\n---------------------------------------------------------------------------------------------------------------")
    else:
        print("\n[*] Este es el comando que se tienes que ejecutar en tu sistema para crear la estructura de directorios y el fichero \"info\" del dispositivo BLE.")
        print("\n---------------------------------------------------------------------------------------------------------------")
    for a in mac_controllers:
        for b in range(len(mac_devices[a])):
            command = 'mkdir -p /var/lib/bluetooth/' + (a[0:2] + ":" + a[2:4] + ":" + a[4:6] + ":" + a[6:8] + ":" + a[8:10] + ":" + a[10:12]).upper() + "/" + (mac_devices[a][b][0:2] + ":" + mac_devices[a][b][2:4] + ":" + mac_devices[a][b][4:6] + ":" + mac_devices[a][b][6:8] + ":" + mac_devices[a][b][8:10] + ":" + mac_devices[a][b][10:12]).upper() + "/" + "; echo -e \'[General]\\nName=" + info_devices[a][b]['LEName'] + "\\nAppearance=" + str(info_devices[a][b]['Appearance']) + "\\nAddressType=static\\nSupportedTechnologies=LE\\nTrusted=false\\nBlocked=false\\nWakeAllowed=true\\nServices=" + str(info_devices[a][b]['Services']) + "\\n\\n[LongTermKey]\\nKey=" + str(keys_devices[a][b]['LTK']) + "\\nAuthenticated=0\\nEncSize=" + str(keys_devices[a][b]['KeyLenght']) + "\\nEDiv=" + str(keys_devices[a][b]['EDIV']) + "\\nRand=" + str(keys_devices[a][b]['Erand']) + "\\n\\n[DeviceID]\\nSource=2\\nVendor=" + str(info_devices[a][b]['Vendor']) + "\\nProduct=" + str(info_devices[a][b]['Product']) + "\\nVersion=" + str(info_devices[a][b]['Version']) + "\' > /var/lib/bluetooth/" + (a[0:2] + ":" + a[2:4] + ":" + a[4:6] + ":" + a[6:8] + ":" + a[8:10] + ":" + a[10:12]).upper() + "/" + (mac_devices[a][b][0:2] + ":" + mac_devices[a][b][2:4] + ":" + mac_devices[a][b][4:6] + ":" + mac_devices[a][b][6:8] + ":" + mac_devices[a][b][8:10] + ":" + mac_devices[a][b][10:12]).upper() + "/info"
            print("\n[+] Este comando corresponde al dispositivo con MAC", (mac_devices[a][b][0:2] + ":" + mac_devices[a][b][2:4] + ":" + mac_devices[a][b][4:6] + ":" + mac_devices[a][b][6:8] + ":" + mac_devices[a][b][8:10] + ":" + mac_devices[a][b][10:12]).upper() , "(" + info_devices[a][b]['LEName'] + ")", "del controlador", (a[0:2] + ":" + a[2:4] + ":" + a[4:6] + ":" + a[6:8] + ":" + a[8:10] + ":" + a[10:12]).upper() + ".")
            commandBase64 = "echo \'" + str(base64.b64encode(command.encode()), 'UTF-8') + "\' | base64 -d | bash"
            print("\n" + commandBase64)
            print("\n---------------------------------------------------------------------------------------------------------------")

#------------------------------------------------------------------------------------------------------------------------#

def outputInfo():
    """Crea un archivo llamado info con la configuracion del dispositivo BLE"""
    
    mac_controllers, num_controller = get_controllers()
    mac_devices, num_devices = get_devices()
    keys_devices = get_keys()
    info_devices = get_parameters_devices()

    try:
        for a in mac_controllers:
            for b in range(len(mac_devices[a])):
                file = open("info_" + (str(mac_devices[a][b])), "w")
                file.write("[General]\nName=" + info_devices[a][b]['LEName'] + "\nAppearance=" + str(info_devices[a][b]['Appearance']) + "\nAddressType=static\nSupportedTechnologies=LE\nTrusted=false\nBlocked=false\nWakeAllowed=true\nServices=" + str(info_devices[a][b]['Services']) + "\n\n[LongTermKey]\nKey=" + str(keys_devices[a][b]['LTK']) + "\nAuthenticated=0\nEncSize=" + str(keys_devices[a][b]['KeyLenght']) + "\nEDiv=" + str(keys_devices[a][b]['EDIV']) + "\nRand=" + str(keys_devices[a][b]['Erand']) + "\n\n[DeviceID]\nSource=2\nVendor=" + str(info_devices[a][b]['Vendor']) + "\nProduct=" + str(info_devices[a][b]['Product']) + "\nVersion=" + str(info_devices[a][b]['Version']))
        file.close()
        print("\n[*] Se ha podido crear correctamente el fichero info en el directorio actual donde te encuentras.\n")
        os.system("dir /b /s info_*")
        os._exit(0)
    except:
        print("\n[*] No se ha podido crear correctamente el fichero info en el directorio actual dode te encuentras. Comprueba que dispones de permisos de escritura en este directorio.\n")
        os._exit(1)


    
#------------------------------------------------------------------------------------------------------------------------#

def displayInfo():

    """Muestra la informacion obtenida por pantalla de los dispositivos BLE"""

    mac_controllers, num_controller = get_controllers()
    mac_devices, num_devices = get_devices()
    keys_devices = get_keys()
    info_devices = get_parameters_devices()

    print("\n[*] La informacion que se ha obtenido de los dispositivos emparejados es la siguiente:\n")
    print("===============================================================================================================")

    for a in mac_controllers:
        for b in range(len(mac_devices[a])):    
            print("\n[+] Nombre del dispositivo:", info_devices[a][b]['LEName'], "| Controlador que lo maneja:", (a[0:2] + ":" + a[2:4] + ":" + a[4:6] + ":" + a[6:8] + ":" + a[8:10] + ":" + a[10:12]).upper())
            print("\t[*] Parametros del dispositivo:")
            print("\t\t- Direccion MAC del dispositivo:", info_devices[a][b]['MAC'].upper())
            print("\t\t- Servicios que ofrece dispone:", info_devices[a][b]['Services'])
            print("\t\t- Informacion que identifica al dispositivo -> Vendor:", info_devices[a][b]['Vendor'], "| Product:", info_devices[a][b]['Product'], "| Version:", info_devices[a][b]['Version'])
            print("\n\t[*] Clave de emparejamiento y valores adicionales:")
            print("\t\t- Key:", keys_devices[a][b]['LTK'])
            print("\t\t- EDIV:", keys_devices[a][b]['EDIV'])
            print("\t\t- Erand:", keys_devices[a][b]['Erand'])
            print("\t\t- KeyLenght:", keys_devices[a][b]['KeyLenght'], "\n")
            if b == 0:
                print("---------------------------------------------------------------------------------------------------------------")


        print("===============================================================================================================")
            

#------------------------------------------------------------------------------------------------------------------------#

def arguments():
    parser = argparse.ArgumentParser()

    # Argumentos de la herramienta.
    parser.add_argument("-oi", "--outputInfo", help="Escribe el fichero info (Fichero con la informacion del dispositivo) en el directorio actual desde donde se ejecuta el binario.", action="store_true")
    parser.add_argument("-ob", "--outputBase64", help="Muestra el comando bash que se tiene que ejecutar con la informacion codificada en Base64, para crear automaticamente el fichero info con sus carpetas, en tu equipo Linux.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Muestra la informacion obtenida por pantalla, mas \"outputBase64\".", action="store_true")

    args = parser.parse_args()

    # Acciones que realizan los argumentos.
    if args.outputBase64:
        linuxCommand()
        os._exit(0)
    if args.verbose:
        displayInfo()
        linuxCommand()
        os._exit(0)
    if args.outputInfo:
        outputInfo()
        os._exit(0)
    if not args.outputInfo and not args.verbose and not args.outputBase64:
            print("""
__________.__       ___________           .__   
\______   \  |   ___\__    ___/___   ____ |  |  
 |    |  _/  | _/ __ \|    | /  _ \ /  _ \|  |  
 |    |   \  |_\  ___/|    |(  <_> |  <_> )  |__
 |______  /____/\___  >____| \____/ \____/|____/
        \/          \/                          

Esta es una herramienta que sustrae la informacion de los dispositivos BLE del registro de Windows. 
Utiliza --help para ver las opciones.

            """)
    os._exit(0)

#------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    #check_sys()
    #arguments()
    keys_devices = get_keys()
    print("\ninfo_devices ->", keys_devices)
   
    
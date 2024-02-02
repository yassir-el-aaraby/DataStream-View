import paho.mqtt.client as mqtt
import json
import pandas as pd
import yaml
import os
import threading
import openpyxl
from display_manager import  DisplayManager
from filter_objects import FilterObjects

# Supprimer le fichier mqtt_data.xlsx s'il existe
if os.path.exists("mqtt_data.xlsx"):
    os.remove("mqtt_data.xlsx")

# Supprimer le fichier mqtt_messages_realtime.json s'il existe
if os.path.exists("mqtt_messages_realtime.json"):
    os.remove("mqtt_messages_realtime.json")

# Variables pour les fichiers de temps réel et historique
realtime_file = "mqtt_messages_realtime.json"
historic_file = "mqtt_messages_historic.json"

# Fonction pour lire la configuration MQTT à partir d'un fichier YAML
def read_mqtt_config(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r') as file:
        return yaml.safe_load(file)

# Fonction pour lire le mappage des noms à partir d'un fichier YAML
def read_name_mappings(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r') as file:
        return yaml.safe_load(file)

# Mappages des noms
name_mappings = read_name_mappings("./data/name_mappings.yaml")

# Fonction pour se connecter au broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

# Fonction pour traiter les messages en temps réel
def process_realtime_messages(client, userdata, message):
    # Convertir le message en JSON
    msg = json.loads(message.payload)

    # Vérifier si le champ "msg" est égal à "alive"
    if msg.get("msg") == "alive":
        # Créer un nouveau message contenant uniquement "msg": "alive"
        alive_msg = {"msg": "alive", "gmac": msg.get("gmac")}  # Ajouter "gmac"
        # color change
        DisplayManager.change_color(msg.get('gmac'), "alive")
        gmac = msg.get("gmac", "Unknown")  # Obtenez le "gmac" ou définissez-le sur "Unknown" si absent
        gname = name_mappings["gmac"].get(gmac, "Unknown")  # Obtenez le "gname" à partir du fichier name_mappings.yaml

        # Afficher les données
        print("gmac:", gmac)
        print("gname:", gname)
        print("-" * 40)  # Séparateur pour les messages

        # Sauvegarder le message "alive" dans le fichier de temps réel
        with open(realtime_file, "a") as file:
            file.write(json.dumps(alive_msg) + "\n")
    else:
        # Le message n'est pas "alive", donc nous continuons avec le traitement normal
        # Ajouter "gmac" à chaque objet "obj"
        gmac = msg.get("gmac", "Unknown")  # Obtenez le "gmac" ou définissez-le sur "Unknown" si absent
        # color change
        DisplayManager.change_color(msg.get('gmac'), "advData")
        gname = name_mappings["gmac"].get(gmac, "Unknown")  # Obtenez le "gname" à partir du fichier name_mappings.yaml
        
        for obj in msg.get("obj", []):
            if obj["type"] == 4:
                obj["gmac"] = gmac  # Ajouter le "gmac" à chaque objet
                obj["gname"] = gname  # Ajouter le "gname" à chaque objet
                dmac = obj.get("dmac", "")
                obj["dname"] = name_mappings["dmac"].get(dmac, dmac)
                # filter objects and then store them
                FilterObjects.filter_and_store(obj)
        # update tables with filtered data
        DisplayManager.update_tables_data()

        # Sauvegarder le message brut dans le fichier de temps réel
        with open(realtime_file, "a") as file:
            file.write(json.dumps(msg) + "\n")
        # Vous pouvez ajouter ici d'autres opérations spécifiques aux messages en temps réel si nécessaire


# Fonction pour traiter les messages historiques
def process_historic_messages(client, userdata, message):
    # Convertir le message en JSON
    msg = json.loads(message.payload)

    # Vérifier si le champ "msg" est égal à "advData"
    if msg.get("msg") == "advData":
        # Récupérer le "gmac" du message principal
        gmac = msg["gmac"]
        
        # Cloner chaque objet individuel dans la liste "obj"
        cloned_objs = []
        for obj in msg["obj"]:
            cloned_obj = obj.copy()  # Cloner l'objet
            cloned_obj["gmac"] = gmac  # Ajouter le "gmac"
            cloned_objs.append(cloned_obj)  # Ajouter l'objet cloné à la liste
        
        # Mettre à jour la liste "obj" du message cloné avec les objets clonés
        msg["obj"] = cloned_objs

        # Ajouter gmac, gname, dmac, dname à chaque sous-objet dans obj et sauvegarder dans Excel
        save_to_excel(msg)
    else:
        # Si le champ "msg" n'est pas "advData", vous pouvez choisir de ne rien faire ou d'attendre le prochain message du topic.
        pass


# Fonction pour ajouter gmac, gname, dmac, dname et sauvegarder dans Excel
def save_to_excel(msg):
    gmac = msg["gmac"]
    gname = name_mappings["gmac"].get(gmac, "Unknown")
    
    for obj in msg["obj"]:
        obj["gmac"] = gmac
        obj["gname"] = gname
        dmac = obj.get("dmac", "")
        obj["dname"] = name_mappings["dmac"].get(dmac, "Unknown")
    
    # Charger le fichier Excel existant ou créer un nouveau fichier
    try:
        wb = openpyxl.load_workbook("mqtt_data.xlsx")
        ws = wb.active
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['gmac', 'gname', 'dmac', 'dname'] + [col for col in msg["obj"][0].keys() if col not in ['gmac', 'gname', 'dmac', 'dname']])
    
    # Ajouter les données au fichier Excel sans effacer les données précédentes
    for obj in msg["obj"]:
        row_data = [obj["gmac"], obj["gname"], obj["dmac"], obj["dname"]] + [obj[col] for col in msg["obj"][0].keys() if col not in ['gmac', 'gname', 'dmac', 'dname']]
        ws.append(row_data)
    
    # Sauvegarder le fichier Excel
    wb.save("mqtt_data.xlsx")


# Lecture de la configuration MQTT à partir du fichier YAML
config = read_mqtt_config("./data/mqtt_config.yaml")

# Créer et configurer le client MQTT pour les messages en temps réel
realtime_client = mqtt.Client()
realtime_client.on_connect = on_connect
realtime_client.on_message = process_realtime_messages

# Créer et configurer le client MQTT pour les messages historiques
historic_client = mqtt.Client()
historic_client.on_connect = on_connect
historic_client.on_message = process_historic_messages

# Connexion aux brokers MQTT pour les deux clients
realtime_client.username_pw_set(username=config['username'], password=config['password'])
realtime_client.connect(config['host'], config['port'], 60)
historic_client.username_pw_set(username=config['username'], password=config['password'])
historic_client.connect(config['host'], config['port'], 60)

# Abonnement aux topics MQTT pour les deux clients
realtime_client.subscribe(config['realtime_topic'])
historic_client.subscribe(config['historic_topic'])

# Démarrer la boucle pour les deux clients en parallèle
realtime_thread = threading.Thread(target=realtime_client.loop_forever)
historic_thread = threading.Thread(target=historic_client.loop_forever)

realtime_thread.start()
historic_thread.start()

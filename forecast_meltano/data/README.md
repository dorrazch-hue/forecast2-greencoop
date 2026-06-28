\# Données sources — forecast\_meltano/data/



Ce dossier contient les fichiers de données historiques à fournir manuellement.

Ces fichiers ne sont pas versionnés car volumineux ou fournis par l'équipe.



\## Fichiers requis



\### Weather Underground (fichiers Excel)

\- Weather\_Underground\_La\_Madeleine\_FR.xlsx (station ILAMAD25, jan-jul 2024)

\- Weather\_Underground\_Ichtegem\_BE.xlsx (station IICHTE19, jan-jul 2024)

Utilisés par : load\_weather\_underground.py



\### InfoClimat historique (fichier JSON)

\- data\_source\_infoclimat.json (stations Bergues, Hazebrouck, Armentières, Lille-Lesquin, oct 2024)

Utilisé par : load\_infoclimat\_json.py



\## Comment obtenir ces fichiers

\- Fichiers Excel WU : fournis par l'équipe Data Science (Ouly)

\- Fichier JSON InfoClimat : export depuis l'API InfoClimat sur la période souhaitée


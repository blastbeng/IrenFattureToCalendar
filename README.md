# IrenFattureToCalendar

  Python App per scaricare dal sito IREN le fatture delle bollette non pagate e inserirle su google calendar

  L'app scarica le bollette ogni 48 ore, parametro configurabile dal file .env

  Sono disponibili due endpoint per la login e per scaricare le bollette manualmente sotto:
  http://localhost:5085



**Init**

  Per prima cosa è necessario il file .env (copia il file .env.example e modificalo)

  Successivamente è necessario creare un progetto su https://console.cloud.google.com 
  con relative chiavi OAuth https://console.cloud.google.com/apis/credentials/oauthclient  
  Una volta create le chiavi OAuth possono essere scaricate e inserite all'interno di ./config/credentials.json

  Ora è possibile autorizzare le credenziali appena scaricate mediante ./authorize_credentials.sh



**Avvio in locale**

  lancia ./launch.sh

**Avvio con Docker**

  lancia ./build.sh per generare l'immagine docker e utilizza docker-compose up -d per avviare il progetto.

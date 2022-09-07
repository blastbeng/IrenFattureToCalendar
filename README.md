# IrenFattureToCalendar
Applicazione python per scaricare le fatture delle bollette non pagate e inserirle su google calendar (WORK IN PROGRESS)



*Init*

Per prima cosa devi creare il file .env (copia il file .env.example e modificalo)
Successivamente è necessario generare le credentials oauth e inserirle all'interno di ./config/credentials.json
Ora è possibile autorizzare le credenziali mediante ./authorize_credentials.sh

*Compile*

lancia ./build.sh per generare l'immagine docker

*Launch*
docker-compose up -d

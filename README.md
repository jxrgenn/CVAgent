To run this, the n8n workflow must be started.
Then you need to run the frontend and its backend (flaskBackend.py); 
run both python scripts and forward their ports to public urls using localtunnel and ngrok.

--also tunnel the 5002 port from flaskBackend to a public url via localtunnel

alternatively, you can just go inside cv-frontend and run 
"npm run start-all"
"npm run start-tunnels"

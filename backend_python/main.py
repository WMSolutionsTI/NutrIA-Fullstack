from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Na configuração do FastAPI/Uvicorn
app = FastAPI()

# Limite de 50MB para requests (alinhado com nginx client_max_body_size)
# Configurado no Nginx (mais eficiente — rejeita antes de chegar ao Python)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nutriapro.com.br",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"]
)

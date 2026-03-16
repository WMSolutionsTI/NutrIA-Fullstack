from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.database import get_db

router = APIRouter()

@router.post("/prompts/criar")
def criar_prompt(funcao: str, contexto: str, texto: str, tenant_id: int = None, caixa_id: int = None, db: Session = Depends(get_db)):
    prompt = Prompt(
        funcao=funcao,
        contexto=contexto,
        texto=texto,
        tenant_id=tenant_id,
        caixa_id=caixa_id
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt

@router.get("/prompts/{funcao}")
def consultar_prompts(funcao: str, db: Session = Depends(get_db)):
    prompts = db.query(Prompt).filter(Prompt.funcao == funcao, Prompt.ativo == 1).all()
    return prompts

@router.put("/prompts/{prompt_id}/atualizar")
def atualizar_prompt(prompt_id: int, texto: str, contexto: str = None, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    prompt.texto = texto
    if contexto:
        prompt.contexto = contexto
    db.commit()
    db.refresh(prompt)
    return prompt

@router.put("/prompts/{prompt_id}/desativar")
def desativar_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    prompt.ativo = 0
    db.commit()
    db.refresh(prompt)
    return prompt
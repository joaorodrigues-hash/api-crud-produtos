from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional

class ProdutoCreate(BaseModel):
    nome:     str
    codigo:   str
    valor:    float
    excluido: bool = False
    imagem:   Optional[str] = None

    # veificacao do campo NOME
    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError("O nome do produto não pode ser vazio.")
        return v.strip()

    # verificacao do campo CODIGO
    @field_validator("codigo")
    @classmethod
    def codigo_nao_pode_ser_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError("O código do produto não pode ser vazio.")
        return v.strip()

    # verificacao do campo VALOR
    @field_validator("valor")
    @classmethod
    def valor_deve_ser_positivo(cls, v):
        if v <= 0:
            raise ValueError("O valor do produto deve ser maior que zero.")
        return v


class ProdutoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    nome:           str
    codigo:         str
    valor:          float
    excluido:       bool
    imagem:         Optional[str]

import json
import logging
import hashlib
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict
import sys
from inspect import currentframe, getframeinfo

# ============================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

for log_type in ["errors"]:
    (LOGS_DIR / log_type).mkdir(exist_ok=True)


# ============================================================================
# CLASSE CUSTOMIZADA DE ERRO
# ============================================================================


class AppError(Exception):
    def __init__(
        self,
        mensagem: str,
        contexto: str = "unknown",
        dados_adicionais: Optional[Dict[str, Any]] = None,
        nivel: str = "ERROR",
    ):
        self.mensagem = mensagem
        self.contexto = contexto
        self.dados_adicionais = dados_adicionais or {}
        self.nivel = nivel.upper()
        super().__init__(self.mensagem)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================


def _obter_contexto_da_pilha() -> str:
    try:
        frame = currentframe()
        if frame is None:
            return "unknown"

        # Pular frames do próprio logger
        while frame:
            filename = frame.f_code.co_filename
            if "logger.py" not in filename:
                func_name = frame.f_code.co_name
                module_name = Path(filename).stem
                return f"{module_name}.{func_name}"
            frame = frame.f_back

        return "unknown"
    except Exception:
        return "unknown"


def _gerar_hash(dados: str) -> str:
    return hashlib.sha256(dados.encode()).hexdigest()[:8]


def _coletar_informacoes_sistema() -> Dict[str, Any]:
    try:
        import platform

        return {
            "sistema_operacional": platform.system(),
            "versao_python": platform.python_version(),
            "plataforma": platform.platform(),
        }
    except Exception:
        return {}


def _extrair_stack_trace() -> str:
    return traceback.format_exc()


# ============================================================================
# FUNÇÃO PRINCIPAL DE LOGGING
# ============================================================================


def _salvar_log(
    mensagem: str,
    contexto: str,
    nivel: str,
    dados_adicionais: Optional[Dict[str, Any]] = None,
    stack_trace: Optional[str] = None,
) -> str:
    nivel = nivel.upper()
    nivel_map = {"ERROR": "errors", "WARNING": "warnings", "INFO": "info"}
    subdir = nivel_map.get(nivel, "info")

    # Gerar dados para o arquivo
    agora = datetime.now()
    data_hora_str = agora.strftime("%Y-%m-%d_%H-%M-%S-%f")

    # Gerar hash baseado em: contexto + mensagem + timestamp
    dados_para_hash = f"{contexto}_{mensagem}_{agora.isoformat()}"
    hash_unico = _gerar_hash(dados_para_hash)

    # Nome do arquivo: contexto_data_hora_hash.json
    nome_arquivo = f"{contexto}_{data_hora_str}_{hash_unico}.json"
    caminho_arquivo = LOGS_DIR / subdir / nome_arquivo

    # Preparar conteúdo do log
    log_data = {
        "timestamp": agora.isoformat(),
        "data": agora.strftime("%Y-%m-%d"),
        "hora": agora.strftime("%H:%M:%S"),
        "nivel": nivel,
        "contexto": contexto,
        "mensagem": mensagem,
        "hash": hash_unico,
        "dados_adicionais": dados_adicionais or {},
        "informacoes_sistema": _coletar_informacoes_sistema(),
        "stack_trace": stack_trace,
    }

    try:
        # Salvar como JSON
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        return str(caminho_arquivo)

    except Exception as e:
        # Fallback: se não conseguir salvar como JSON, tenta salvar como texto
        try:
            caminho_fallback = caminho_arquivo.with_suffix(".txt")
            with open(caminho_fallback, "w", encoding="utf-8") as f:
                f.write(f"TIMESTAMP: {agora.isoformat()}\n")
                f.write(f"NÍVEL: {nivel}\n")
                f.write(f"CONTEXTO: {contexto}\n")
                f.write(f"HASH: {hash_unico}\n")
                f.write(f"MENSAGEM: {mensagem}\n")
                if dados_adicionais:
                    f.write(
                        f"DADOS:\n{json.dumps(dados_adicionais, indent=2, ensure_ascii=False)}\n"
                    )
                if stack_trace:
                    f.write(f"STACK TRACE:\n{stack_trace}\n")
            return str(caminho_fallback)
        except Exception as e_fallback:
            print(f"ERRO CRÍTICO ao salvar log: {e_fallback}")
            return ""


# ============================================================================
# FUNÇÕES PÚBLICAS DE LOGGING
# ============================================================================


def log_error(
    mensagem: str,
    contexto: Optional[str] = None,
    dados_adicionais: Optional[Dict[str, Any]] = None,
    include_stack_trace: bool = True,
) -> str:
    contexto = contexto or _obter_contexto_da_pilha()
    stack_trace = _extrair_stack_trace() if include_stack_trace else None

    return _salvar_log(
        mensagem=mensagem,
        contexto=contexto,
        nivel="ERROR",
        dados_adicionais=dados_adicionais,
        stack_trace=stack_trace,
    )


# ============================================================================
# WRAPPER PARA TRATAMENTO DE ERROS
# ============================================================================


def registrar_erro_com_contexto(
    contexto: str,
    mensagem: str = None,
    dados_adicionais: Optional[Dict[str, Any]] = None,
) -> callable:
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                msg = mensagem or f"Erro em {func.__name__}"
                log_error(
                    mensagem=f"{msg}: {str(e)}",
                    contexto=contexto,
                    dados_adicionais=dados_adicionais,
                )
                raise

        return wrapper

    return decorator

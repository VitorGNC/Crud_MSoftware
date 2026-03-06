"""
Utilitário para armazenamento em RAM (cache).
Demonstra que o sistema utiliza memória além da persistência em BD.
"""
from typing import Dict, List, Optional
from app.models.usuario import UsuarioORM


class CacheRAM:
    """
    Cache simples em memória RAM para armazenar usuários.
    Complementa a persistência em SQLite.
    """
    
    # Armazenamento em RAM (variável de classe compartilhada)
    _usuarios: Dict[int, UsuarioORM] = {}
    _inicializado: bool = False
    
    @classmethod
    def inicializar(cls, usuarios: List[UsuarioORM]) -> None:
        """Carrega usuários do BD para RAM na inicialização."""
        if not cls._inicializado:
            for usuario in usuarios:
                cls._usuarios[usuario.id] = usuario
            print(f"[CacheRAM] Inicializado com {len(usuarios)} usuários.")
            cls._inicializado = True
    
    @classmethod
    def adicionar(cls, usuario: UsuarioORM) -> None:
        """Adiciona um usuário ao cache."""
        cls._usuarios[usuario.id] = usuario
    
    @classmethod
    def atualizar(cls, usuario: UsuarioORM) -> None:
        """Atualiza um usuário no cache."""
        cls._usuarios[usuario.id] = usuario
    
    @classmethod
    def remover(cls, usuario_id: int) -> None:
        """Remove um usuário do cache."""
        if usuario_id in cls._usuarios:
            del cls._usuarios[usuario_id]
    
    @classmethod
    def buscar(cls, usuario_id: int) -> Optional[UsuarioORM]:
        """Busca um usuário no cache."""
        return cls._usuarios.get(usuario_id)
    
    @classmethod
    def listar_todos(cls, somente_ativos: bool = True) -> List[UsuarioORM]:
        """Lista usuários do cache."""
        if somente_ativos:
            return [u for u in cls._usuarios.values() if u.ativo]
        return list(cls._usuarios.values())
    
    @classmethod
    def obter_estatisticas(cls, total_bd: int) -> dict:
        """Retorna estatísticas do cache (demonstração)."""
        total_cache = len(cls._usuarios)
        ativos_cache = len([u for u in cls._usuarios.values() if u.ativo])
        
        return {
            "cache_ram": {
                "total": total_cache,
                "ativos": ativos_cache,
                "inativos": total_cache - ativos_cache,
            },
            "banco_dados": {
                "total": total_bd,
            },
            "sincronizado": total_cache == total_bd,
        }

usuarios = {}  # Dicionário na RAM

def Criar_Usuario(list_usuarios, nome: str, senha: str, email: str, idade: int, id: int):
    dic_usuario = {
        "nome": nome,
        "senha": senha,
        "email": email,
        "idade": idade,
        "id": id
    }
    list_usuarios[id] = dic_usuario
    return dic_usuario

def Deletar_Usuario(list_usuarios, id: int):
    if id in list_usuarios:
        del list_usuarios[id]
        return True
    return False

def Listar_Usuario(list_usuarios):
    return list_usuarios

def Alterar_Usuario(list_usuarios, id: int, nome=None, senha=None, email=None, idade=None):
    if id not in list_usuarios:
        return False

    if nome is not None:
        list_usuarios[id]["nome"] = nome
    if senha is not None:
        list_usuarios[id]["senha"] = senha
    if email is not None:
        list_usuarios[id]["email"] = email
    if idade is not None:
        list_usuarios[id]["idade"] = idade

    return True

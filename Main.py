import CRUD as cr

usuarios = {}

cr.Criar_Usuario(usuarios, "Vitor", "123", "vitor@email", 20, 1)
cr.Criar_Usuario(usuarios, "Maria", "abc", "maria@email", 25, 2)

print(cr.Listar_Usuario(usuarios))

cr.Alterar_Usuario(usuarios, 1, nome="Vitor Cavalcante")

print(cr.Listar_Usuario(usuarios))

cr.Deletar_Usuario(usuarios, 2)

print(cr.Listar_Usuario(usuarios))

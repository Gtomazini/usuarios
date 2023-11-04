"""
Módulo Usuários
"""
from flask import Blueprint
import locale
from dict_helper import dict_helper_list, dict_helper_obj
from seguranca.autenticacao import Auth
from usuario import Usuario
from flask import request, jsonify, make_response

locale.setlocale( locale.LC_ALL,'pt_BR.UTF-8' )

usersRoute = Blueprint('usersRoute', __name__)

# Recupera todos os Usuários Cadastrados no Banco de Dados
@usersRoute.route('/api/usuarios', methods=['GET'])
@Auth.token_required
def get_usuarios(usuario_id):
    try:
        usuarios = Usuario.get_usuarios(usuario_id)
        u = dict_helper_list(usuarios) 
        return jsonify(usuarios = u)            
    except Exception as err:
        response = jsonify({'message err': f'{err}'})
        return response, 401

# Recupera os dados do Usuário
@usersRoute.route('/api/usuarios/<int:id>', methods=['GET'])
@Auth.token_required
def get_usuario_id(usuario_id, id:int):
    try:
        usuario = Usuario.get_usuario_id(usuario_id, id)
        u = dict_helper_list(usuario) 
        return jsonify(usuario = u)            
    except Exception as err:
        response = jsonify({'message err': f'{err}'})
        return response, 401    

# Atualiza a senha do usuario no banco de dados
@usersRoute.route('/api/usuarios/change_password', methods=['POST'])
@Auth.token_required
def change_password(usuario_id):
    try:
        obj = request.get_json()                
        ok = Usuario.change_password(usuario_id, obj['user_id_to_be_changed'], obj['old_pass'], obj['new_pass'], obj['new_pass_confirmed'])
        return jsonify(changed = ok)            
    except Exception as err:
        response = jsonify({'message err': f'{err}'})
        return response, 401    

"""
@usersRoute.route('/api/usuarios/teste', methods=['GET'])  
def teste():
    ok = Usuario.generate_password()
    return jsonify(changed = ok)  
"""

#PRecisa arrumar aqui pra fazer a front
# Criar o usuario
#
#Adiciona um usuario no banco de dados
@usersRoute.route('/api/usuarios/add', methods=['POST'])
@Auth.token_required
def add_usuarios(usuario_id, primeiro_nome, sobrenome, email):
    try:
        primeiro_nome = request.get_json()
        sobrenome = request.get_json()
        email = request.get_json()
        usuario = Usuario.add_usuarios(usuario_id, primeiro_nome, sobrenome, email)
        u = dict_helper_obj(usuario)
        return jsonify(usuario = u)
    except Exception as err:
        response = jsonify({'message err': f'{err}'})
        return response, 404

#Atualiza o usuario
#
@usersRoute.route('/api/usuarios/update/<int:usuario_id>', methods=['PUT'])
@Auth.token_required
def update_usuarios(usuario_id: int, username, primeiro_nome, sobrenome, email):
    try:
        usuario_id = request.get_json()
        username = request.get_json()
        primeiro_nome = request.get_json()
        sobrenome = request.get_json()
        email = request.get_json
        usuario = Usuario.update_usuarios(usuario_id, username, primeiro_nome, sobrenome, email)
        u = dict_helper_obj(usuario)
        return jsonify(usuario = u)
    except Exception as err:
        response = jsonify({'message err': f'{err}'})
        return response, 401

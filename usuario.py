
from config import parameters
from sqlalchemy import  Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import (BOOLEAN, INTEGER, TEXT, VARCHAR)
from sqlalchemy import create_engine, func
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import ilike_op
from werkzeug.security import generate_password_hash, check_password_hash

from seguranca.pemissoes import Permissao
from seguranca.usuario_permissao import Usuario_Permissao
from seguranca.business_exception import BusinessException
import uuid
import re 
import random
import string

regex = '[a-z0-9!#$%&’*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&’*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?'

Base = declarative_base()

# Mapeia o banco de dados
engine = create_engine(parameters['SQLALCHEMY_DATABASE_URI'], echo=True)
session = Session(engine)

class Usuario (Base):
    __tablename__ = "USUARIO"

    usuario_id = Column(INTEGER, primary_key=True)
    primeiro_nome = Column(TEXT(30), nullable=False)
    sobrenome =  Column(TEXT(100), nullable=False)
    username = Column(TEXT(150), nullable=False)
    senha = Column(VARCHAR(500), nullable=False)
    email = Column(VARCHAR(250), nullable=False)
    ativo = Column(BOOLEAN, nullable=False)
    chave_publica = Column(TEXT(100), nullable=False)

    def __repr__(self) -> str:
        return f"Usuario(usuario_id={self.usuario_id!r},primeiro_nome={self.primeiro_nome!r},sobrenome={self.sobrenome!r},\
            senha={self.senha!r},email={self.ativo!r},email={self.ativo!r},email={self.chave_publica!r})"
    
    def __init__(self, primeiro_nome, sobrenome, username, senha, email, ativo):
        self.primeiro_nome = primeiro_nome
        self.sobrenome = sobrenome
        self.username = username
        self.senha = senha
        self.email = email
        self.ativo = ativo
    
    # Retorna o resultado da Classe em formato json
    def obj_to_dict(self):  
        return {
            'usuario_id': str(self.usuario_id),
            'primeiro_nome': self.primeiro_nome,
            'sobrenome': self.sobrenome,
            'username': self.username,
            'senha': self.senha,
            'email': self.email,
            'ativo': self.ativo,
            'chave_publica' : self.chave_publica
        }   
        
    def generate_password():  
        """
        A password is generated by the following criteria:
            8 characters length or more
            1 digit or more
            1 symbol or more
            1 uppercase letter or more
            1 lowercase letter or more
        """                            
        n = random.choice([8, 9, 10, 11, 12])
        
        # Garante pelo menos um dos tipos de critérios para senha
        p = random.choice(string.ascii_lowercase)
        p += random.choice(string.ascii_uppercase)
        p += random.choice(string.digits)
        p += random.choice(string.punctuation)

        # Gera Caracteres Aleatórios
        characters = string.ascii_letters + string.digits + string.punctuation
        random_characters = ''.join(random.choice(characters) for i in range(n - 4))
        random_characters += p
        password = '' .join(random.sample(random_characters, n))
        
        return password
        
    def password_check(password):
        """
        Verify the strength of 'password'
        Returns a dict indicating the wrong criteria
        A password is considered strong if:
            8 characters length or more
            1 digit or more
            1 symbol or more
            1 uppercase letter or more
            1 lowercase letter or more
        """

        # calculating the length
        length_error = len(password) < 8

        # searching for digits
        digit_error = re.search(r"\d", password) is None

        # searching for uppercase
        uppercase_error = re.search(r"[A-Z]", password) is None

        # searching for lowercase
        lowercase_error = re.search(r"[a-z]", password) is None

        # searching for symbols
        #symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None
        symbol_error = re.search(r"\W", password) is None

        # overall result
        password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

        return password_ok
    
    # Validador de e-mail
    def email_eh_valido(email):  
        if(re.search(regex,email)):  
            return True   
        else:  
            return False           
    
    # Retorna os usuários cadastrados
    def get_usuarios(usuario_id):
        try:
            # Verifica se o usuário pode ver o conteúdo da tabela usuário
            acesso_liberado = Permissao.valida_permissao_usuario(usuario_id, 'Pode_Visualizar_Usuarios')
            if not acesso_liberado:                
                raise BusinessException('Usuário não possui permissão para visualização da lista de usuários')
            usuarios = session.query(Usuario).all()  

            return usuarios 
        except BusinessException as err:
            raise Exception(err)
        except Exception:
            # tratamento de erro desconhecido
            return Exception('Erro desconhecido')

    # Retorna os dados do usuário informado
    def get_usuario_id(usuario_id, id, permissao_pai: str=None):
        """
        Este método utiliza um conceito de permissão pai, quando invocado por uma outra classe.
        Facilita para não ter que dar outras permissões para o usuário
        Utiliza a permissão do método que a chamou
        """
        try:
            # Verifica se o usuário pode ver o conteúdo da tabela usuarios            
            acesso_liberado = False
            if permissao_pai:
                acesso_liberado = Permissao.valida_permissao_usuario(usuario_id, permissao_pai)
            else:
                acesso_liberado = Permissao.valida_permissao_usuario(usuario_id, 'Pode_Visualizar_Usuarios')
            if not acesso_liberado:                
                raise BusinessException('Usuário não possui permissão para visualização de dados de usuários')
            
            # Retorna o usuario selecionado
            usuario = session.query(Usuario).where(Usuario.usuario_id == id).all()  
            if not usuario:                
                raise BusinessException('Usuário não encontrado')

            return usuario 
        except BusinessException as err:
            raise Exception(err)
        except Exception:
            # tratamento de erro desconhecido
            return Exception('Erro desconhecido') 

    def add_usuarios(usuario_id, primeiro_nome, sobrenome, email):
        try:
            # Verifica se o usuário pode adicionar um novo usuario usuário
            acesso_liberado = Permissao.valida_permissao_usuario(usuario_id, 'Pode_Adicionar_Usuarios')
            if not acesso_liberado:                
                raise BusinessException('Usuário não possui permissão para adicionar novos usuários')
            
            # Verifica se os campos estão preenchidos
            if primeiro_nome == '' or  not primeiro_nome:
                raise BusinessException('Primeiro nome é obrigatório')

            if sobrenome == '' or  not sobrenome:
                raise BusinessException('Sobrenome é obrigatório')            

            if email == '' or  not email:
                raise BusinessException('E-mail é obrigatório')  

            if Usuario.email_eh_valido(email):
                raise BusinessException('E-mail não é Válido')                       

            # Verifica se já existe um e-mail cadastrado no banco de dados
            rows = session.query(Usuario).where(Usuario.email == email).count()   
            if rows > 0:
                raise BusinessException('E-mail já cadastrado no banco de dados')

            # Gera o username do usuário
            n = sobrenome.split()
            x = len(n)

            username = ''
            rows = 0
            for l in primeiro_nome:
                pn = pn.join(l)
                username = pn + '.' + n[x -1]
                # Verifcar se este username já existe no banco de dados
                rows = session.query(Usuario).where(Usuario.username == username).count()
                if rows == 0:
                    break
                
            novoUsuario = Usuario(
                primeiro_nome = primeiro_nome.upper().strip(),
                sobrenome = sobrenome.upper().strip(),
                username = username,
                email = email.upper(),
                ativo = True,
                # Criptografa a senha do usuário 
                # Gera senha aleatória
                senha =  generate_password_hash(Usuario.generate_password()), 
                # Gera uma chave de identificador único para o usuário
                chave_publica = str(uuid.uuid4()) 
            )

            # Adiciona um novo usuário
            session.add(novoUsuario)        
            session.commit()     
            return 'ok'
        
        except BusinessException as err:
            raise Exception(err)
        except Exception:
            # tratamento de erro desconhecido
            return Exception('Erro desconhecido')    
    
    # Retorna os dados do usuário pelo parametro e-mail
    def get_usuario_by_email(email):
        sql = select(Usuario).where(Usuario.email == email)
        usuario = session.scalars(sql).one()
        return usuario

    # Retorna os dados do usuário pela chave pública
    def get_usuario_by_chave_publica(chave_publica):
        sql = select(Usuario).where(Usuario.chave_publica == chave_publica)
        usuario = session.scalars(sql).one()
        return usuario  

    def change_password(usuario_id, user_id_to_be_changed, old_pass, new_pass, new_pass_confirmed):
        try:
            # Retorna o usuário a ser alterado
            sql = select(Usuario).where(Usuario.usuario_id == user_id_to_be_changed)
            usuario = session.scalars(sql).one()     
            
            # Se o usario é o mesmo que será editado, não precisa checar a permissão
            # Se for diferente, o usuário precisa ter permissao de alteraçao
            if (usuario_id != user_id_to_be_changed):
                # Verifica se o usuário pode adicionar um novo usuario usuário
                acesso_liberado = Permissao.valida_permissao_usuario(usuario_id, 'Pode_Atualizar_Usuarios')
                if not acesso_liberado:                
                    raise BusinessException('Usuário não possui permissão para adicionar novos usuários')
            
            else:
                # Se o usario é o mesmo, precisa checar se a senha informada é válida
                if not check_password_hash(usuario.senha, old_pass): 
                    raise BusinessException('Senha informada não confere')
            
            # Verifica a nova senha
            if (new_pass != new_pass_confirmed):
                raise BusinessException('Senha informada não confere')
                
            if (not Usuario.password_check(new_pass)):
                raise BusinessException('Senha informada não confere com os critérios de segurança')
            
            # Encripta a nova senha para salvar no banco de dados
            usuario.senha = generate_password_hash(new_pass)
            
            # Comita as alterações no banco de dados
            session.commit()
            return 'ok'
        
        except BusinessException as err:
            raise Exception(err)
        except Exception:
            # tratamento de erro desconhecido
            return Exception('Erro desconhecido')                  
        
    def update_usuarios(usuario_id, username, primeiro_nome, sobrenome, email):
        # Verifica a permissão do usuario para poder editar usuarios
        acesso_liberado = Permissao.valida_permissao_usuario(usuario_id, 'Pode_Adicionar_Usuarios')
        if not acesso_liberado:
            raise BusinessException('Usuário não possui permissão para editar os dados do usuário')
        # Aqui começa a validar os campos
        if 'usuario_id' != usuario_id:
            raise BusinessException('Usuário não encontrado')

        if username == '' or not username:
            raise BusinessException('Nome de usuário é obrigatório')

        if primeiro_nome == '' or not primeiro_nome:
            raise BusinessException('Primeiro nome é obrigatório')

        if sobrenome == '' or not sobrenome:
            raise BusinessException('Sobrenome é obrigatório')

        if email == '' or not email:
            raise BusinessException('E-mail é obrigatório')


        # Recupera os dados do usuário informado
        sql = select(Usuario).where(Usuario.usuario_id == usuario_id['usuario_id'])
        usuario = session.scalars(sql).one()
        if not usuario:
            raise BusinessException('Usuário não encontrado')

        # Agora verifica se as alterações já foram feitas:
        # Para nomes não importa eles estarem duplicados, apenas credenciais exclusivas
        # USERNAME
        if usuario.username != username['username']:
            rows = session.query(Usuario).where(
                and_(
                    Usuario.username == username['username'],
                    Usuario.usuario_id != usuario_id['usuario_id']
                )).count()
            if rows > 0:
                raise BusinessException('Nome de usuário já utilizado')

        # EMAIL
        if usuario.email != email['primeiro_nome']:
            rows = session.query(Usuario).where(
                and_(
                    Usuario.email == email['email'],
                    Usuario.usuario_id != usuario_id['usuario_id']
                )).count()
            if rows > 0:
                raise BusinessException('Email já utilizado')

        #Atualiza o objeto com as informações
        #
        #O que faz com o ativo?
        usuario.username = username['username'].upper().strip()
        usuario.primeiro_nome = primeiro_nome['primeiro_nome'].upper().strip()
        usuario.sobrenome = sobrenome['sobrenome'].upper().strip()
        usuario.chave_publica = str(uuid.uiUID4())
        session.commit()    


        #recupera as permissoes do usuario
    def get_permissoes_usuario(usuario_id):

        permissoes = session.query(Permissao.permissao)\
            .join(Usuario_Permissao, Permissao.permissao_id == Usuario_Permissao.permissao_id)\
            .where(Usuario_Permissao.usuario_id == usuario_id)\
            .order_by(Permissao.permissao).all()
        return permissoes
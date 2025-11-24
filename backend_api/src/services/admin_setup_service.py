# src/services/admin_setup_service.py (VERSÃO FINAL E COMPLETA - Ciclo Quebrado)

from src.models.funcionario_dao import FuncionarioDAO
from src.db_connection import get_db_connection
import sys
import logging
import os
# REMOVER A IMPORTAÇÃO: from app import bcrypt 
# (O objeto bcrypt agora é passado como argumento da função)

logger = logging.getLogger(__name__)

def initialize_application(app, bcrypt): 
    """
    Função principal de inicialização: cria um Superusuário MINIMAL.
    O objeto bcrypt é passado como argumento para quebrar a dependência circular.
    """
    
    conn = get_db_connection()
    if conn is None:
        logger.error("ERRO CRÍTICO: Não foi possível conectar ao banco de dados.")
        sys.exit(1) 

    try:
        # 1. Verificar/Criar o Tipo de Funcionário 'Admin'
        CARGO_ADMIN_TEMP = 'Admin'
        with conn.cursor() as cur:
            cur.execute(f"SELECT id_tipo_funcionario FROM tipo_funcionario WHERE cargo = %s", (CARGO_ADMIN_TEMP,))
            result = cur.fetchone()

        if result is None:
            with conn.cursor() as cur:
                cur.execute(f"INSERT INTO tipo_funcionario (cargo) VALUES (%s) RETURNING id_tipo_funcionario;", (CARGO_ADMIN_TEMP,))
                result = cur.fetchone()
                conn.commit()
                logger.info(f"Tipo de funcionário '{CARGO_ADMIN_TEMP}' criado com sucesso.")
        
        tipo_admin_id = result[0]

        # 2. Verificar se o Superusuário Admin já existe
        admin_cpf = '00000000000'
        funcionario_dao = FuncionarioDAO()
        admin_exists = funcionario_dao.find_by_cpf(admin_cpf)

        if admin_exists is None:
            
            print("\n" + "="*50)
            print("🚀 PRIMEIRO SETUP DA APLICAÇÃO: CADASTRO DO SUPERUSUÁRIO TEMPORÁRIO")
            print("==================================================")
            
            # --- COLETA DE DADOS OBRIGATÓRIOS ---
            nome = input("Nome do Superusuário: ")
            email = input("Email do Superusuário (Obrigatório): ") # <-- CAMPO AGORA COLETADO
            
            # --- COLETA DE SENHA ---
            while True:
                senha_pura = input("Senha do Superusuário (mínimo 6 caracteres): ")
                if len(senha_pura) >= 6:
                    break
                print("A senha deve ter pelo menos 6 caracteres.")
            
            # 3. Hash da Senha e Inserção
            senha_hashed = bcrypt.generate_password_hash(senha_pura).decode('utf-8')
            
            # Insere o Superusuário Mínimo (com email preenchido e o resto como NULL)
            cpf_inserido = funcionario_dao.insert(
                cpf=admin_cpf,
                nome=nome,
                sobrenome=None, 
                senha_hashed=senha_hashed,
                id_tipo_funcionario=tipo_admin_id,
                email=email, # <-- PASSANDO O EMAIL COLETADO
                sexo=None, 
                telefone=None,
                nome_social=None, 
                localizacao_data=None 
            )

            if cpf_inserido:
                print("\n✅ SUPERUSUÁRIO TEMPORÁRIO CRIADO COM SUCESSO!")
                print(f"CPF de Acesso: {admin_cpf}")
                print("==================================================\n")
            else:
                print("ERRO: Falha na inserção do Superusuário. Verifique as configurações do DB.")
                sys.exit(1)
        
        else:
            logger.info("Superusuário Admin já existe. Ignorando setup inicial.")

    except Exception as e:
        logger.error(f"Erro na rotina de setup inicial do DB: {e}")
        if conn: conn.rollback()
        sys.exit(1)
    finally:
        if conn: conn.close()
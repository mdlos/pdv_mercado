import psycopg2
import random
from datetime import datetime, timedelta
import hashlib
from faker import Faker
import time

class PopuladorBancoDados:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'pdv_market_coffee',
            'user': 'seu_usuario',
            'password': 'sua_senha',
            'port': '5432'
        }
        
        self.fake = Faker('pt_BR')
        self.conexao = None
        self.cursor = None
        
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            self.conexao = psycopg2.connect(**self.db_config)
            self.cursor = self.conexao.cursor()
            print("✅ Conexão estabelecida com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            return False
    
    def desconectar_banco(self):
        """Desconecta do banco de dados"""
        if self.cursor:
            self.cursor.close()
        if self.conexao:
            self.conexao.close()
        print("✅ Conexão fechada!")
    
    def hash_senha(self, senha):
        """Gera hash SHA256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def limpar_tabelas(self):
        """Limpa todas as tabelas (cuidado!)"""
        print("\n⚠️  LIMPANDO TABELAS...")
        try:
            # Desabilitar constraints temporariamente
            self.cursor.execute("SET session_replication_role = 'replica';")
            
            # Ordem correta para evitar erros de FK
            tabelas = [
                'devolucao_credito', 'devolucao_item', 'devolucao',
                'nota_fiscal', 'pagamento', 'venda_item', 'venda',
                'compra_item', 'compra', 'estoque', 'produto',
                'fornecedor', 'funcionario', 'cliente', 'localizacao',
                'fluxo_caixa', 'tipo_pagamento', 'tipo_funcionario'
            ]
            
            for tabela in tabelas:
                try:
                    self.cursor.execute(f"DELETE FROM {tabela} CASCADE;")
                    print(f"   Limpada tabela: {tabela}")
                except Exception as e:
                    print(f"   Não foi possível limpar {tabela}: {e}")
            
            # Reabilitar constraints
            self.cursor.execute("SET session_replication_role = 'origin';")
            self.conexao.commit()
            print("✅ Todas as tabelas foram limpas!")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao limpar tabelas: {e}")
    
    def popular_tipo_funcionario(self):
        """Popula a tabela tipo_funcionario"""
        print("\n📋 Populando TIPO_FUNCIONARIO...")
        
        cargos = [
            'Gerente',
            'Caixa',
            'Vendedor',
            'Estoquista',
            'Supervisor',
            'Auxiliar',
            'Administrativo'
        ]
        
        try:
            for cargo in cargos:
                self.cursor.execute(
                    "INSERT INTO tipo_funcionario (cargo) VALUES (%s) ON CONFLICT (cargo) DO NOTHING;",
                    (cargo,)
                )
            
            self.conexao.commit()
            print(f"✅ Inseridos {len(cargos)} tipos de funcionário")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular tipo_funcionario: {e}")
    
    def popular_tipo_pagamento(self):
        """Popula a tabela tipo_pagamento"""
        print("\n💳 Populando TIPO_PAGAMENTO...")
        
        formas_pagamento = [
            'Dinheiro',
            'Cartão Débito',
            'Cartão Crédito',
            'PIX',
            'Vale Crédito',
            'Transferência',
            'Boleto',
            'Cheque'
        ]
        
        try:
            for forma in formas_pagamento:
                self.cursor.execute(
                    "INSERT INTO tipo_pagamento (descricao) VALUES (%s) ON CONFLICT (descricao) DO NOTHING;",
                    (forma,)
                )
            
            self.conexao.commit()
            print(f"✅ Inseridas {len(formas_pagamento)} formas de pagamento")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular tipo_pagamento: {e}")
    
    def popular_localizacao(self, quantidade=50):
        """Popula a tabela localizacao"""
        print(f"\n📍 Populando LOCALIZACAO ({quantidade} registros)...")
        
        try:
            for _ in range(quantidade):
                cep = self.fake.postcode()
                logradouro = self.fake.street_name()
                numero = str(random.randint(1, 9999))
                bairro = self.fake.bairro()
                cidade = self.fake.city()
                uf = self.fake.estado_sigla()
                
                self.cursor.execute(
                    """
                    INSERT INTO localizacao (cep, logradouro, numero, bairro, cidade, uf)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (cep, logradouro, numero, bairro, cidade, uf)
                )
            
            self.conexao.commit()
            print(f"✅ Inseridas {quantidade} localizações")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular localizacao: {e}")
    
    def popular_cliente(self, quantidade=100):
        """Popula a tabela cliente"""
        print(f"\n👥 Populando CLIENTE ({quantidade} registros)...")
        
        try:
            # Primeiro, pegar IDs de localização disponíveis
            self.cursor.execute("SELECT id_localizacao FROM localizacao ORDER BY RANDOM() LIMIT %s;", (quantidade,))
            ids_localizacao = [row[0] for row in self.cursor.fetchall()]
            
            if len(ids_localizacao) < quantidade:
                # Se não houver localizações suficientes, criar mais
                print("   Criando localizações adicionais...")
                self.popular_localizacao(quantidade - len(ids_localizacao))
                self.cursor.execute("SELECT id_localizacao FROM localizacao ORDER BY RANDOM() LIMIT %s;", (quantidade,))
                ids_localizacao = [row[0] for row in self.cursor.fetchall()]
            
            tipos_pessoa = ['Física', 'Jurídica']
            
            for i in range(quantidade):
                if random.choice([True, False]):  # 50% chance de ter localização
                    id_local = random.choice(ids_localizacao)
                else:
                    id_local = None
                
                tipo = random.choice(tipos_pessoa)
                
                if tipo == 'Física':
                    cpf_cnpj = self.fake.cpf()
                    nome = self.fake.name()
                else:
                    cpf_cnpj = self.fake.cnpj()
                    nome = self.fake.company()
                
                sexo = random.choice(['M', 'F', 'O'])
                telefone = self.fake.cellphone_number()
                email = self.fake.email() if random.choice([True, False]) else None
                
                self.cursor.execute(
                    """
                    INSERT INTO cliente (cpf_cnpj, nome, sexo, telefone, email, id_localizacao)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (cpf_cnpj, nome, sexo, telefone, email, id_local)
                )
            
            self.conexao.commit()
            print(f"✅ Inseridos {quantidade} clientes")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular cliente: {e}")
    
    def popular_fornecedor(self, quantidade=30):
        """Popula a tabela fornecedor"""
        print(f"\n🏢 Populando FORNECEDOR ({quantidade} registros)...")
        
        situacoes = ['ATIVA', 'SUSPENSA', 'INAPTA', 'BAIXADA']
        
        try:
            for _ in range(quantidade):
                cnpj = self.fake.cnpj()
                razao_social = self.fake.company()
                situacao_cadastral = random.choice(situacoes)
                data_abertura = self.fake.date_between(start_date='-20y', end_date='-1y')
                celular = self.fake.cellphone_number()
                email = self.fake.company_email()
                
                self.cursor.execute(
                    """
                    INSERT INTO fornecedor (cnpj, razao_social, situacao_cadastral, data_abertura, celular, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (cnpj, razao_social, situacao_cadastral, data_abertura, celular, email)
                )
            
            self.conexao.commit()
            print(f"✅ Inseridos {quantidade} fornecedores")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular fornecedor: {e}")
    
    def popular_funcionario(self, quantidade=20):
        """Popula a tabela funcionario"""
        print(f"\n👔 Populando FUNCIONARIO ({quantidade} registros)...")
        
        try:
            # Pegar IDs dos tipos de funcionário
            self.cursor.execute("SELECT id_tipo_funcionario, cargo FROM tipo_funcionario;")
            tipos_funcionario = self.cursor.fetchall()
            
            if not tipos_funcionario:
                print("   Criando tipos de funcionário...")
                self.popular_tipo_funcionario()
                self.cursor.execute("SELECT id_tipo_funcionario, cargo FROM tipo_funcionario;")
                tipos_funcionario = self.cursor.fetchall()
            
            # Distribuição de cargos
            distribuicao_cargos = {
                'Gerente': 2,
                'Caixa': 5,
                'Vendedor': 8,
                'Estoquista': 3,
                'Supervisor': 2
            }
            
            contador = 0
            for cargo, qtd in distribuicao_cargos.items():
                if contador >= quantidade:
                    break
                    
                # Encontrar ID do cargo
                id_tipo = None
                for tipo_id, tipo_cargo in tipos_funcionario:
                    if tipo_cargo == cargo:
                        id_tipo = tipo_id
                        break
                
                if id_tipo:
                    for _ in range(min(qtd, quantidade - contador)):
                        cpf = self.fake.cpf()
                        nome = self.fake.first_name()
                        sobrenome = self.fake.last_name()
                        nome_social = nome if random.choice([True, False]) else None
                        sexo = random.choice(['M', 'F'])
                        email = f"{nome.lower()}.{sobrenome.lower()}@marketcoffee.com.br"
                        senha_hash = self.hash_senha("123456")  # Senha padrão
                        telefone = self.fake.cellphone_number()
                        
                        self.cursor.execute(
                            """
                            INSERT INTO funcionario 
                            (cpf, nome, sobrenome, nome_social, sexo, email, senha, telefone, id_tipo_funcionario)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (cpf, nome, sobrenome, nome_social, sexo, email, senha_hash, telefone, id_tipo)
                        )
                        contador += 1
            
            # Se ainda precisar de mais funcionários, completar com cargos aleatórios
            if contador < quantidade:
                for _ in range(quantidade - contador):
                    id_tipo = random.choice(tipos_funcionario)[0]
                    cpf = self.fake.cpf()
                    nome = self.fake.first_name()
                    sobrenome = self.fake.last_name()
                    sexo = random.choice(['M', 'F'])
                    email = self.fake.email()
                    senha_hash = self.hash_senha("123456")
                    telefone = self.fake.cellphone_number()
                    
                    self.cursor.execute(
                        """
                        INSERT INTO funcionario 
                        (cpf, nome, sobrenome, sexo, email, senha, telefone, id_tipo_funcionario)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (cpf, nome, sobrenome, sexo, email, senha_hash, telefone, id_tipo)
                    )
                    contador += 1
            
            self.conexao.commit()
            print(f"✅ Inseridos {quantidade} funcionários")
            
            # Mostrar usuários criados
            self.cursor.execute("""
                SELECT f.cpf, f.nome, f.email, tf.cargo 
                FROM funcionario f
                JOIN tipo_funcionario tf ON f.id_tipo_funcionario = tf.id_tipo_funcionario
                ORDER BY tf.cargo, f.nome
            """)
            funcionarios = self.cursor.fetchall()
            print("\n👥 FUNCIONÁRIOS CRIADOS:")
            print("="*60)
            for cpf, nome, email, cargo in funcionarios:
                print(f"• {nome} ({cpf}) - {cargo}")
                print(f"  Email: {email} | Senha: 123456")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular funcionario: {e}")
    
    def popular_produto(self, quantidade=50):
        """Popula a tabela produto"""
        print(f"\n🛒 Populando PRODUTO ({quantidade} registros)...")
        
        categorias = {
            'Cafés': [
                ('Café Expresso', 'Café espresso tradicional', 5.00, 8.00),
                ('Café com Leite', 'Café com leite vaporizado', 7.50, 10.00),
                ('Cappuccino', 'Cappuccino cremoso', 8.00, 12.00),
                ('Macchiato', 'Espresso com espuma de leite', 6.50, 9.00),
                ('Mocha', 'Café com chocolate', 9.00, 13.00),
                ('Americano', 'Café longo', 6.00, 8.50),
                ('Café Gelado', 'Café gelado com gelo', 8.50, 12.00)
            ],
            'Chás': [
                ('Chá Verde', 'Chá verde natural', 5.50, 7.50),
                ('Chá de Camomila', 'Chá calmante', 5.00, 7.00),
                ('Chá Preto', 'Chá preto forte', 6.00, 8.00),
                ('Chá de Hortelã', 'Chá refrescante', 5.50, 7.50)
            ],
            'Bolos': [
                ('Bolo de Chocolate', 'Fatia de bolo de chocolate', 6.50, 8.50),
                ('Bolo de Cenoura', 'Fatia de bolo de cenoura com chocolate', 6.00, 8.00),
                ('Bolo de Fubá', 'Fatia de bolo de fubá', 5.50, 7.50),
                ('Cheesecake', 'Fatia de cheesecake', 8.50, 11.00)
            ],
            'Salgados': [
                ('Coxinha', 'Coxinha de frango', 4.50, 6.00),
                ('Empada', 'Empada de frango', 4.00, 5.50),
                ('Quibe', 'Quibe assado', 5.00, 6.50),
                ('Pastel', 'Pastel de carne', 5.50, 7.00),
                ('Sanduíche Natural', 'Sanduíche de frango', 12.00, 15.00)
            ],
            'Sucos': [
                ('Suco de Laranja', 'Suco natural de laranja', 7.00, 9.00),
                ('Suco de Abacaxi', 'Suco natural de abacaxi', 6.50, 8.50),
                ('Suco de Morango', 'Suco natural de morango', 8.00, 10.00),
                ('Vitamina de Banana', 'Vitamina de banana com leite', 9.00, 11.00)
            ],
            'Produtos para Venda': [
                ('Café em Grãos 250g', 'Café especial em grãos', 25.00, 35.00),
                ('Café Moído 500g', 'Café moído tradicional', 18.00, 25.00),
                ('Xícara de Porcelana', 'Xícara personalizada', 35.00, 45.00),
                ('Kit Presente', 'Kit café + xícara', 50.00, 65.00)
            ]
        }
        
        try:
            produtos_inseridos = 0
            
            # Inserir produtos das categorias
            for categoria, lista_produtos in categorias.items():
                for nome, descricao, preco_min, preco_max in lista_produtos:
                    if produtos_inseridos >= quantidade:
                        break
                    
                    preco = round(random.uniform(preco_min, preco_max), 2)
                    codigo_barras = f'789{random.randint(100000000, 999999999):09d}'
                    
                    self.cursor.execute(
                        """
                        INSERT INTO produto (nome, descricao, preco, codigo_barras)
                        VALUES (%s, %s, %s, %s)
                        RETURNING codigo_produto
                        """,
                        (nome, descricao, preco, codigo_barras)
                    )
                    
                    codigo_produto = self.cursor.fetchone()[0]
                    
                    # Criar registro no estoque
                    estoque = random.randint(10, 100)
                    self.cursor.execute(
                        """
                        INSERT INTO estoque (codigo_produto, quantidade)
                        VALUES (%s, %s)
                        """,
                        (codigo_produto, estoque)
                    )
                    
                    produtos_inseridos += 1
            
            # Se precisar de mais produtos, criar genéricos
            if produtos_inseridos < quantidade:
                for i in range(quantidade - produtos_inseridos):
                    nome = f"Produto {i+1} - {self.fake.word().capitalize()}"
                    descricao = self.fake.text(max_nb_chars=100)
                    preco = round(random.uniform(2.00, 50.00), 2)
                    codigo_barras = f'789{random.randint(100000000, 999999999):09d}'
                    
                    self.cursor.execute(
                        """
                        INSERT INTO produto (nome, descricao, preco, codigo_barras)
                        VALUES (%s, %s, %s, %s)
                        RETURNING codigo_produto
                        """,
                        (nome, descricao, preco, codigo_barras)
                    )
                    
                    codigo_produto = self.cursor.fetchone()[0]
                    
                    # Criar registro no estoque
                    estoque = random.randint(0, 50)
                    self.cursor.execute(
                        """
                        INSERT INTO estoque (codigo_produto, quantidade)
                        VALUES (%s, %s)
                        """,
                        (codigo_produto, estoque)
                    )
            
            self.conexao.commit()
            print(f"✅ Inseridos {quantidade} produtos com estoque")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular produto: {e}")
    
    def popular_fluxo_caixa(self, quantidade=10):
        """Popula a tabela fluxo_caixa"""
        print(f"\n💰 Populando FLUXO_CAIXA ({quantidade} registros)...")
        
        try:
            # Pegar funcionários
            self.cursor.execute("SELECT cpf FROM funcionario WHERE cpf LIKE '1%' OR cpf LIKE '2%' LIMIT 5;")
            funcionarios = [row[0] for row in self.cursor.fetchall()]
            
            if not funcionarios:
                print("   Não há funcionários disponíveis")
                return
            
            for i in range(quantidade):
                status = 'FECHADO'  # A maioria será fechada
                if i == quantidade - 1:  # Último será aberto
                    status = 'ABERTO'
                
                saldo_inicial = round(random.uniform(100.00, 500.00), 2)
                saldo_final_informado = None
                
                if status == 'FECHADO':
                    saldo_final_informado = round(random.uniform(saldo_inicial + 50, saldo_inicial + 1000), 2)
                
                data_abertura = self.fake.date_time_between(start_date='-30d', end_date='now')
                cpf_funcionario = random.choice(funcionarios)
                data_fechamento = None
                
                if status == 'FECHADO':
                    data_fechamento = data_abertura + timedelta(hours=random.randint(8, 12))
                
                self.cursor.execute(
                    """
                    INSERT INTO fluxo_caixa 
                    (status, saldo_inicial, saldo_final_informado, data_hora_abertura, 
                     cpf_funcionario_abertura, data_hora_fechamento)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (status, saldo_inicial, saldo_final_informado, data_abertura, cpf_funcionario, data_fechamento)
                )
            
            self.conexao.commit()
            print(f"✅ Inseridos {quantidade} registros de fluxo de caixa")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular fluxo_caixa: {e}")
    
    def popular_venda(self, quantidade=200):
        """Popula a tabela venda e relacionadas"""
        print(f"\n🛍️  Populando VENDA ({quantidade} vendas)...")
        
        try:
            # Pegar dados necessários
            self.cursor.execute("SELECT id_cliente FROM cliente ORDER BY RANDOM() LIMIT 50;")
            clientes = [row[0] for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT cpf FROM funcionario WHERE cpf LIKE '1%' OR cpf LIKE '2%' LIMIT 10;")
            funcionarios = [row[0] for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT id_tipo, descricao FROM tipo_pagamento;")
            tipos_pagamento = self.cursor.fetchall()
            
            if not clientes or not funcionarios or not tipos_pagamento:
                print("   Dados insuficientes para criar vendas")
                return
            
            for venda_num in range(quantidade):
                # Dados da venda
                data_venda = self.fake.date_time_between(start_date='-60d', end_date='now')
                id_cliente = random.choice(clientes) if random.choice([True, False]) else None
                
                # Criar venda
                self.cursor.execute(
                    """
                    INSERT INTO venda (data_venda, valor_total, id_cliente)
                    VALUES (%s, %s, %s)
                    RETURNING id_venda
                    """,
                    (data_venda, 0, id_cliente)  # Valor total será atualizado depois
                )
                
                id_venda = self.cursor.fetchone()[0]
                
                # Adicionar itens à venda
                num_itens = random.randint(1, 5)
                valor_total_venda = 0
                
                for _ in range(num_itens):
                    # Pegar produto aleatório com estoque
                    self.cursor.execute("""
                        SELECT p.codigo_produto, p.preco, e.quantidade 
                        FROM produto p
                        JOIN estoque e ON p.codigo_produto = e.codigo_produto
                        WHERE e.quantidade > 0
                        ORDER BY RANDOM() LIMIT 1
                    """)
                    
                    produto = self.cursor.fetchone()
                    if not produto:
                        continue
                    
                    codigo_produto, preco_unitario, estoque = produto
                    quantidade_venda = random.randint(1, min(3, estoque))
                    valor_total_item = round(preco_unitario * quantidade_venda, 2)
                    
                    # Inserir item da venda
                    self.cursor.execute(
                        """
                        INSERT INTO venda_item 
                        (id_venda, codigo_produto, preco_unitario, quantidade_venda, valor_total)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (id_venda, codigo_produto, preco_unitario, quantidade_venda, valor_total_item)
                    )
                    
                    # Atualizar estoque
                    self.cursor.execute(
                        """
                        UPDATE estoque 
                        SET quantidade = quantidade - %s
                        WHERE codigo_produto = %s
                        """,
                        (quantidade_venda, codigo_produto)
                    )
                    
                    valor_total_venda += valor_total_item
                
                # Atualizar valor total da venda
                self.cursor.execute(
                    """
                    UPDATE venda 
                    SET valor_total = %s
                    WHERE id_venda = %s
                    """,
                    (valor_total_venda, id_venda)
                )
                
                # Adicionar pagamento
                id_tipo, descricao = random.choice(tipos_pagamento)
                self.cursor.execute(
                    """
                    INSERT INTO pagamento (valor_pago, id_tipo, id_venda)
                    VALUES (%s, %s, %s)
                    """,
                    (valor_total_venda, id_tipo, id_venda)
                )
                
                # Criar nota fiscal (50% das vendas)
                if random.choice([True, False]):
                    numero_nf = f"NF{id_venda:08d}"
                    status_nf = random.choice(['EMITIDA', 'CANCELADA', 'PENDENTE'])
                    
                    self.cursor.execute(
                        """
                        INSERT INTO nota_fiscal (numero_nf, data_emissao, valor_total, status, id_venda)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (numero_nf, data_venda.date(), valor_total_venda, status_nf, id_venda)
                    )
            
            self.conexao.commit()
            print(f"✅ Inseridas {quantidade} vendas completas")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular venda: {e}")
    
    def popular_compra(self, quantidade=50):
        """Popula a tabela compra e relacionadas"""
        print(f"\n📦 Populando COMPRA ({quantidade} compras)...")
        
        try:
            # Pegar dados necessários
            self.cursor.execute("SELECT id_fornecedor FROM fornecedor ORDER BY RANDOM() LIMIT 10;")
            fornecedores = [row[0] for row in self.cursor.fetchall()]
            
            if not fornecedores:
                print("   Não há fornecedores disponíveis")
                return
            
            for _ in range(quantidade):
                # Dados da compra
                data_compra = self.fake.date_between(start_date='-90d', end_date='today')
                data_entrega = data_compra + timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None
                id_fornecedor = random.choice(fornecedores)
                
                # Criar compra
                self.cursor.execute(
                    """
                    INSERT INTO compra (data_compra, data_entrega, valor_total_compra, id_fornecedor)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_compra
                    """,
                    (data_compra, data_entrega, 0, id_fornecedor)  # Valor total será atualizado depois
                )
                
                id_compra = self.cursor.fetchone()[0]
                
                # Adicionar itens à compra
                num_itens = random.randint(1, 8)
                valor_total_compra = 0
                
                for _ in range(num_itens):
                    # Pegar produto aleatório
                    self.cursor.execute("""
                        SELECT codigo_produto, preco 
                        FROM produto 
                        ORDER BY RANDOM() LIMIT 1
                    """)
                    
                    produto = self.cursor.fetchone()
                    if not produto:
                        continue
                    
                    codigo_produto, preco_venda = produto
                    
                    # Preço de compra é menor que o de venda
                    preco_unitario = round(preco_venda * random.uniform(0.4, 0.7), 2)
                    quantidade_compra = random.randint(10, 100)
                    valor_item = round(preco_unitario * quantidade_compra, 2)
                    
                    # Inserir item da compra
                    self.cursor.execute(
                        """
                        INSERT INTO compra_item 
                        (id_compra, codigo_produto, quantidade_compra, preco_unitario)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (id_compra, codigo_produto, quantidade_compra, preco_unitario)
                    )
                    
                    # Atualizar estoque
                    self.cursor.execute(
                        """
                        UPDATE estoque 
                        SET quantidade = quantidade + %s
                        WHERE codigo_produto = %s
                        """,
                        (quantidade_compra, codigo_produto)
                    )
                    
                    valor_total_compra += valor_item
                
                # Atualizar valor total da compra
                self.cursor.execute(
                    """
                    UPDATE compra 
                    SET valor_total_compra = %s
                    WHERE id_compra = %s
                    """,
                    (valor_total_compra, id_compra)
                )
            
            self.conexao.commit()
            print(f"✅ Inseridas {quantidade} compras")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular compra: {e}")
    
    def popular_devolucao(self, quantidade=20):
        """Popula a tabela devolucao e relacionadas"""
        print(f"\n🔄 Populando DEVOLUCAO ({quantidade} devoluções)...")
        
        try:
            # Pegar vendas para devolver
            self.cursor.execute("""
                SELECT v.id_venda, vi.codigo_produto, vi.quantidade_venda, vi.preco_unitario
                FROM venda v
                JOIN venda_item vi ON v.id_venda = vi.id_venda
                WHERE v.data_venda >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY RANDOM() LIMIT %s
            """, (quantidade * 2,))
            
            vendas_itens = self.cursor.fetchall()
            
            if not vendas_itens:
                print("   Não há vendas recentes para devolução")
                return
            
            motivos = [
                "Produto com defeito",
                "Arrependimento da compra",
                "Produto não correspondente à descrição",
                "Trocado por outro produto",
                "Data de validade vencida",
                "Embalagem danificada"
            ]
            
            for i in range(min(quantidade, len(vendas_itens))):
                id_venda, codigo_produto, quantidade_venda, preco_unitario = vendas_itens[i]
                
                # Quantidade a devolver (até a quantidade comprada)
                quantidade_devolvida = random.randint(1, quantidade_venda)
                motivo = random.choice(motivos)
                
                # Criar devolução
                self.cursor.execute(
                    """
                    INSERT INTO devolucao (motivo, data_devolucao, id_venda)
                    VALUES (%s, %s, %s)
                    RETURNING id_devolucao
                    """,
                    (motivo, datetime.now(), id_venda)
                )
                
                id_devolucao = self.cursor.fetchone()[0]
                
                # Item da devolução
                self.cursor.execute(
                    """
                    INSERT INTO devolucao_item (id_devolucao, codigo_produto, quantidade_devolvida, valor_unitario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (id_devolucao, codigo_produto, quantidade_devolvida, preco_unitario)
                )
                
                # Atualizar estoque
                self.cursor.execute(
                    """
                    UPDATE estoque 
                    SET quantidade = quantidade + %s
                    WHERE codigo_produto = %s
                    """,
                    (quantidade_devolvida, codigo_produto)
                )
                
                # Criar crédito (50% das devoluções)
                if random.choice([True, False]):
                    codigo_vale_credito = f"VC{id_devolucao:06d}{random.randint(1000, 9999)}"
                    data_validade = datetime.now() + timedelta(days=90)
                    status = 'DISPONIVEL'
                    
                    self.cursor.execute(
                        """
                        INSERT INTO devolucao_credito (id_devolucao, codigo_vale_credito, data_validade, status)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (id_devolucao, codigo_vale_credito, data_validade, status)
                    )
            
            self.conexao.commit()
            print(f"✅ Inseridas {min(quantidade, len(vendas_itens))} devoluções")
            
        except Exception as e:
            self.conexao.rollback()
            print(f"❌ Erro ao popular devolucao: {e}")
    
    def executar_tudo(self, limpar=False):
        """Executa todo o processo de população"""
        print("="*60)
        print("🚀 INICIANDO POPULAÇÃO DO BANCO DE DADOS")
        print("="*60)
        
        start_time = time.time()
        
        if not self.conectar_banco():
            return
        
        try:
            if limpar:
                self.limpar_tabelas()
            
            # População em ordem correta para evitar erros de FK
            self.popular_tipo_funcionario()
            self.popular_tipo_pagamento()
            self.popular_localizacao(50)
            self.popular_cliente(100)
            self.popular_fornecedor(30)
            self.popular_funcionario(20)
            self.popular_produto(50)
            self.popular_fluxo_caixa(10)
            self.popular_compra(50)
            self.popular_venda(200)
            self.popular_devolucao(20)
            
            end_time = time.time()
            tempo_total = end_time - start_time
            
            print("\n" + "="*60)
            print("✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print(f"⏱️  Tempo total: {tempo_total:.2f} segundos")
            
            # Resumo das tabelas
            print("\n📊 RESUMO DAS TABELAS:")
            print("-"*40)
            
            tabelas = [
                'tipo_funcionario', 'tipo_pagamento', 'localizacao',
                'cliente', 'fornecedor', 'funcionario', 'produto',
                'estoque', 'fluxo_caixa', 'venda', 'venda_item',
                'pagamento', 'nota_fiscal', 'compra', 'compra_item',
                'devolucao', 'devolucao_item', 'devolucao_credito'
            ]
            
            for tabela in tabelas:
                try:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {tabela};")
                    count = self.cursor.fetchone()[0]
                    print(f"• {tabela}: {count} registros")
                except:
                    print(f"• {tabela}: ERRO AO CONTAR")
            
            print("\n🔑 CREDENCIAIS PARA TESTE:")
            print("-"*40)
            print("Gerente: CPF 111.111.111-11 | Senha: 123456")
            print("Todos os funcionários têm senha: 123456")
            
        except Exception as e:
            print(f"\n❌ ERRO GERAL: {e}")
        
        finally:
            self.desconectar_banco()
    
    def gerar_relatorio(self):
        """Gera um relatório do banco de dados"""
        if not self.conectar_banco():
            return
        
        try:
            print("\n" + "="*60)
            print("📈 RELATÓRIO DO BANCO DE DADOS")
            print("="*60)
            
            # Estatísticas principais
            queries = {
                'Total de Clientes': "SELECT COUNT(*) FROM cliente;",
                'Total de Produtos': "SELECT COUNT(*) FROM produto;",
                'Produtos em Estoque': "SELECT SUM(quantidade) FROM estoque;",
                'Valor Total em Estoque': """
                    SELECT SUM(p.preco * e.quantidade) 
                    FROM produto p
                    JOIN estoque e ON p.codigo_produto = e.codigo_produto;
                """,
                'Total de Vendas': "SELECT COUNT(*) FROM venda;",
                'Valor Total Vendido': "SELECT SUM(valor_total) FROM venda;",
                'Vendas Hoje': """
                    SELECT COUNT(*), COALESCE(SUM(valor_total), 0)
                    FROM venda 
                    WHERE DATE(data_venda) = CURRENT_DATE;
                """,
                'Funcionários Ativos': "SELECT COUNT(*) FROM funcionario;",
                'Caixas Abertos': "SELECT COUNT(*) FROM fluxo_caixa WHERE status = 'ABERTO';"
            }
            
            for descricao, query in queries.items():
                self.cursor.execute(query)
                resultado = self.cursor.fetchone()[0]
                print(f"• {descricao}: {resultado if resultado else 0}")
            
            # Produtos mais vendidos
            print("\n🏆 PRODUTOS MAIS VENDIDOS:")
            print("-"*40)
            
            self.cursor.execute("""
                SELECT p.nome, SUM(vi.quantidade_venda) as total_vendido
                FROM venda_item vi
                JOIN produto p ON vi.codigo_produto = p.codigo_produto
                GROUP BY p.nome
                ORDER BY total_vendido DESC
                LIMIT 5;
            """)
            
            for nome, quantidade in self.cursor.fetchall():
                print(f"• {nome}: {quantidade} unidades")
            
            # Vendas por forma de pagamento
            print("\n💳 VENDAS POR FORMA DE PAGAMENTO:")
            print("-"*40)
            
            self.cursor.execute("""
                SELECT tp.descricao, COUNT(p.id_pagamento) as quantidade, 
                       COALESCE(SUM(p.valor_pago), 0) as total
                FROM tipo_pagamento tp
                LEFT JOIN pagamento p ON tp.id_tipo = p.id_tipo
                GROUP BY tp.descricao
                ORDER BY total DESC;
            """)
            
            for forma, qtd, total in self.cursor.fetchall():
                print(f"• {forma}: {qtd} vendas (R$ {total:.2f})")
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
        
        finally:
            self.desconectar_banco()

def main():
    """Função principal"""
    print("="*60)
    print("🛒 PDV MARKET COFFEE - POPULADOR DE BANCO DE DADOS")
    print("="*60)
    
    populador = PopuladorBancoDados()
    
    while True:
        print("\n📋 MENU PRINCIPAL:")
        print("1. Popular todas as tabelas (com limpeza)")
        print("2. Popular todas as tabelas (sem limpar)")
        print("3. Popular tabelas específicas")
        print("4. Gerar relatório do banco")
        print("5. Limpar todas as tabelas")
        print("6. Sair")
        
        opcao = input("\nEscolha uma opção (1-6): ").strip()
        
        if opcao == '1':
            print("\n⚠️  ATENÇÃO: Esta opção irá LIMPAR TODOS os dados existentes!")
            confirmar = input("Deseja continuar? (s/n): ").lower()
            if confirmar == 's':
                populador.executar_tudo(limpar=True)
            else:
                print("Operação cancelada.")
        
        elif opcao == '2':
            populador.executar_tudo(limpar=False)
        
        elif opcao == '3':
            print("\n📊 TABELAS ESPECÍFICAS:")
            print("1. Clientes")
            print("2. Produtos")
            print("3. Funcionários")
            print("4. Vendas")
            print("5. Voltar")
            
            sub_opcao = input("\nEscolha uma tabela (1-5): ").strip()
            
            if not populador.conectar_banco():
                continue
            
            try:
                if sub_opcao == '1':
                    qtd = int(input("Quantidade de clientes: "))
                    populador.popular_cliente(qtd)
                elif sub_opcao == '2':
                    qtd = int(input("Quantidade de produtos: "))
                    populador.popular_produto(qtd)
                elif sub_opcao == '3':
                    qtd = int(input("Quantidade de funcionários: "))
                    populador.popular_funcionario(qtd)
                elif sub_opcao == '4':
                    qtd = int(input("Quantidade de vendas: "))
                    populador.popular_venda(qtd)
                
                populador.conexao.commit()
            except Exception as e:
                print(f"❌ Erro: {e}")
            finally:
                populador.desconectar_banco()
        
        elif opcao == '4':
            populador.gerar_relatorio()
        
        elif opcao == '5':
            print("\n⚠️  ATENÇÃO: Esta opção irá APAGAR TODOS os dados do banco!")
            confirmar = input("Tem certeza? Esta ação não pode ser desfeita (s/n): ").lower()
            if confirmar == 's':
                if populador.conectar_banco():
                    populador.limpar_tabelas()
                    populador.desconectar_banco()
            else:
                print("Operação cancelada.")
        
        elif opcao == '6':
            print("\n👋 Saindo... Até logo!")
            break
        
        else:
            print("❌ Opção inválida! Tente novamente.")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    # Instalar dependências necessárias:
    # pip install psycopg2-binary faker
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")

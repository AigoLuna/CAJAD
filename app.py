from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import usuario, CodigoConvite
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='Front', static_folder='static')  #Configurações do Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cadastro.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cadastro_funci.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    tipo_desejado = request.args.get('tipo') or request.form.get('tipo', 'funcionario')

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            #Trava de segurança: impede empresa de logar na área de funcionário e vice-versa
            if user.tipo != tipo_desejado:
                return f"Acesso negado: Este usuário é do tipo '{user.tipo}', mas tentou entrar como '{tipo_desejado}'. <a href='/login?tipo={tipo_desejado}'>Voltar</a>"

            #Redirecionamento correto baseado no tipo do usuário logado
            if user.tipo == 'empresa':
                return redirect(url_for('empresa'))
            else:
                return redirect(url_for('funcionarios'))
        else:
            return f"E-mail ou senha incorretos. <a href='/login?tipo={tipo_desejado}'>Tentar novamente</a>"

    return render_template('login.html', tipo=tipo_desejado)



@app.route('/login_funci', methods=['GET', 'POST'])
def login_funci():
    tipo_desejado = request.args.get('tipo') or request.form.get('tipo', 'funcionario')

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            #Trava de segurança: Empresa não entra na área de funcionário e vice-versa
            if user.tipo != tipo_desejado:
                return f"Acesso negado: Este usuário é do tipo '{user.tipo}', mas tentou entrar como '{tipo_desejado}'. <a href='/login_funci?tipo={tipo_desejado}'>Voltar</a>"

            if user.tipo == 'empresa':
                return redirect(url_for('empresa'))
            else:
                return redirect(url_for('funcionarios'))
        else:
            return f"E-mail ou senha incorretos. <a href='/login_funci?tipo={tipo_desejado}'>Tentar novamente</a>"

    return render_template('login_funci.html', tipo=tipo_desejado)




# Rota de Cadastro com validação de código restrito para empresas
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    # Garante que se abrir direto /cadastro, o tipo padrão é 'empresa'
    tipo = request.args.get('tipo', 'empresa') 
    
    # ... resto do código da rota ...

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo', 'funcionario')
        
        #Pega o código enviado ou deixa vazio se não existir
        codigo_informado = request.form.get('codigo_empresa', '')

        #Se for cadastro de empresa, valida o código fixo de uso único
        if tipo_usuario == 'empresa':
            convite = CodigoConvite.query.filter_by(codigo=codigo_informado, usado=False).first()
            if not convite:
                return "Erro: Código de acesso de empresa inválido ou já utilizado! <a href='/cadastro?tipo=empresa'>Tentar outro código</a>"
            
            #Marca o código como usado para nunca mais poder ser reutilizado
            convite.usado = True

        senha_segura = generate_password_hash(senha)
        
        #Cria o usuário enviando o 'cod' preenchido (ou vazio para funcionário)
        novo_usuario = usuario(nome=nome, email=email, senha=senha_segura, tipo=tipo_usuario, cod=codigo_informado)

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            return f"Cadastro de {tipo_usuario.capitalize()} realizado com sucesso! <a href='/login?tipo={tipo_usuario}'>Ir para o Login</a>"
        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar (provavelmente o e-mail já está em uso): {e}"

    return render_template('cadastro.html', tipo=tipo)



@app.route('/cadastro_funci', methods=['GET', 'POST'])
def cadastro_funci():
    tipo = request.args.get('tipo', 'funcionario')

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo', 'funcionario')
        
        #Pega o código enviado ou deixa vazio se não existir
        codigo_informado = request.form.get('codigo_empresa', '')

        #Se for cadastro de empresa, valida o código fixo de uso único
        if tipo_usuario == 'empresa':
            convite = CodigoConvite.query.filter_by(codigo=codigo_informado, usado=False).first()
            if not convite:
                return "Erro: Código de acesso de empresa inválido ou já utilizado! <a href='/cadastro_funci?tipo=empresa'>Tentar outro código</a>"
            
        #Marca o código como usado para nunca mais poder ser reutilizado
            convite.usado = True

        senha_segura = generate_password_hash(senha)
        
        #Cria o usuário enviando o 'cod' preenchido (ou vazio para funcionário)
        novo_usuario = usuario(nome=nome, email=email, senha=senha_segura, tipo=tipo_usuario, cod=codigo_informado)

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            return f"Cadastro de {tipo_usuario.capitalize()} realizado com sucesso! <a href='/login_funci?tipo={tipo_usuario}'>Ir para o Login_funci</a>"
        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar (provavelmente o e-mail já está em uso): {e}"

    return render_template('cadastro_funci.html', tipo=tipo)




@app.route('/empresa')
def empresa():
    return render_template('empresa.html')

@app.route('/funcionarios')
def funcionarios():
    return render_template('funcionarios.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Cria códigos fixos de uso único para empresa caso ainda não existam no banco
        if CodigoConvite.query.count() == 0:  #Se não tiverem códigos no banco, ele gera esses códigos fixos
            lista_meus_codigos = [
                "A7K2M9", "B4R8X1", "C9T3P6", "D2W5L8", "E6N1Q4",
                "F8J3Z7", "G5V9A2", "H1P6Y4", "J7C2R9", "K3M8D5",
                "L9X4B1", "M2Q7T6", "N5A1W8", "P4Z9K3", "Q8D2F7",
                "R1Y6C5", "S7L3N9", "T4B8J2", "V6K1M5", "W9P3A7",
                "X2R5D8", "Y8C4Q1", "Z3N7F6", "A5T9H2", "B1W6K4",
                "C7P2X8", "D4M9V3", "E8R1Y5", "F2Q6L7", "G9J4Z1", 
            ]
            for c in lista_meus_codigos:
                novo_c = CodigoConvite(codigo=c, usado=False)
                db.session.add(novo_c)
            db.session.commit()
            print(">>> Códigos de empresa criados com sucesso no banco de dados!")

    app.run(debug=True)
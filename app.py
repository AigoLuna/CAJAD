import os
from datetime import datetime, timedelta
import io
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import usuario, CodigoConvite, AreaTrabalho, Epi, RegistroFotografico, Notificacao
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='Front', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cadastro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'chave_secreta_cajad_segura'

db.init_app(app)

def limpar_registros_antigos():
    """Apaga automaticamente registros pendentes com mais de 3 dias (72 horas) sem avaliação"""
    limite_72_horas = datetime.now() - timedelta(days=3)
    antigos = RegistroFotografico.query.filter(
        RegistroFotografico.status == 'pendente',
        RegistroFotografico.data_envio < limite_72_horas
    ).all()
    
    for reg in antigos:
        db.session.delete(reg)
    
    if antigos:
        db.session.commit()
        print(f">>> {len(antigos)} registro(s) pendentes com mais de 3 dias foram apagados automaticamente.")

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
            if user.tipo != tipo_desejado:
                return f"Acesso negado: Este usuário é do tipo '{user.tipo}', mas tentou entrar como '{tipo_desejado}'. <a href='/login?tipo={tipo_desejado}'>Voltar</a>"

            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome
            session['usuario_email'] = user.email
            session['usuario_tipo'] = user.tipo

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
            if user.tipo != tipo_desejado:
                return f"Acesso negado: Este usuário é do tipo '{user.tipo}', mas tentou entrar como '{tipo_desejado}'. <a href='/login_funci?tipo={tipo_desejado}'>Voltar</a>"

            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome
            session['usuario_email'] = user.email
            session['usuario_tipo'] = user.tipo

            if user.tipo == 'empresa':
                return redirect(url_for('empresa'))
            else:
                return redirect(url_for('funcionarios'))
        else:
            return f"E-mail ou senha incorretos. <a href='/login_funci?tipo={tipo_desejado}'>Tentar novamente</a>"

    return render_template('login_funci.html', tipo=tipo_desejado)

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    tipo = request.args.get('tipo') or request.form.get('tipo', 'funcionario')

    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')

        user = usuario.query.filter_by(email=email).first()

        if not user:
            return f"Erro: O e-mail informado não está registrado no sistema. <a href='/recuperar_senha?tipo={tipo}'>Tentar novamente</a>"

        # Atualiza a senha antiga para a nova senha do usuário no mesmo instante
        user.senha = generate_password_hash(nova_senha)
        db.session.commit()

        pagina_login = 'login' if tipo == 'empresa' else 'login_funci'
        return f"Senha alterada com sucesso! <a href='/{pagina_login}?tipo={tipo}'>Ir para o Login</a>"

    # Renderiza uma página simples de recuperação de senha mantendo o padrão visual
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>CAJAD Construções - Recuperar Senha</title>
        <style>
            body {{ background-color: #f4f7f9; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 400px; margin: 140px auto 40px auto; background: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); }}
            h2 {{ color: #002b45; text-align: center; margin-bottom: 20px; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; color: #176087; font-weight: bold; }}
            .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; box-sizing: border-box; }}
            .btn-enviar {{ width: 100%; background-color: #176087; color: white; border: none; border-radius: 6px; padding: 12px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
            .btn-enviar:hover {{ background-color: #002b45; }}
            .voltar {{ text-align: center; margin-top: 15px; }}
            .voltar a {{ color: #176087; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Recuperar Senha</h2>
            <form action="/recuperar_senha" method="POST">
                <input type="hidden" name="tipo" value="{tipo}">
                <div class="form-group">
                    <label for="email">E-mail cadastrado:</label>
                    <input type="email" id="email" name="email" required placeholder="seuemail@cajad.com">
                </div>
                <div class="form-group">
                    <label for="nova_senha">Nova Senha:</label>
                    <input type="password" id="nova_senha" name="nova_senha" required placeholder="Digite sua nova senha">
                </div>
                <button type="submit" class="btn-enviar">Atualizar Senha</button>
            </form>
            <div class="voltar">
                <a href="/{'login' if tipo == 'empresa' else 'login_funci'}?tipo={tipo}">Voltar ao Login</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    tipo = request.args.get('tipo', 'empresa') 

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo', 'funcionario')
        codigo_informado = request.form.get('codigo_empresa', '')

        if tipo_usuario == 'empresa':
            convite = CodigoConvite.query.filter_by(codigo=codigo_informado, usado=False).first()
            if not convite:
                return "Erro: Código de acesso de empresa inválido ou já utilizado! <a href='/cadastro?tipo=empresa'>Tentar outro código</a>"
            convite.usado = True

        senha_segura = generate_password_hash(senha)
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
        codigo_informado = request.form.get('codigo_empresa', '')

        if tipo_usuario == 'empresa':
            convite = CodigoConvite.query.filter_by(codigo=codigo_informado, usado=False).first()
            if not convite:
                return "Erro: Código de acesso de empresa inválido ou já utilizado! <a href='/cadastro_funci?tipo=empresa'>Tentar outro código</a>"
            convite.usado = True

        senha_segura = generate_password_hash(senha)
        novo_usuario = usuario(nome=nome, email=email, senha=senha_segura, tipo=tipo_usuario, cod=codigo_informado)

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            return f"Cadastro de {tipo_usuario.capitalize()} realizado com sucesso! <a href='/login_funci?tipo={tipo_usuario}'>Ir para o Login_funci</a>"
        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar (provavelmente o e-mail já está em uso): {e}"

    return render_template('cadastro_funci.html', tipo=tipo)

@app.route('/empresa', methods=['GET', 'POST'])
def empresa():
    limpar_registros_antigos()

    if request.method == 'POST':
        tipo_acao = request.form.get('acao')
        
        if tipo_acao == 'novo_local':
            nome_local = request.form.get('nome_local')
            descricao = request.form.get('descricao_local', '')
            if nome_local:
                nova_area = AreaTrabalho(nome=nome_local, descricao=descricao)
                db.session.add(nova_area)
                db.session.commit()
                
        elif tipo_acao == 'novo_equipamento':
            id_area = request.form.get('id_area')
            nome_epi = request.form.get('nome_epi')
            categoria = request.form.get('categoria', '')
            codigo = request.form.get('codigo', '')
            descricao_epi = request.form.get('descricao_epi', '')
            
            if nome_epi and id_area:
                novo_epi = Epi(nome=nome_epi, categoria=categoria, codigo=codigo, descricao=descricao_epi, obrigatorio=True, id_area=id_area)
                db.session.add(novo_epi)
                db.session.commit()
                
        return redirect(url_for('empresa'))

    locais_cadastrados = AreaTrabalho.query.all()
    todos_registros = RegistroFotografico.query.filter_by(status='pendente').order_by(RegistroFotografico.data_envio.desc()).all()
    
    registros_por_dia = {}
    for reg in todos_registros:
        dia_str = reg.data_envio.strftime('%d/%m/%Y')
        if dia_str not in registros_por_dia:
            registros_por_dia[dia_str] = []
        registros_por_dia[dia_str].append(reg)

    return render_template('empresa.html', locais=locais_cadastrados, registros_por_dia=registros_por_dia)

@app.route('/avaliar_registro/<int:id_foto>', methods=['POST'])
def avaliar_registro(id_foto):
    if 'usuario_id' not in session or session.get('usuario_tipo') != 'empresa':
        return redirect(url_for('login'))

    reg = RegistroFotografico.query.get_or_404(id_foto)
    acao = request.form.get('acao')
    nome_empresa = session.get('usuario_nome', 'Empresa')
    agora = datetime.now()

    if acao == 'aprovar':
        reg.status = 'aprovado'
        reg.empresa_responsavel = nome_empresa
        reg.data_avaliacao = agora
        
        msg = f"Seu registro de utilização (Área ID: {reg.id_area}) enviado em {reg.data_envio.strftime('%d/%m/%Y às %H:%M')} foi APROVADO por {nome_empresa} às {agora.strftime('%H:%M')}."
        notif = Notificacao(email_usuario=reg.email_usuario, mensagem=msg, tipo='aprovado', id_foto=reg.id_foto, data_criacao=agora)
        db.session.add(notif)
        db.session.commit()

    elif acao == 'negar':
        motivo = request.form.get('motivo', 'Nenhum motivo informado.')
        reg.status = 'negado'
        reg.motivo_rejeicao = motivo
        reg.empresa_responsavel = nome_empresa
        reg.data_avaliacao = agora

        msg = f"Seu registro (Área ID: {reg.id_area}) foi NEGADO por {nome_empresa} às {agora.strftime('%H:%M')} do dia {agora.strftime('%d/%m/%Y')}. Motivo: {motivo}"
        notif = Notificacao(email_usuario=reg.email_usuario, mensagem=msg, tipo='negado', id_foto=reg.id_foto, data_criacao=agora)
        db.session.add(notif)
        db.session.commit()

    return redirect(url_for('empresa'))

@app.route('/editar_local/<int:id_area>', methods=['POST'])
def editar_local(id_area):
    area = AreaTrabalho.query.get_or_404(id_area)
    novo_nome = request.form.get('nome_local')
    if novo_nome:
        area.nome = novo_nome
        db.session.commit()
    return redirect(url_for('empresa'))

@app.route('/editar_equipamento/<int:id_epi>', methods=['POST'])
def editar_equipamento(id_epi):
    epi = Epi.query.get_or_404(id_epi)
    novo_nome = request.form.get('nome_epi')
    nova_categoria = request.form.get('categoria')
    novo_codigo = request.form.get('codigo')
    nova_descricao = request.form.get('descricao_epi')
    
    if novo_nome:
        epi.nome = novo_nome
        epi.categoria = nova_categoria
        epi.codigo = novo_codigo
        epi.descricao = nova_descricao
        db.session.commit()
    return redirect(url_for('empresa'))

@app.route('/excluir_local/<int:id_area>', methods=['POST'])
def excluir_local(id_area):
    area = AreaTrabalho.query.get_or_404(id_area)
    db.session.delete(area)
    db.session.commit()
    return redirect(url_for('empresa'))

@app.route('/excluir_equipamento/<int:id_epi>', methods=['POST'])
def excluir_equipamento(id_epi):
    epi = Epi.query.get_or_404(id_epi)
    db.session.delete(epi)
    db.session.commit()
    return redirect(url_for('empresa'))

@app.route('/funcionarios')
def funcionarios():
    if 'usuario_id' not in session:
        return redirect(url_for('login_funci'))
    
    email_atual = session.get('usuario_email')
    minhas_notificacoes = Notificacao.query.filter_by(email_usuario=email_atual).order_by(Notificacao.data_criacao.desc()).all()
    
    locais_cadastrados = AreaTrabalho.query.all()
    return render_template('funcionarios.html', locais=locais_cadastrados, notificacoes=minhas_notificacoes)

@app.route('/registrar_utilizacao', methods=['POST'])
def registrar_utilizacao():
    if 'usuario_id' not in session:
        return redirect(url_for('login_funci'))

    usuario_id = session['usuario_id']
    nome_funcionario = session.get('usuario_nome', 'Desconhecido')
    email_usuario = session.get('usuario_email', 'sem-email@cajad.com')
    
    id_area = request.form.get('id_area')
    foto = request.files.get('foto')

    if not id_area:
        return "Área não informada!", 400

    conteudo_arquivo = b''
    nome_arq = 'sem_foto.jpg'
    mime_type = 'image/jpeg'

    if foto and foto.filename != '':
        conteudo_arquivo = foto.read()
        nome_arq = foto.filename
        mime_type = foto.content_type or 'image/jpeg'

    novo_registro = RegistroFotografico(
        id_area=int(id_area),
        usuario_id=usuario_id,
        nome_funcionario=nome_funcionario,
        email_usuario=email_usuario,
        nome_arquivo=nome_arq,
        tipo_mime=mime_type,
        arquivo=conteudo_arquivo,
        data_envio=datetime.now(),
        status='pendente'
    )
    db.session.add(novo_registro)
    db.session.commit()

    return redirect(url_for('funcionarios'))

@app.route('/baixar_foto/<int:id_foto>', methods=['GET'])
def baixar_foto(id_foto):
    reg = RegistroFotografico.query.get_or_404(id_foto)
    if not reg or not reg.arquivo:
        return "Foto não encontrada", 404
    
    return send_file(
        io.BytesIO(reg.arquivo),
        mimetype=reg.tipo_mime,
        as_attachment=True,
        download_name=reg.nome_arquivo
    )

@app.route('/reiniciar_checklist/<int:id_area>', methods=['POST'])
def reiniciar_checklist(id_area):
    registros = RegistroFotografico.query.filter_by(id_area=id_area).all()
    for reg in registros:
        db.session.delete(reg)
    db.session.commit()
    return {"status": "sucesso"}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if CodigoConvite.query.count() == 0:
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
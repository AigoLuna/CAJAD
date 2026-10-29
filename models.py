# Guardar os modelos do banco de dados
from datetime import datetime
from db import db

class usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='funcionario')  # 'empresa' ou 'funcionario'
    cod = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<{self.nome} - {self.tipo}>"



class CodigoConvite(db.Model):
    __tablename__ = 'codigos_convite'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    usado = db.Column(db.Boolean, default=False)  # False = disponível, True = já utilizado

    def __repr__(self):
        return f"<Codigo {self.codigo} - Usado: {self.usado}>"



class Colaborador(db.Model):
    __tablename__ = 'colaborador'

    id_colaborador = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    perfil = db.Column(db.String(20), nullable=False)  # 'COLABORADOR' ou 'GESTOR'
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamentos
    checagens = db.relationship('Checagem', backref='colaborador', lazy=True)
    auditorias = db.relationship('Auditoria', backref='gestor', lazy=True)

    def __repr__(self):
        return f"<Colaborador {self.nome} - {self.perfil}>"


class AreaTrabalho(db.Model):
    __tablename__ = 'area_trabalho'

    id_area = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativa = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamentos
    epis = db.relationship('Epi', secondary='area_epi', backref=db.backref('areas', lazy='dynamic'))
    checagens = db.relationship('Checagem', backref='area_trabalho', lazy=True)

    def __repr__(self):
        return f"<AreaTrabalho {self.nome}>"


class Epi(db.Model):
    __tablename__ = 'epi'

    id_epi = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    obrigatorio = db.Column(db.Boolean, nullable=False, default=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Epi {self.nome}>"


# Tabela associativa para a relação N para N entre Área e EPI
class AreaEpi(db.Model):
    __tablename__ = 'area_epi'

    id_area = db.Column(db.Integer, db.ForeignKey('area_trabalho.id_area'), primary_key=True)
    id_epi = db.Column(db.Integer, db.ForeignKey('epi.id_epi'), primary_key=True)


class Checagem(db.Model):
    __tablename__ = 'checagem'

    id_checagem = db.Column(db.Integer, primary_key=True)
    id_colaborador = db.Column(db.Integer, db.ForeignKey('colaborador.id_colaborador'), nullable=False)
    id_area = db.Column(db.Integer, db.ForeignKey('area_trabalho.id_area'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='PENDENTE')  # 'PENDENTE', 'ENVIADA', 'VERIFICADA', 'NAO_CONFORME'

    # Relacionamentos
    epis_checagem = db.relationship('ChecagemEpi', backref='checagem', lazy=True)
    registros_fotograficos = db.relationship('RegistroFotografico', backref='checagem', lazy=True)
    auditorias = db.relationship('Auditoria', backref='checagem', lazy=True)

    def __repr__(self):
        return f"<Checagem {self.id_checagem} - Status: {self.status}>"


class ChecagemEpi(db.Model):
    __tablename__ = 'checagem_epi'

    id_checagem = db.Column(db.Integer, db.ForeignKey('checagem.id_checagem'), primary_key=True)
    id_epi = db.Column(db.Integer, db.ForeignKey('epi.id_epi'), primary_key=True)
    conforme = db.Column(db.Boolean, nullable=False)
    observacao = db.Column(db.Text)


class RegistroFotografico(db.Model):
    __tablename__ = 'registro_fotografico'

    id_foto = db.Column(db.Integer, primary_key=True)
    id_checagem = db.Column(db.Integer, db.ForeignKey('checagem.id_checagem'), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo_mime = db.Column(db.String(100), nullable=False)
    arquivo = db.Column(db.LargeBinary, nullable=False)  
    data_envio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<RegistroFotografico {self.nome_arquivo}>"


class Auditoria(db.Model):
    __tablename__ = 'auditoria'

    id_auditoria = db.Column(db.Integer, primary_key=True)
    id_checagem = db.Column(db.Integer, db.ForeignKey('checagem.id_checagem'), nullable=False)
    id_gestor = db.Column(db.Integer, db.ForeignKey('colaborador.id_colaborador'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resultado = db.Column(db.String(20), nullable=False)  # 'CONFORME', 'NAO_CONFORME', 'PENDENTE'
    observacao = db.Column(db.Text)

    def __repr__(self):
        return f"<Auditoria {self.id_auditoria} - Resultado: {self.resultado}>"






    

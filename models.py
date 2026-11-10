# Guardar os modelos do banco de dados
from datetime import datetime
from db import db

class usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='funcionario')
    cod = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<{self.nome} {self.tipo}>"


class CodigoConvite(db.Model):
    __tablename__ = 'codigos_convite'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    usado = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Codigo {self.codigo} Usado: {self.usado}>"


class AreaTrabalho(db.Model):
    __tablename__ = 'area_trabalho'

    id_area = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativa = db.Column(db.Boolean, nullable=False, default=True)

    epis = db.relationship('Epi', backref='area_trabalho', lazy=True, cascade='all, delete-orphan')
    registros = db.relationship('RegistroFotografico', backref='area_trabalho', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<AreaTrabalho {self.nome}>"


class Epi(db.Model):
    __tablename__ = 'epi'

    id_epi = db.Column(db.Integer, primary_key=True)
    id_area = db.Column(db.Integer, db.ForeignKey('area_trabalho.id_area'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=True)
    codigo = db.Column(db.String(50), nullable=True)
    descricao = db.Column(db.Text)
    obrigatorio = db.Column(db.Boolean, nullable=False, default=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Epi {self.nome}>"


class RegistroFotografico(db.Model):
    __tablename__ = 'registro_fotografico'

    id_foto = db.Column(db.Integer, primary_key=True) 
    id_area = db.Column(db.Integer, db.ForeignKey('area_trabalho.id_area'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nome_funcionario = db.Column(db.String(120), nullable=False)
    email_usuario = db.Column(db.String(100), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo_mime = db.Column(db.String(100), nullable=False)
    arquivo = db.Column(db.LargeBinary, nullable=False)  
    data_envio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    status = db.Column(db.String(20), default='pendente') 
    motivo_rejeicao = db.Column(db.Text, nullable=True)
    empresa_responsavel = db.Column(db.String(120), nullable=True)
    data_avaliacao = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<RegistroFotografico ID: {self.id_foto} Area: {self.id_area} Status: {self.status}>"


class Notificacao(db.Model):
    __tablename__ = 'notificacoes'

    id_notificacao = db.Column(db.Integer, primary_key=True)
    email_usuario = db.Column(db.String(100), nullable=False) 
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  
    id_foto = db.Column(db.Integer, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notificacao Para: {self.email_usuario} Tipo: {self.tipo}>"
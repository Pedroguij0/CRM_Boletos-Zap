from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)
@views_bp.route('/')
@views_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@views_bp.route('/contatos')
def contatos():
    return render_template('contatos.html')    
@views_bp.route('/configuracoes')
def configuracoes():
    return render_template('configuracoes.html')    
@views_bp.route('/chat')
def chat():
    return render_template('chat.html')    
@views_bp.route('/logs')
def logs():
    return render_template('logs.html')    
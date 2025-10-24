from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from itsdangerous import URLSafeSerializer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mysql.connector
from mysql.connector.cursor import MySQLCursorDict
import hashlib
from typing import Optional, List, Dict, Any

# === CONFIGURAÇÃO DO BANCO DE DADOS ===
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "escola_db",
}


# --- MELHORIA NA GESTÃO DO BD ---
def get_db():
    """Dependência FastAPI para gerenciar conexões com o BD."""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    finally:
        if conn:
            conn.close()


# === CONFIGURAÇÃO DO FASTAPI ===
app = FastAPI(title="Sistema de Gestão Acadêmica")

# chave secreta para assinar cookies
SECRET_KEY = "minha_chave_super_secreta"
serializer = URLSafeSerializer(SECRET_KEY)

# montar o direcionamento para a pasta paginas (usando /static)
app.mount("/static", StaticFiles(directory="paginas"), name="static")
paginas = Jinja2Templates(directory="paginas")


# === SISTEMA DE AUTENTICAÇÃO E SESSÃO ===


def get_session_data(request: Request) -> Dict[str, Any]:
    """Lê o cookie de sessão e retorna os dados."""
    cookie = request.cookies.get("session")
    if cookie:
        try:
            data = serializer.loads(cookie)
            return data
        except Exception:
            return {}
    return {}


def require_session(request: Request) -> Dict[str, Any]:
    """
    Dependência de "muro" (guard).
    Verifica se o usuário está logado. Se não, redireciona para a home.
    """
    session_data = get_session_data(request)
    if not session_data.get("usuario"):
        # Redireciona para a página de login (rota "/")
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/"},
        )
    return session_data


def verificar_usuario(
    login: str, senha: str, conn: mysql.connector.MySQLConnection
) -> Optional[Dict[str, Any]]:
    """Verifica o usuário usando MD5, conforme solicitado."""
    # Como você pediu, mantendo o MD5 para testes
    senha_md5 = hashlib.md5(senha.encode()).hexdigest()

    # Usamos cursor com dictionary=True para facilitar o manuseio
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Users WHERE user = %s AND senha_hash = %s",
        (login, senha_md5),
    )
    usuario = cursor.fetchone()
    cursor.close()
    return usuario


# --- ROTAS DE AUTENTICAÇÃO ---


@app.get("/", response_class=HTMLResponse, summary="Página de Login ou Dashboard")
async def index(request: Request):
    """
    Se o usuário estiver logado, mostra o dashboard (login_sucesso.html).
    Se não, mostra a página de login (index.html).
    """
    session_data = get_session_data(request)
    if not session_data.get("usuario"):
        return paginas.TemplateResponse("index.html", {"request": request})
    else:
        # Usuário está logado, 'usuario' está na sessão
        context = {"request": request, "usuario": session_data.get("usuario")}
        return paginas.TemplateResponse("login_sucesso.html", context)


@app.post("/realizar_login", summary="Processa o formulário de login")
async def login(
    request: Request, conn: mysql.connector.MySQLConnection = Depends(get_db)
):
    form = await request.form()
    user = form.get("usuario")
    passw = form.get("senha")

    usuario_db = verificar_usuario(user, passw, conn)

    if usuario_db:
        session_data = {"usuario": usuario_db["user"]}
        cookie_value = serializer.dumps(session_data)

        # Redireciona para a home ("/") após o login
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="session", value=cookie_value, httponly=True)
        return response
    else:
        context = {"request": request, "error": "Usuário ou senha inválidos"}
        # Retorna a página de login com uma mensagem de erro
        return paginas.TemplateResponse("index.html", context=context, status_code=401)


@app.get("/logout", summary="Desloga o usuário")
def logout():
    """Limpa o cookie de sessão e redireciona para a home."""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session")
    return response


# --- [NOVAS ROTAS] RELATÓRIOS E LISTAGENS ---
# Todas as rotas abaixo usam Depends(require_session) para proteção.


@app.get(
    "/alunos",
    response_class=HTMLResponse,
    summary="[Relatório 1] Listar todos os alunos",
)
async def get_alunos(
    request: Request,
    session: Dict[str, Any] = Depends(require_session),
    conn: mysql.connector.MySQLConnection = Depends(get_db),
):

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_aluno, nome, cidade, estado, telefone FROM Aluno ORDER BY nome"
    )
    alunos = cursor.fetchall()
    cursor.close()

    context = {"request": request, "usuario": session.get("usuario"), "alunos": alunos}
    return paginas.TemplateResponse("alunos.html", context)


@app.get(
    "/professores",
    response_class=HTMLResponse,
    summary="[Relatório 2] Listar todos os professores",
)
async def get_professores(
    request: Request,
    session: Dict[str, Any] = Depends(require_session),
    conn: mysql.connector.MySQLConnection = Depends(get_db),
):

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_professor, nome, cidade, estado, telefone FROM Professor ORDER BY nome"
    )
    professores = cursor.fetchall()
    cursor.close()

    context = {
        "request": request,
        "usuario": session.get("usuario"),
        "professores": professores,
    }
    return paginas.TemplateResponse("professores.html", context)


@app.get(
    "/disciplinas/relatorio",
    response_class=HTMLResponse,
    summary="[Relatório 3] Diário de Disciplinas",
)
async def get_relatorio_disciplinas(
    request: Request,
    session: Dict[str, Any] = Depends(require_session),
    conn: mysql.connector.MySQLConnection = Depends(get_db),
):

    cursor = conn.cursor(dictionary=True)
    # Query complexa que busca tudo e ordena
    query = """
        SELECT 
            d.nome AS disciplina_nome, 
            p.nome AS professor_nome,
            a.nome AS aluno_nome, 
            m.nota1, m.nota2, m.nota3, m.nota4
        FROM Disciplina d
        LEFT JOIN Professor p ON d.id_professor_ministrante = p.id_professor
        LEFT JOIN Matricula m ON d.id_disciplina = m.id_disciplina
        LEFT JOIN Aluno a ON m.id_aluno = a.id_aluno
        WHERE a.nome IS NOT NULL
        ORDER BY d.nome, a.nome;
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()

    # Processar os dados em Python para agrupar por disciplina
    diario = {}
    for r in resultados:
        disciplina = r["disciplina_nome"]
        if disciplina not in diario:
            diario[disciplina] = {
                "nome": disciplina,
                "professor": r["professor_nome"],
                "alunos": [],
            }

        diario[disciplina]["alunos"].append(
            {
                "nome": r["aluno_nome"],
                "nota1": r["nota1"],
                "nota2": r["nota2"],
                "nota3": r["nota3"],
                "nota4": r["nota4"],
            }
        )

    context = {
        "request": request,
        "usuario": session.get("usuario"),
        "relatorio": diario.values(),  # Envia como uma lista
    }
    return paginas.TemplateResponse("relatorio_disciplinas.html", context)


def calcular_media_e_resultado(n1, n2, n3, n4, media_aprovacao=7.0):
    """Helper para calcular média e resultado, ignorando notas NULAS."""
    notas = [n for n in [n1, n2, n3, n4] if n is not None]

    if not notas:
        return (None, "Cursando")

    media = sum(notas) / len(notas)

    # Se ainda não tiver as 4 notas, está cursando
    if len(notas) < 4:
        return (round(media, 2), "Cursando")

    if media >= media_aprovacao:
        return (round(media, 2), "Aprovado")
    else:
        return (round(media, 2), "Reprovado")


@app.get(
    "/aluno/{id_aluno}/atestado",
    response_class=HTMLResponse,
    summary="[Relatório 4] Atestado de Matrícula do Aluno",
)
async def get_atestado_aluno(
    request: Request,
    id_aluno: int,
    session: Dict[str, Any] = Depends(require_session),
    conn: mysql.connector.MySQLConnection = Depends(get_db),
):

    cursor = conn.cursor(dictionary=True)

    # 1. Buscar dados do aluno
    cursor.execute("SELECT * FROM Aluno WHERE id_aluno = %s", (id_aluno,))
    aluno = cursor.fetchone()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # 2. Buscar disciplinas e notas do aluno
    query_matriculas = """
        SELECT 
            d.nome AS disciplina_nome,
            p.nome AS professor_nome,
            m.nota1, m.nota2, m.nota3, m.nota4
        FROM Matricula m
        JOIN Disciplina d ON m.id_disciplina = d.id_disciplina
        LEFT JOIN Professor p ON d.id_professor_ministrante = p.id_professor
        WHERE m.id_aluno = %s
        ORDER BY d.nome;
    """
    cursor.execute(query_matriculas, (id_aluno,))
    matriculas_db = cursor.fetchall()
    cursor.close()

    # 3. Processar notas em Python
    matriculas_processadas = []
    for m in matriculas_db:
        media, resultado = calcular_media_e_resultado(
            m["nota1"], m["nota2"], m["nota3"], m["nota4"]
        )
        m["media_final"] = media
        m["resultado_final"] = resultado
        matriculas_processadas.append(m)

    context = {
        "request": request,
        "usuario": session.get("usuario"),
        "aluno": aluno,
        "matriculas": matriculas_processadas,
    }
    return paginas.TemplateResponse("atestado_aluno.html", context)


# Rota de detalhamento que você já tinha (agora protegida)
@app.get("/detalhar", response_class=HTMLResponse)
def detalhar(request: Request, session: dict = Depends(require_session)):
    usuario = session.get("usuario")
    return paginas.TemplateResponse(
        "detalhamento.html", {"request": request, "usuario": usuario}
    )


if __name__ == "__main__":
    import uvicorn

    # Rodar o app: uvicorn app:app --reload
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

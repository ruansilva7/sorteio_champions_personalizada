import random
import tkinter as tk
from collections import Counter
from tkinter import font as tkfont

# =====================================================================
# 1) CORES FIXAS (as cores de cada competição ficam no bloco de dados)
# =====================================================================
BRANCO = "#FFFFFF"
VERMELHO = "#FF5C7A"      # o "✕" de remover clube

# =====================================================================
# 2) DADOS DAS COMPETIÇÕES
#    Cada competição tem: título, tema (cores) e os 4 potes (nome, país).
#    Aqui há só duas: a Champions League (lista de exemplo) e a Personalizada,
#    que começa vazia para o usuário montar do zero com o + e o ✕.
# =====================================================================
COMPETICOES = {
    "Champions League": {
        "titulo": "UEFA CHAMPIONS LEAGUE",
        "tema": {"fundo": "#050B2E", "cartao": "#101C66", "destaque": "#2FA8FF",
                 "claro": "#5CBCFF", "pisca": "#1E6FD9", "botao2": "#2A3A8F",
                 "prata": "#B8C4E6", "cinza": "#6B76A8"},
        # lista de exemplo (não é o sorteio oficial)
        "potes": {
            1: [("Real Madrid", "ESP"), ("Manchester City", "ENG"),
                ("Bayern de Munique", "GER"), ("Paris Saint-Germain", "FRA"),
                ("Inter de Milão", "ITA"), ("Barcelona", "ESP"),
                ("Liverpool", "ENG"), ("Borussia Dortmund", "GER")],
            2: [("Arsenal", "ENG"), ("Atlético de Madrid", "ESP"),
                ("Juventus", "ITA"), ("Milan", "ITA"),
                ("Benfica", "POR"), ("Porto", "POR"),
                ("Bayer Leverkusen", "GER"), ("Napoli", "ITA")],
            3: [("Chelsea", "ENG"), ("Tottenham", "ENG"),
                ("Sporting", "POR"), ("Ajax", "NED"),
                ("PSV", "NED"), ("Celtic", "SCO"),
                ("Galatasaray", "TUR"), ("Marseille", "FRA")],
            4: [("Atalanta", "ITA"), ("Club Brugge", "BEL"),
                ("Feyenoord", "NED"), ("RB Leipzig", "GER"),
                ("Monaco", "FRA"), ("Shakhtar", "UKR"),
                ("Red Bull Salzburg", "AUT"), ("Olympiacos", "GRE")],
        },
    },
    "Personalizada": {
        "titulo": "COMPETIÇÃO PERSONALIZADA",
        "tema": {"fundo": "#0B0720", "cartao": "#231A55", "destaque": "#A678FF",
                 "claro": "#C2A3FF", "pisca": "#6A3FD1", "botao2": "#43309A",
                 "prata": "#D2C8F2", "cinza": "#8479B5"},
        "potes": {1: [], 2: [], 3: [], 4: []},   # começa vazia: monte com o +
    },
}

NOMES_GRUPOS = "ABCDEFGH"
TAMANHO_POTE = len(NOMES_GRUPOS)   # 8 clubes por pote (1 para cada grupo)
JOGOS_POR_GRUPO = 12               # 6 rodadas x 2 jogos

# chance de cada quantidade de gols na simulação (0, 1, 2, 3, 4, 5)
GOLS_POSSIVEIS = [0, 1, 2, 3, 4, 5]
GOLS_PESOS = [22, 32, 25, 13, 6, 2]


def aplicar_tema(tema):
    """Troca as cores globais. Os widgets lêem essas cores quando são criados."""
    global FUNDO, CARTAO, DESTAQUE, DESTAQUE_CLARO, PISCA, BOTAO2, PRATA, CINZA
    FUNDO = tema["fundo"]              # fundo da janela
    CARTAO = tema["cartao"]            # fundo dos cartões
    DESTAQUE = tema["destaque"]        # títulos e botão principal
    DESTAQUE_CLARO = tema["claro"]     # botão com o mouse em cima
    PISCA = tema["pisca"]              # piscada quando um clube é sorteado
    BOTAO2 = tema["botao2"]            # botões secundários
    PRATA = tema["prata"]              # textos secundários
    CINZA = tema["cinza"]              # textos apagados


aplicar_tema(COMPETICOES["Champions League"]["tema"])


# =====================================================================
# 3) LÓGICA (sem nada de interface, só regras)
# =====================================================================
def realizar_sorteio(potes):
    """
    Faz o sorteio completo e devolve uma lista de 'passos'.
    Cada passo é uma tupla: (pote, (nome, pais), indice_do_grupo).
    A interface depois só "reproduz" esses passos, um por vez.

    Se os potes estiverem incompletos (ou o sorteio for impossível),
    levanta um ValueError com a mensagem que aparece na tela.
    """
    listas = {p: [c for c in potes[p] if c] for p in (1, 2, 3, 4)}

    faltam = sum(TAMANHO_POTE - len(lista) for lista in listas.values())
    if faltam:
        raise ValueError(f"Faltam {faltam} clube(s) nos potes. Use o + para adicionar.")

    paises = Counter(pais for lista in listas.values() for _, pais in lista)
    if max(paises.values()) > len(NOMES_GRUPOS):
        raise ValueError("Há mais de 8 clubes do mesmo país: sorteio impossível.")

    for _ in range(5000):  # se o sorteio travar, recomeça (com limite de tentativas)
        grupos = [[] for _ in NOMES_GRUPOS]
        passos = []
        deu_certo = True

        for pote in (1, 2, 3, 4):
            clubes = listas[pote][:]      # copia para não alterar o original
            random.shuffle(clubes)        # ordem aleatória = "tirar a bola"
            grupos_usados = set()         # grupos que já receberam clube deste pote

            for clube in clubes:
                nome, pais = clube
                # grupos possíveis: ainda sem clube deste pote
                # e sem nenhum clube do mesmo país
                candidatos = [
                    g for g in range(len(grupos))
                    if g not in grupos_usados
                    and all(pais != outro_pais for _, outro_pais in grupos[g])
                ]
                if not candidatos:        # beco sem saída: refaz tudo
                    deu_certo = False
                    break
                g = random.choice(candidatos)
                grupos[g].append(clube)
                grupos_usados.add(g)
                passos.append((pote, clube, g))

            if not deu_certo:
                break

        if deu_certo:
            return passos

    raise ValueError("Não foi possível sortear com esses times.")


def gerar_jogos(clubes):
    """
    Recebe os 4 clubes de um grupo e devolve as 6 rodadas (turno e returno).
    Cada rodada é uma lista com 2 jogos; cada jogo é (indice_casa, indice_fora).
    Método do "círculo": o clube 0 fica fixo e os outros giram.
    """
    ordem = [0, 1, 2, 3]
    ida = []
    for _ in range(3):
        ida.append([(ordem[0], ordem[3]), (ordem[1], ordem[2])])
        ordem = [ordem[0], ordem[3], ordem[1], ordem[2]]   # gira
    volta = [[(fora, casa) for casa, fora in rodada] for rodada in ida]  # inverte o mando
    return ida + volta


def calcular_tabela(resultados, quantidade=4):
    """
    Monta a classificação de um grupo.
    'resultados' é uma lista de (casa, fora, gols_casa, gols_fora) dos jogos
    já preenchidos. Devolve [(indice_do_clube, estatisticas), ...] ordenado por
    pontos, saldo de gols, gols pró e, por fim, pela ordem do sorteio.
    """
    linhas = {i: {"pts": 0, "j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0}
              for i in range(quantidade)}

    for casa, fora, gols_casa, gols_fora in resultados:
        for clube, pro, contra in ((casa, gols_casa, gols_fora),
                                   (fora, gols_fora, gols_casa)):
            linha = linhas[clube]
            linha["j"] += 1
            linha["gp"] += pro
            linha["gc"] += contra
            if pro > contra:
                linha["v"] += 1
                linha["pts"] += 3
            elif pro == contra:
                linha["e"] += 1
                linha["pts"] += 1
            else:
                linha["d"] += 1

    for linha in linhas.values():
        linha["sg"] = linha["gp"] - linha["gc"]

    ordem = sorted(range(quantidade),
                   key=lambda i: (-linhas[i]["pts"], -linhas[i]["sg"], -linhas[i]["gp"], i))
    return [(i, linhas[i]) for i in ordem]


# =====================================================================
# 4) COMPONENTES VISUAIS
# =====================================================================
class Botao(tk.Label):
    """Label com cara de botão, porque o tk.Button ignora cores no macOS."""

    def __init__(self, pai, texto, comando, cor=None):
        cor = cor or DESTAQUE
        fg = FUNDO if cor == DESTAQUE else BRANCO     # texto escuro sobre a cor de destaque
        super().__init__(pai, text=texto, bg=cor, fg=fg,
                         font=("Helvetica", 13, "bold"),
                         padx=24, pady=10, cursor="hand2")
        self.cor = cor
        self.fg_normal = fg
        self.comando = comando
        self.ativo = True
        self.bind("<Button-1>", self._clicar)
        self.bind("<Enter>", self._entrar)
        self.bind("<Leave>", self._sair)

    def _clicar(self, _evento):
        if self.ativo:
            self.comando()

    def _entrar(self, _evento):
        if self.ativo:
            self.config(bg=DESTAQUE_CLARO, fg=FUNDO)

    def _sair(self, _evento):
        self.config(bg=self.cor if self.ativo else CINZA,
                    fg=self.fg_normal if self.ativo else BRANCO)

    def definir_ativo(self, ativo):
        self.ativo = ativo
        self.config(bg=self.cor if ativo else CINZA,
                    fg=self.fg_normal if ativo else BRANCO,
                    cursor="hand2" if ativo else "arrow")


class SlotPote(tk.Frame):
    """
    Uma linha de clube dentro de um pote.
    - Com clube: clicar no nome edita o clube; ao passar o mouse aparece
      um ✕ vermelho para tirar o time.
    - Vazia: mostra "vazio" e um + azul para colocar outro time.
    """

    def __init__(self, pai, app, pote, indice):
        super().__init__(pai, bg=CARTAO)
        self.app = app
        self.pote = pote
        self.indice = indice
        self.clube = None

        self.nome = tk.Label(self, bg=CARTAO, fg=BRANCO, font=app.f_pote,
                             anchor="w", cursor="hand2")
        self.acao = tk.Label(self, text="✕", bg=CARTAO, fg=CARTAO, width=2,
                             font=("Helvetica", 11, "bold"), cursor="hand2")
        self.nome.pack(side="left")
        self.acao.pack(side="left")

        # o mouse "entra/sai" de cada pedaço, então escutamos todos
        for parte in (self, self.nome, self.acao):
            parte.bind("<Enter>", self._entrar)
            parte.bind("<Leave>", self._sair)
        self.acao.bind("<Button-1>", self._clicar_acao)
        self.nome.bind("<Button-1>", self._clicar_nome)

    def atualizar(self, clube):
        """Mostra o clube (ou o estado vazio) e tira qualquer risco de 'já sorteado'."""
        self.clube = clube
        if clube:
            self.nome.config(text=clube[0], fg=BRANCO, font=self.app.f_pote)
            self.acao.config(text="✕", fg=CARTAO)          # escondido até o mouse chegar
        else:
            self.nome.config(text="vazio", fg=CINZA, font=self.app.f_pote)
            self.acao.config(text="+", fg=DESTAQUE)

    def marcar_sorteado(self):
        self.nome.config(fg=CINZA, font=self.app.f_pote_usado)

    def centro_x(self):
        return self.nome.winfo_rootx() + self.nome.winfo_width() // 2

    # ---------- mouse ----------
    def _entrar(self, _evento):
        if self.clube:
            self.acao.config(fg=VERMELHO)

    def _sair(self, _evento):
        # Ao passar de um pedaço para outro da linha o Tk dispara "Leave";
        # só esconde o ✕ se o mouse realmente saiu da linha inteira.
        sob_o_mouse = self.winfo_containing(*self.winfo_pointerxy())
        while sob_o_mouse is not None:
            if sob_o_mouse is self:
                return
            sob_o_mouse = getattr(sob_o_mouse, "master", None)
        if self.clube:
            self.acao.config(fg=CARTAO)

    def _clicar_acao(self, _evento):
        if self.clube:
            self.app.remover(self.pote, self.indice)
        else:
            self.app.adicionar(self.pote, self.indice)

    def _clicar_nome(self, _evento):
        if self.clube:
            self.app.editar(self.pote, self.indice)
        else:
            self.app.adicionar(self.pote, self.indice)


class DialogoClube(tk.Toplevel):
    """
    Janelinha para digitar o nome e a sigla do país de um clube.
    Se 'atual' vier preenchido, ela serve para EDITAR esse clube.
    """

    def __init__(self, pai, nomes_existentes, pote, atual=None):
        super().__init__(pai, bg=CARTAO, padx=24, pady=18)
        editando = atual is not None
        self.title(f"{'Editar' if editando else 'Novo'} clube · Pote {pote}")
        self.resizable(False, False)
        self.transient(pai)
        self.resultado = None            # vira (nome, pais) se o usuário confirmar
        self.existentes = nomes_existentes

        titulo = f"EDITAR CLUBE · POTE {pote}" if editando else f"ADICIONAR AO POTE {pote}"
        tk.Label(self, text=titulo, bg=CARTAO, fg=DESTAQUE,
                 font=("Helvetica", 13, "bold")).grid(row=0, column=0, columnspan=2,
                                                      sticky="w", pady=(0, 10))
        self.e_nome = self._campo("Clube", 1)
        self.e_pais = self._campo("País (sigla)", 2)
        if editando:
            self.e_nome.insert(0, atual[0])
            self.e_pais.insert(0, atual[1])
            self.e_nome.select_range(0, "end")

        self.erro = tk.Label(self, text="", bg=CARTAO, fg=VERMELHO, font=("Helvetica", 11))
        self.erro.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        botoes = tk.Frame(self, bg=CARTAO)
        botoes.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))
        Botao(botoes, "Cancelar", self.destroy, BOTAO2).pack(side="left", padx=(0, 8))
        Botao(botoes, "Salvar" if editando else "Adicionar", self._confirmar).pack(side="left")

        self.bind("<Return>", lambda e: self._confirmar())
        self.bind("<Escape>", lambda e: self.destroy())

        # centraliza em cima da janela principal
        self.update_idletasks()
        x = pai.winfo_rootx() + (pai.winfo_width() - self.winfo_reqwidth()) // 2
        y = pai.winfo_rooty() + (pai.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{x}+{y}")

        self.e_nome.focus_set()
        self.wait_visibility()
        self.grab_set()                  # trava a janela de trás até fechar

    def _campo(self, rotulo, linha):
        tk.Label(self, text=rotulo, bg=CARTAO, fg=PRATA,
                 font=("Helvetica", 12)).grid(row=linha, column=0, sticky="w", pady=4)
        entrada = tk.Entry(self, font=("Helvetica", 13), width=22, bg=BRANCO, fg=FUNDO,
                           insertbackground=FUNDO, relief="flat", highlightthickness=2,
                           highlightbackground=BOTAO2, highlightcolor=DESTAQUE)
        entrada.grid(row=linha, column=1, sticky="w", padx=(12, 0), pady=4)
        return entrada

    def _confirmar(self):
        nome = " ".join(self.e_nome.get().split())
        pais = self.e_pais.get().strip().upper()
        if not nome:
            self.erro.config(text="Digite o nome do clube.")
        elif len(nome) > 22:
            self.erro.config(text="Nome muito grande (máximo 22 letras).")
        elif nome.lower() in self.existentes:
            self.erro.config(text="Esse clube já está nos potes.")
        elif not (2 <= len(pais) <= 3 and pais.isalpha()):
            self.erro.config(text="Use a sigla do país (ex.: BRA, ESP).")
        else:
            self.resultado = (nome, pais)
            self.destroy()


# =====================================================================
# 5) JANELA PRINCIPAL
# =====================================================================
class SorteioApp:
    def __init__(self, root):
        self.root = root
        root.geometry("1320x780")
        root.minsize(1200, 700)

        # fontes (guardadas em self para o Tkinter não descartá-las)
        self.f_pote = tkfont.Font(family="Helvetica", size=10)
        self.f_pote_usado = tkfont.Font(family="Helvetica", size=10, overstrike=True)
        self.f_slot = tkfont.Font(family="Helvetica", size=11, weight="bold")

        self.competicao = "Champions League"
        self.potes_por_comp = {}   # cada competição guarda os seus potes editados
        self.potes = {}

        self.passos = []
        self.indice = 0
        self.auto = False          # "Sortear tudo" em andamento?
        self.after_id = None       # temporizador do modo automático
        self.slots_pote = {}       # (pote, posição) -> SlotPote
        self.por_nome = {}         # nome do clube -> SlotPote
        self.slots = {}            # (grupo, pote) -> Label no grupo

        # janela de jogos / placar
        self.janela_jogos = None
        self.vars_placar = {}      # (grupo, rodada, jogo) -> (gols casa, gols fora)
        self.grupos_sorteados = []
        self.jogos_grupo = []
        self.grupo_aberto = 0
        self._lote = False         # True enquanto preenche vários placares de uma vez

        self.construir_tudo()

    # =================================================================
    # CONSTRUÇÃO DA TELA
    # =================================================================
    def construir_tudo(self):
        """Desenha a tela inteira com as cores e os potes da competição atual."""
        self.cancelar_timers()
        self.fechar_jogos()
        for filho in self.root.winfo_children():
            filho.destroy()

        comp = COMPETICOES[self.competicao]
        aplicar_tema(comp["tema"])
        self.root.configure(bg=FUNDO)
        self.root.title(f"{comp['titulo']} - Sorteio")

        if self.competicao not in self.potes_por_comp:
            base = comp["potes"]
            self.potes_por_comp[self.competicao] = {
                p: (list(base.get(p, [])) + [None] * TAMANHO_POTE)[:TAMANHO_POTE]
                for p in (1, 2, 3, 4)
            }
        self.potes = self.potes_por_comp[self.competicao]

        self.slots_pote = {}
        self.slots = {}
        self.por_nome = {}

        self.construir_cabecalho()
        self.construir_potes()
        self.construir_controles()     # antes dos grupos, para nunca ficar cortado
        self.construir_grupos()
        self.reiniciar()

    def trocar_competicao(self, nome):
        if nome != self.competicao:
            self.competicao = nome
            self.construir_tudo()

    # ---------- cabeçalho: título e seletor de competição ----------
    def construir_cabecalho(self):
        topo = tk.Frame(self.root, bg=FUNDO)
        topo.pack(fill="x", pady=(12, 4))
        tk.Label(topo, text=f"★  {COMPETICOES[self.competicao]['titulo']}  ★", bg=FUNDO,
                 fg=BRANCO, font=("Helvetica", 28, "bold")).pack()
        tk.Label(topo, text="SORTEIO DA FASE DE GRUPOS", bg=FUNDO, fg=DESTAQUE,
                 font=("Helvetica", 13, "bold")).pack()

        seletor = tk.Frame(topo, bg=FUNDO)
        seletor.pack(pady=(8, 0))
        for nome in COMPETICOES:
            ativa = nome == self.competicao
            pilula = tk.Label(seletor, text=nome, bg=DESTAQUE if ativa else CARTAO,
                              fg=FUNDO if ativa else PRATA, font=("Helvetica", 11, "bold"),
                              padx=14, pady=5, cursor="hand2")
            pilula.pack(side="left", padx=4)
            # after: troca a competição só depois do clique terminar
            pilula.bind("<Button-1>",
                        lambda e, n=nome: self.root.after(1, self.trocar_competicao, n))
            if not ativa:
                pilula.bind("<Enter>", lambda e, p=pilula: p.config(bg=BOTAO2))
                pilula.bind("<Leave>", lambda e, p=pilula: p.config(bg=CARTAO))

    # ---------- faixa com os 4 potes ----------
    def construir_potes(self):
        faixa = tk.Frame(self.root, bg=FUNDO)
        faixa.pack(fill="x", padx=20, pady=(10, 0))
        for c in range(4):
            faixa.columnconfigure(c, weight=1, uniform="potes")

        for pote in (1, 2, 3, 4):
            cartao = tk.Frame(faixa, bg=CARTAO, padx=10, pady=8)
            cartao.grid(row=0, column=pote - 1, padx=6, sticky="nsew")
            tk.Label(cartao, text=f"POTE {pote}", bg=CARTAO, fg=DESTAQUE,
                     font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
            # 8 posições em 2 colunas de 4 linhas
            for i in range(TAMANHO_POTE):
                slot = SlotPote(cartao, self, pote, i)
                slot.grid(row=1 + i % 4, column=i // 4, sticky="w", padx=(0, 8))
                self.slots_pote[(pote, i)] = slot

    # ---------- grade com os 8 grupos ----------
    def construir_grupos(self):
        grade = tk.Frame(self.root, bg=FUNDO)
        grade.pack(fill="both", expand=True, padx=20, pady=6)
        for c in range(4):
            grade.columnconfigure(c, weight=1, uniform="grupos")
        for r in range(2):
            grade.rowconfigure(r, weight=1, uniform="linhas")

        for g, letra in enumerate(NOMES_GRUPOS):
            cartao = tk.Frame(grade, bg=CARTAO)
            cartao.grid(row=g // 4, column=g % 4, padx=6, pady=6, sticky="nsew")
            tk.Label(cartao, text=f"GRUPO {letra}", bg=DESTAQUE, fg=FUNDO,
                     font=("Helvetica", 12, "bold"), pady=4).pack(fill="x")
            for pote in (1, 2, 3, 4):
                slot = tk.Label(cartao, text=f"P{pote}  ·  —", bg=CARTAO, fg=CINZA,
                                font=self.f_slot, anchor="w", padx=12, pady=5)
                slot.pack(fill="x")
                self.slots[(g, pote)] = slot

    # ---------- barra inferior: status e botões ----------
    def construir_controles(self):
        barra = tk.Frame(self.root, bg=FUNDO)
        barra.pack(side="bottom", fill="x", padx=20, pady=(4, 16))

        self.status = tk.StringVar()
        tk.Label(barra, textvariable=self.status, bg=FUNDO, fg=PRATA,
                 font=("Helvetica", 14)).pack(side="left")

        self.btn_reiniciar = Botao(barra, "Reiniciar", self.reiniciar, BOTAO2)
        self.btn_reiniciar.pack(side="right", padx=(10, 0))
        self.btn_jogos = Botao(barra, "Jogos e tabela", self.abrir_jogos, BOTAO2)
        self.btn_jogos.pack(side="right", padx=(10, 0))
        self.btn_tudo = Botao(barra, "Sortear tudo", self.sortear_tudo, BOTAO2)
        self.btn_tudo.pack(side="right", padx=(10, 0))
        self.btn_proximo = Botao(barra, "Sortear próxima bola", self.proximo_passo)
        self.btn_proximo.pack(side="right")

    # =================================================================
    # EDIÇÃO DOS POTES
    # =================================================================
    def remover(self, pote, indice):
        """O ✕: deixa a posição vazia e reinicia o sorteio."""
        self.potes[pote][indice] = None
        self.reiniciar()

    def adicionar(self, pote, indice):
        """O +: abre a janelinha e coloca o clube novo naquela posição."""
        dialogo = DialogoClube(self.root, self._nomes_nos_potes(), pote)
        self.root.wait_window(dialogo)
        if dialogo.resultado:
            self.potes[pote][indice] = dialogo.resultado
            self.reiniciar(f"{dialogo.resultado[0]} entrou no Pote {pote}. Sorteio reiniciado.")

    def editar(self, pote, indice):
        """Clicar no nome: abre a janelinha já preenchida para corrigir nome ou país."""
        atual = self.potes[pote][indice]
        outros = self._nomes_nos_potes() - {atual[0].lower()}   # o próprio nome pode ficar
        dialogo = DialogoClube(self.root, outros, pote, atual)
        self.root.wait_window(dialogo)
        if dialogo.resultado and dialogo.resultado != atual:
            self.potes[pote][indice] = dialogo.resultado
            nome, pais = dialogo.resultado
            self.reiniciar(f"Clube atualizado: {nome} ({pais}). Sorteio reiniciado.")

    def _nomes_nos_potes(self):
        return {c[0].lower() for lista in self.potes.values() for c in lista if c}

    def refrescar_potes(self):
        """Redesenha os 4 potes a partir dos dados."""
        self.por_nome = {}
        for (pote, i), slot in self.slots_pote.items():
            clube = self.potes[pote][i]
            slot.atualizar(clube)
            if clube:
                self.por_nome[clube[0]] = slot

    # =================================================================
    # AÇÕES DO SORTEIO
    # =================================================================
    def cancelar_timers(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = None
        self.auto = False

    def reiniciar(self, aviso=None):
        """Cancela animações, gera um sorteio novo e limpa a tela."""
        self.cancelar_timers()
        self.indice = 0
        self.fechar_jogos()
        self.vars_placar = {}          # placares antigos não valem para um sorteio novo

        self.refrescar_potes()
        for (g, pote), slot in self.slots.items():
            slot.config(text=f"P{pote}  ·  —", fg=CINZA, bg=CARTAO)

        try:
            self.passos = realizar_sorteio(self.potes)
            self.status.set(aviso or "Pronto! Clique em “Sortear próxima bola”.")
        except ValueError as erro:     # potes incompletos ou sorteio impossível
            self.passos = []
            self.status.set(str(erro))
        self.atualizar_botoes()

    def proximo_passo(self):
        """Revela UM clube: tira do pote e coloca no grupo sorteado."""
        if self.indice >= len(self.passos):
            return False
        pote, (nome, pais), g = self.passos[self.indice]
        self.indice += 1

        # no pote: clube fica apagado e riscado
        self.por_nome[nome].marcar_sorteado()

        # no grupo: escreve o clube e faz o slot piscar
        slot = self.slots[(g, pote)]
        slot.config(text=f"P{pote}  ·  {nome}  ({pais})", fg=BRANCO)
        self.piscar(slot)

        terminou = self.indice == len(self.passos)
        if terminou:
            self.status.set("★ Sorteio concluído! Clique em “Jogos e tabela”. ★")
        else:
            self.status.set(f"{nome}  →  Grupo {NOMES_GRUPOS[g]}")

        if self.auto:                  # modo "Sortear tudo": agenda o próximo clube
            if terminou:
                self.auto = False
            else:
                self.after_id = self.root.after(300, self._passo_automatico)
        self.atualizar_botoes()
        return True

    def sortear_tudo(self):
        """Roda os passos restantes sozinho, com uma pausa entre eles."""
        if self.auto:
            return
        self.auto = True
        self.atualizar_botoes()
        self._passo_automatico()

    def _passo_automatico(self):
        self.after_id = None
        if not self.auto:
            return
        if not self.proximo_passo():
            self.auto = False
            self.atualizar_botoes()

    def piscar(self, widget, vezes=6):
        """Efeito visual: alterna a cor de fundo do slot algumas vezes."""
        try:
            if vezes == 0:
                widget.config(bg=CARTAO)
                return
            widget.config(bg=PISCA if vezes % 2 == 0 else CARTAO)
            self.root.after(120, self.piscar, widget, vezes - 1)
        except tk.TclError:            # a tela foi redesenhada no meio da piscada
            pass

    def atualizar_botoes(self):
        """Liga/desliga os botões conforme o estado do sorteio."""
        livre = not self.auto
        tem_passos = self.indice < len(self.passos)
        terminou = bool(self.passos) and self.indice == len(self.passos)
        self.btn_proximo.definir_ativo(livre and tem_passos)
        self.btn_tudo.definir_ativo(livre and tem_passos)
        self.btn_jogos.definir_ativo(terminou)

    # =================================================================
    # JOGOS, PLACARES E CLASSIFICAÇÃO
    # =================================================================
    def fechar_jogos(self):
        if self.janela_jogos is not None:
            try:
                self.janela_jogos.destroy()
            except tk.TclError:
                pass
            self.janela_jogos = None

    def abrir_jogos(self):
        """Abre a janela onde o usuário digita os placares e vê a classificação."""
        if not self.btn_jogos.ativo:
            return
        self.fechar_jogos()

        # os grupos saem dos passos (já na ordem dos potes); os jogos, de gerar_jogos
        self.grupos_sorteados = [[] for _ in NOMES_GRUPOS]
        for _pote, clube, g in self.passos:
            self.grupos_sorteados[g].append(clube)
        self.jogos_grupo = [gerar_jogos(clubes) for clubes in self.grupos_sorteados]

        # um par de "caixinhas" de gols para cada jogo (mantidas enquanto o sorteio valer)
        if not self.vars_placar:
            for g in range(len(NOMES_GRUPOS)):
                for r in range(6):
                    for j in range(2):
                        gols = (tk.StringVar(self.root), tk.StringVar(self.root))
                        for var in gols:
                            var.trace_add("write", self._placar_mudou)
                        self.vars_placar[(g, r, j)] = gols

        janela = tk.Toplevel(self.root)
        janela.title("Jogos e classificação")
        janela.configure(bg=FUNDO)
        janela.geometry("1320x800")
        janela.protocol("WM_DELETE_WINDOW", self.fechar_jogos)
        self.janela_jogos = janela
        self._vcmd = (janela.register(self._valida_gol), "%P")
        self.grupo_aberto = 0

        tk.Label(janela, text="JOGOS E CLASSIFICAÇÃO", bg=FUNDO, fg=BRANCO,
                 font=("Helvetica", 22, "bold")).pack(pady=(12, 0))
        tk.Label(janela, text="Digite os placares ou use “Simular resultados”. "
                              "Desempate: pontos, saldo de gols e gols pró.",
                 bg=FUNDO, fg=DESTAQUE, font=("Helvetica", 12, "bold")).pack()

        # faixa dos classificados (embaixo) é empacotada antes para nunca ser cortada
        self.frame_classificados = tk.Frame(janela, bg=FUNDO)
        self.frame_classificados.pack(side="bottom", fill="x", padx=16, pady=(0, 14))

        # abas dos grupos + botões
        barra = tk.Frame(janela, bg=FUNDO)
        barra.pack(fill="x", padx=16, pady=(12, 6))
        self.abas = []
        for g, letra in enumerate(NOMES_GRUPOS):
            aba = tk.Label(barra, text=letra, font=("Helvetica", 13, "bold"),
                           width=5, pady=6, cursor="hand2")
            aba.pack(side="left", padx=3)
            aba.bind("<Button-1>", lambda e, g=g: self.mostrar_grupo(g))
            self.abas.append(aba)
        Botao(barra, "Limpar placares", self.limpar_placares, BOTAO2).pack(side="right", padx=(8, 0))
        Botao(barra, "Simular resultados", self.simular_resultados).pack(side="right")

        corpo = tk.Frame(janela, bg=FUNDO)
        corpo.pack(fill="both", expand=True, padx=16, pady=4)
        corpo.columnconfigure(1, weight=1)
        self.frame_jogos = tk.Frame(corpo, bg=FUNDO)
        self.frame_jogos.grid(row=0, column=0, sticky="n")
        self.frame_tabela = tk.Frame(corpo, bg=CARTAO, padx=14, pady=12)
        self.frame_tabela.grid(row=0, column=1, padx=(12, 0), sticky="n")

        self.mostrar_grupo(0)

    def _valida_gol(self, novo_texto):
        """Só deixa digitar números (até 2 dígitos) nas caixinhas de gols."""
        return novo_texto == "" or (novo_texto.isascii() and novo_texto.isdigit()
                                    and len(novo_texto) <= 2)

    def _placar_mudou(self, *_args):
        """Chamada a cada gol digitado: recalcula as tabelas na hora."""
        if not self._lote and self.janela_jogos is not None:
            self.atualizar_tabelas()

    def resultados_do_grupo(self, g):
        """Lista (casa, fora, gols_casa, gols_fora) dos jogos já preenchidos."""
        lista = []
        for r, rodada in enumerate(self.jogos_grupo[g]):
            for j, (casa, fora) in enumerate(rodada):
                gols_casa, gols_fora = self.vars_placar[(g, r, j)]
                if gols_casa.get() != "" and gols_fora.get() != "":
                    lista.append((casa, fora, int(gols_casa.get()), int(gols_fora.get())))
        return lista

    def mostrar_grupo(self, g):
        self.grupo_aberto = g
        self.desenhar_jogos(g)
        self.atualizar_tabelas()

    def atualizar_tabelas(self):
        self.desenhar_tabela(self.grupo_aberto)
        self.desenhar_classificados()
        for g, aba in enumerate(self.abas):
            completo = len(self.resultados_do_grupo(g)) == JOGOS_POR_GRUPO
            ativa = g == self.grupo_aberto
            aba.config(text=f"{NOMES_GRUPOS[g]} ✓" if completo else NOMES_GRUPOS[g],
                       bg=DESTAQUE if ativa else BOTAO2,
                       fg=FUNDO if ativa else BRANCO)

    def _entrada_gol(self, pai, variavel):
        return tk.Entry(pai, textvariable=variavel, width=3, justify="center",
                        font=("Helvetica", 13, "bold"), bg=BRANCO, fg=FUNDO,
                        insertbackground=FUNDO, relief="flat", highlightthickness=2,
                        highlightbackground=BOTAO2, highlightcolor=DESTAQUE,
                        validate="key", validatecommand=self._vcmd)

    def desenhar_jogos(self, g):
        """Os 12 jogos do grupo, com as caixinhas de gols."""
        for w in self.frame_jogos.winfo_children():
            w.destroy()
        clubes = self.grupos_sorteados[g]

        for coluna, titulo in enumerate(("TURNO (IDA)", "RETURNO (VOLTA)")):
            bloco = tk.Frame(self.frame_jogos, bg=CARTAO, padx=12, pady=10)
            bloco.grid(row=0, column=coluna, padx=6, sticky="n")
            tk.Label(bloco, text=titulo, bg=CARTAO, fg=DESTAQUE,
                     font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=5, sticky="w")
            linha = 1
            for r in range(coluna * 3, coluna * 3 + 3):
                tk.Label(bloco, text=f"RODADA {r + 1}", bg=CARTAO, fg=PRATA,
                         font=("Helvetica", 10, "bold")).grid(row=linha, column=0, columnspan=5,
                                                              sticky="w", pady=(10, 2))
                linha += 1
                for j, (casa, fora) in enumerate(self.jogos_grupo[g][r]):
                    gols_casa, gols_fora = self.vars_placar[(g, r, j)]
                    tk.Label(bloco, text=clubes[casa][0], bg=CARTAO, fg=BRANCO,
                             font=("Helvetica", 11), anchor="e").grid(row=linha, column=0,
                                                                      sticky="e", pady=3)
                    self._entrada_gol(bloco, gols_casa).grid(row=linha, column=1, padx=(8, 2))
                    tk.Label(bloco, text="x", bg=CARTAO, fg=PRATA,
                             font=("Helvetica", 11, "bold")).grid(row=linha, column=2)
                    self._entrada_gol(bloco, gols_fora).grid(row=linha, column=3, padx=(2, 8))
                    tk.Label(bloco, text=clubes[fora][0], bg=CARTAO, fg=BRANCO,
                             font=("Helvetica", 11), anchor="w").grid(row=linha, column=4,
                                                                      sticky="w")
                    linha += 1

    def desenhar_tabela(self, g):
        """A tabela de pontos do grupo aberto."""
        for w in self.frame_tabela.winfo_children():
            w.destroy()
        clubes = self.grupos_sorteados[g]
        resultados = self.resultados_do_grupo(g)
        completo = len(resultados) == JOGOS_POR_GRUPO

        tk.Label(self.frame_tabela, text=f"CLASSIFICAÇÃO · GRUPO {NOMES_GRUPOS[g]}",
                 bg=CARTAO, fg=DESTAQUE, font=("Helvetica", 12, "bold")).grid(
                     row=0, column=0, columnspan=10, sticky="w", pady=(0, 8))

        for c, titulo in enumerate(("#", "Clube", "P", "J", "V", "E", "D", "GP", "GC", "SG")):
            tk.Label(self.frame_tabela, text=titulo, bg=DESTAQUE, fg=FUNDO,
                     font=("Helvetica", 10, "bold"), width=4 if c != 1 else 18,
                     anchor="w" if c == 1 else "center").grid(row=1, column=c, sticky="ew")

        for posicao, (i, linha) in enumerate(calcular_tabela(resultados), start=1):
            classificado = completo and posicao <= 2
            fundo = PISCA if classificado else CARTAO
            saldo = f"{linha['sg']:+d}" if linha["sg"] else "0"
            valores = (posicao, clubes[i][0], linha["pts"], linha["j"], linha["v"],
                       linha["e"], linha["d"], linha["gp"], linha["gc"], saldo)
            for c, valor in enumerate(valores):
                destaque = c in (1, 2)       # nome e pontos em negrito
                tk.Label(self.frame_tabela, text=str(valor), bg=fundo,
                         fg=BRANCO if classificado or destaque else PRATA,
                         font=("Helvetica", 11, "bold" if destaque else "normal"),
                         anchor="w" if c == 1 else "center", pady=4).grid(
                             row=1 + posicao, column=c, sticky="ew")

        legenda = ("Os 2 primeiros (em destaque) estão classificados."
                   if completo else f"{len(resultados)} de {JOGOS_POR_GRUPO} jogos preenchidos.")
        tk.Label(self.frame_tabela, text=legenda, bg=CARTAO, fg=PRATA,
                 font=("Helvetica", 10)).grid(row=6, column=0, columnspan=10,
                                              sticky="w", pady=(10, 0))

    def desenhar_classificados(self):
        """Faixa de baixo: os 2 primeiros de cada grupo que já terminou."""
        for w in self.frame_classificados.winfo_children():
            w.destroy()
        tk.Label(self.frame_classificados, text="CLASSIFICADOS (2 primeiros de cada grupo)",
                 bg=FUNDO, fg=DESTAQUE, font=("Helvetica", 12, "bold")).grid(
                     row=0, column=0, columnspan=len(NOMES_GRUPOS), sticky="w", pady=(0, 4))
        for g, letra in enumerate(NOMES_GRUPOS):
            self.frame_classificados.columnconfigure(g, weight=1, uniform="class")
            resultados = self.resultados_do_grupo(g)
            if len(resultados) == JOGOS_POR_GRUPO:
                tabela = calcular_tabela(resultados)
                primeiro = f"1º {self.grupos_sorteados[g][tabela[0][0]][0]}"
                segundo = f"2º {self.grupos_sorteados[g][tabela[1][0]][0]}"
                cor = BRANCO
            else:
                primeiro, segundo, cor = "1º —", "2º —", CINZA
            cartao = tk.Frame(self.frame_classificados, bg=CARTAO, padx=8, pady=4)
            cartao.grid(row=1, column=g, padx=3, sticky="nsew")
            tk.Label(cartao, text=f"GRUPO {letra}", bg=CARTAO, fg=DESTAQUE,
                     font=("Helvetica", 10, "bold")).pack(anchor="w")
            tk.Label(cartao, text=primeiro, bg=CARTAO, fg=cor,
                     font=("Helvetica", 10), anchor="w").pack(fill="x")
            tk.Label(cartao, text=segundo, bg=CARTAO, fg=cor,
                     font=("Helvetica", 10), anchor="w").pack(fill="x")

    def simular_resultados(self):
        """Preenche TODOS os placares com gols aleatórios."""
        self._lote = True              # evita recalcular a cada gol
        for gols_casa, gols_fora in self.vars_placar.values():
            gols_casa.set(str(random.choices(GOLS_POSSIVEIS, GOLS_PESOS)[0]))
            gols_fora.set(str(random.choices(GOLS_POSSIVEIS, GOLS_PESOS)[0]))
        self._lote = False
        self.atualizar_tabelas()

    def limpar_placares(self):
        self._lote = True
        for gols_casa, gols_fora in self.vars_placar.values():
            gols_casa.set("")
            gols_fora.set("")
        self._lote = False
        self.atualizar_tabelas()


# =====================================================================
# 6) PONTO DE ENTRADA
# =====================================================================
if __name__ == "__main__":
    janela = tk.Tk()
    SorteioApp(janela)
    janela.mainloop()

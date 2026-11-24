README · MD
⚽ Sorteador da Champions League

Simulador do sorteio da fase de grupos feito em Python com interface gráfica em Tkinter.

Aluno: Ruan Henrique
Cadeira: Programação 1
Instituição: Universidade Federal Rural de Pernambuco (UFRPE)

📌 Sobre o projeto

O programa sorteia 32 clubes, divididos em 4 potes de 8, em 8 grupos de 4 (A a H). Depois do sorteio, ele gera os jogos de cada grupo, deixa o usuário digitar os placares, calcula a classificação e mostra os dois classificados de cada grupo.

Há duas competições, escolhidas por botões no topo da tela:

Champions League: lista de exemplo com 32 clubes (não é o sorteio oficial).
Personalizada: começa com os potes vazios para o usuário montar o próprio campeonato.
✨ Funcionalidades
Sorteio clube a clube ou completo (Sortear tudo)
Regras: um clube de cada pote por grupo e nenhum grupo com dois clubes do mesmo país
Edição dos times na tela: ✕ para tirar, + para colocar e clique no nome para corrigir
Jogos de cada grupo (turno e returno, 6 rodadas)
Placares digitados pelo usuário, com tabela de classificação atualizada na hora
Botão Simular resultados, que preenche todos os placares aleatoriamente
Lista dos 2 classificados de cada grupo
🚀 Como executar

Requisitos: Python 3.8 ou mais recente. O Tkinter já vem com o Python no Windows e no macOS. No Linux, instale com sudo apt install python3-tk. Não é preciso instalar nenhuma biblioteca externa.

bash
python sorteio_champions_personalizada.py

(em alguns sistemas o comando é python3)

🕹️ Como usar
Sortear: escolha a competição e clique em Sortear próxima bola (um clube por vez) ou em Sortear tudo.
Editar os times: passe o mouse sobre um clube e clique no ✕ para tirar. Numa posição vazia, clique no + e informe o nome e a sigla do país (por exemplo, BRA ou ESP). Clique no nome de um clube para corrigi-lo.
Competição personalizada: clique em Personalizada, preencha os 32 clubes com o + e sorteie.
Jogos e tabela: com o sorteio concluído, clique em Jogos e tabela. Escolha o grupo pelas abas, digite os gols de cada jogo ou use Simular resultados.
Reiniciar: o botão Reiniciar faz um sorteio novo com os mesmos clubes.

⚠️ Qualquer edição nos potes reinicia o sorteio e apaga os placares. Nada é salvo em arquivo: ao fechar o programa, as edições são perdidas.

📐 Regras de pontuação
Vitória: 3 pontos, empate: 1 ponto, derrota: 0.
Desempate, nesta ordem: pontos, saldo de gols, gols pró e ordem do sorteio.
Classificam-se os 2 primeiros de cada grupo.
🗂️ Estrutura do código
Parte	O que faz
COMPETICOES	Dados de cada competição: título, cores e potes
realizar_sorteio()	Faz o sorteio e devolve os passos (pote, clube, grupo)
gerar_jogos()	Gera as 6 rodadas de um grupo
calcular_tabela()	Calcula pontos, saldo e a ordem da classificação
Botao, SlotPote, DialogoClube	Componentes visuais: botão, linha de clube no pote e janelinha de adicionar/editar
SorteioApp	Janela principal: tela, sorteio, edição dos potes e janela de jogos

A lógica (realizar_sorteio, gerar_jogos e calcular_tabela) não usa nada do Tkinter. Ela só recebe dados e devolve resultados, e a interface apenas os mostra na tela.

⚠️ Limitações
A lista da Champions é um exemplo, não o sorteio oficial de uma temporada.
O formato é o de grupos clássico (8 grupos de 4), e não a fase de liga com 36 clubes usada hoje pela UEFA.
O desempate não usa confronto direto.
O número de grupos (8) e de potes (4) é fixo.

👤 Autor
Ruan Henrique · Programação 1 · UFRPE

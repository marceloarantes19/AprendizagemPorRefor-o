import streamlit as st
import numpy as np
import json
import random
import pandas as pd
import time
from typing import List, Tuple, Dict, Optional, Union

# ==========================================
# LÓGICA DO JOGO DA VELHA (TIC-TAC-TOE)
# ==========================================
class TicTacToe:
    """
    Ambiente do Jogo da Velha para treinamento de agentes de Aprendizado por Reforço.
    O tabuleiro é representado por uma lista de 9 posições:
    0 indica vazio, 1 indica Jogador 1 (X), -1 indica Jogador 2 (O).
    """
    def __init__(self):
        self.board = [0] * 9
        self.done = False
        self.winner = None

    def reset(self) -> str:
        """Reinicia o tabuleiro para um novo jogo e retorna o estado inicial."""
        self.board = [0] * 9
        self.done = False
        self.winner = None
        return self.get_state()

    def get_state(self) -> str:
        """
        Retorna o estado atual do tabuleiro como uma string (ex: '0,1,-1,0,0,0,0,0,0').
        Essa string servirá como chave na Tabela Q.
        """
        return ",".join(map(str, self.board))

    def available_actions(self) -> List[int]:
        """Retorna uma lista com os índices (0 a 8) das posições vazias no tabuleiro."""
        return [i for i, x in enumerate(self.board) if x == 0]

    def step(self, action: int, player: int) -> Tuple[str, bool, Optional[int]]:
        """
        Executa uma jogada no tabuleiro.
        
        Parâmetros:
            action (int): A posição escolhida (0 a 8).
            player (int): O jogador atual (1 para 'X', -1 para 'O').
            
        Retorna:
            next_state (str): O estado do tabuleiro após a jogada.
            done (bool): Verdadeiro se o jogo acabou (vitória ou empate).
            winner (int ou None): O vencedor (1, -1) ou 0 para empate. None se não acabou.
        """
        if self.board[action] != 0 or self.done:
            # Jogada inválida, penalidade severa (não deveria acontecer se o agente escolher dentre as available_actions)
            return self.get_state(), True, -player  

        # Aplica a jogada
        self.board[action] = player
        self.check_game_over()
        return self.get_state(), self.done, self.winner

    def check_game_over(self):
        """Verifica se há um vencedor ou se o jogo empatou."""
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Linhas
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Colunas
            [0, 4, 8], [2, 4, 6]             # Diagonais
        ]
        for condition in win_conditions:
            a, b, c = condition
            if self.board[a] != 0 and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                self.done = True
                return
        
        if 0 not in self.board:
            self.winner = 0 # Empate
            self.done = True

# ==========================================
# AGENTES (Q-LEARNING E ALEATÓRIO)
# ==========================================
class RandomAgent:
    """Um agente que joga fazendo movimentos aleatórios."""
    def choose_action(self, available_actions: List[int]) -> int:
        return random.choice(available_actions)

class QLearningAgent:
    """
    Agente inteligente que utiliza o algoritmo Q-Learning.
    Aprende a jogar interagindo com o ambiente.
    """
    def __init__(self, alpha: float = 0.5, gamma: float = 0.9, epsilon: float = 0.1):
        self.q_table: Dict[str, Dict[str, float]] = {} # Dicionário de estados para (dicionário de ações e valores)
        self.alpha = alpha     # Taxa de aprendizado
        self.gamma = gamma     # Fator de desconto (importância das recompensas futuras)
        self.epsilon = epsilon # Taxa de exploração (probabilidade de tomar ação aleatória durante treino)

    def get_q(self, state: str, action: int) -> float:
        """Obtém o valor Q para um estado e ação. Retorna 0.0 se não existir."""
        if state not in self.q_table:
            self.q_table[state] = {}
        str_action = str(action)
        if str_action not in self.q_table[state]:
            self.q_table[state][str_action] = 0.0
        return self.q_table[state][str_action]

    def choose_action(self, state: str, available_actions: List[int], explore: bool = True, player: int = -1) -> int:
        """
        Escolhe uma ação baseada na política epsilon-greedy.
        O Jogador 'O' (player=-1) busca maximizar o valor Q.
        O Jogador 'X' (player=1) busca minimizar o valor Q.
        """
        if explore and random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions) # Exploração
        
        q_values = [self.get_q(state, a) for a in available_actions]
        
        # Explotação: Minimax
        target_q = min(q_values) if player == 1 else max(q_values)
        
        best_actions = [a for a, q in zip(available_actions, q_values) if q == target_q]
        return random.choice(best_actions)

    def learn_episode(self, history: List[Tuple[str, int, int]], ref: float):
        """
        Atualiza a Tabela Q no final do episódio para todas as jogadas de X e O.
        Utiliza as fórmulas de Minimax:
        X (player=1):  Q = Q + alpha * (ref + gamma * min(Q) - Q)
        O (player=-1): Q = Q + alpha * (ref + gamma * max(Q) - Q)
        """
        for state, action, player in history:
            avail = [i for i, x in enumerate(map(int, state.split(','))) if x == 0]
            if not avail:
                target_q = 0.0
            else:
                q_values = [self.get_q(state, a) for a in avail]
                target_q = min(q_values) if player == 1 else max(q_values)
                
            old_q = self.get_q(state, action)
            self.q_table[state][str(action)] = old_q + self.alpha * (ref + self.gamma * target_q - old_q)

    def save_q_table(self, epochs: int = None, reward_win: float = None, reward_draw: float = None, reward_loss: float = None) -> str:
        """Exporta a Tabela Q e os metadados de treinamento como uma string no formato JSON."""
        data = {
            "metadata": {
                "epochs": epochs,
                "alpha": self.alpha,
                "reward_win": reward_win,
                "reward_draw": reward_draw,
                "reward_loss": reward_loss
            },
            "q_table": self.q_table
        }
        return json.dumps(data)

    def load_q_table(self, json_data: str):
        """Carrega a Tabela Q a partir de uma string JSON e retorna os metadados (se existirem)."""
        data = json.loads(json_data)
        if "metadata" in data and "q_table" in data:
            self.q_table = data["q_table"]
            return data["metadata"]
        else:
            self.q_table = data
            return None

# ==========================================
# INTERFACE COM STREAMLIT (UI)
# ==========================================
st.set_page_config(page_title="Treinador Q-Learning | Jogo da Velha", layout="wide", page_icon="🤖")



# Menu lateral para navegação
menu = st.sidebar.selectbox("Escolha um Módulo", ["1. Treinamento e Exportação", "2. Jogar contra o Agente", "3. Arena de Batalha Autônoma"])

if menu == "1. Treinamento e Exportação":
    st.header("⚙️ Configurações de Treinamento")
    st.markdown("Ajuste os hiperparâmetros do algoritmo e defina as recompensas do ambiente.")
    
    agent_name = st.text_input("Nome do Agente", value="Agente_Zero", help="Este nome será usado para salvar o arquivo do cérebro do agente.")
    
    col1, col2 = st.columns(2)
    with col1:
        epochs = st.number_input("Número de Épocas (Partidas)", min_value=100, max_value=100000, value=10000, step=1000)
        alpha = st.slider("Alfa (Taxa de Aprendizagem)", 0.0, 1.0, 0.5, 0.01, help="Velocidade com que o agente aceita a nova informação.")
        gamma = st.slider("Gama (Fator de Desconto)", 0.0, 1.0, float(1.0 - alpha), 0.01, disabled=True, help="Calculado automaticamente como 1 - Alfa")
        epsilon = st.slider("Epsilon (Percentual de jogos aleatórios)", 0.0, 1.0, 0.3, 0.01, help="Probabilidade do agente tentar um movimento aleatório durante o treino.")
    
    with col2:
        reward_win = st.number_input("Reforço para Vitória", value=0.0, step=1.0)
        reward_draw = st.number_input("Reforço para Empate", value=0.0, step=1.0)
        reward_loss = st.number_input("Reforço para Derrota", value=0.0, step=1.0)
        
        st.info("💡 **Dica Didática**: O agente treina alternando quem começa a partida (ora ele joga como X, ora como O) contra um Agente Aleatório.")

    if st.button("🚀 Iniciar Treinamento", type="primary"):
        env = TicTacToe()
        agent = QLearningAgent(alpha=alpha, gamma=gamma, epsilon=epsilon)
        random_opponent = RandomAgent()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        chart_placeholder = st.empty()
        
        # Para montar o gráfico: salvar as taxas em blocos
        block_size = max(1, epochs // 100) # Teremos até 100 pontos no gráfico
        win_rates = []
        draw_rates = []
        loss_rates = []
        epochs_history = []
        
        wins = 0
        draws = 0
        losses = 0
        
        start_time = time.time()
        
        for epoch in range(1, epochs + 1):
            env.reset()
            history = []
            
            # Alterna quem o agente representa (1=X, -1=O)
            agente_como = 1 if epoch % 2 != 0 else -1
            adversario = -1 if agente_como == 1 else 1
            vez = 1 # 1 (X) sempre começa
            primeira_jogada = True
            
            while not env.done:
                avail = env.available_actions()
                state_current = env.get_state()
                
                if primeira_jogada:
                    action_current = random.choice(avail)
                    primeira_jogada = False
                elif vez == agente_como:
                    action_current = agent.choose_action(state_current, avail, explore=True, player=agente_como)
                else:
                    action_current = random_opponent.choose_action(avail)
                    
                env.step(action_current, player=vez)
                history.append((state_current, action_current, vez))
                
                vez = adversario if vez == agente_como else agente_como
                
            # Define o reforço (ref) do episódio na visão absoluta da tabela Q
            if env.winner == -1: # O venceu
                ref = reward_win
                if agente_como == -1: wins += 1
                else: losses += 1
            elif env.winner == 1: # X venceu
                ref = reward_loss
                if agente_como == 1: wins += 1
                else: losses += 1
            else:
                ref = reward_draw
                draws += 1
                
            # Atualiza os valores de X e O
            agent.learn_episode(history, ref)
            
            # Atualização da UI a cada bloco de épocas
            if epoch % block_size == 0 or epoch == epochs:
                win_rate = (wins / block_size) * 100
                draw_rate = (draws / block_size) * 100
                loss_rate = (losses / block_size) * 100
                
                win_rates.append(win_rate)
                draw_rates.append(draw_rate)
                loss_rates.append(loss_rate)
                epochs_history.append(epoch)
                
                # Reseta contadores locais do bloco
                wins = 0
                draws = 0
                losses = 0
                
                progress = epoch / epochs
                progress_bar.progress(progress)
                status_text.text(f"Treinando... Época {epoch}/{epochs} | Vitórias: {win_rate:.1f}% | Empates: {draw_rate:.1f}% | Derrotas: {loss_rate:.1f}%")
                
                # Atualiza o gráfico de linha com as 3 métricas
                df = pd.DataFrame({
                    "Época": epochs_history,
                    "Vitórias (%)": win_rates,
                    "Empates (%)": draw_rates,
                    "Derrotas (%)": loss_rates
                }).set_index("Época")
                
                # O Streamlit mapeia automaticamente colunas diferentes para cores diferentes
                chart_placeholder.line_chart(df)
        
        end_time = time.time()
        st.success(f"🎉 Treinamento concluído em {end_time - start_time:.2f} segundos!")
        
        # Salva na sessão para não perder os dados se a tela recarregar
        st.session_state.trained_q_table_data = agent.save_q_table(
            epochs=epochs, reward_win=reward_win, reward_draw=reward_draw, reward_loss=reward_loss
        )
        
    if "trained_q_table_data" in st.session_state:
        st.divider()
        st.subheader("💾 Exportar Agente")
        st.markdown("Altere o nome do arquivo abaixo, se desejar, antes de baixar:")
        file_name_input = st.text_input("Nome do arquivo (sem .json):", value=agent_name, key="filename_input")
        
        # Garante que o nome do arquivo tenha a extensão .json
        safe_filename = file_name_input if file_name_input.endswith('.json') else f"{file_name_input}.json"
        
        st.download_button(
            label="💾 Baixar Tabela Q (Cérebro do Agente)",
            data=st.session_state.trained_q_table_data,
            file_name=safe_filename,
            mime="application/json",
            help="Salve o JSON na sua máquina para usar na Arena de Batalha."
        )

elif menu == "3. Arena de Batalha Autônoma":
    st.header("⚔️ Arena Autônoma: Batalha dos Agentes")
    st.markdown("Faça o upload de dois 'cérebros' (arquivos JSON) gerados no módulo de treinamento e veja qual agente é mais inteligente!")
    
    col1, col2 = st.columns(2)
    with col1:
        file_a = st.file_uploader("Upload Agente A (Jogador 'X')", type=['json'])
    with col2:
        file_b = st.file_uploader("Upload Agente B (Jogador 'O')", type=['json'])
        
    num_matches = st.selectbox("Quantidade de Partidas do Torneio", [5, 10, 15, 20, 25, 50, 75, 100, 200])
    
    # Função para renderizar o tabuleiro em HTML/CSS
    def render_board(board_array):
        symbols = {0: "", 1: "X", -1: "O"}
        colors = {1: "#E74C3C", -1: "#3498DB", 0: "#ECF0F1"}
        html = "<div style='display: grid; grid-template-columns: repeat(3, 80px); gap: 5px; justify-content: center;'>"
        for cell in board_array:
            html += f"<div style='width: 80px; height: 80px; background-color: #2C3E50; display: flex; align-items: center; justify-content: center; font-size: 40px; font-weight: bold; border-radius: 10px; color: {colors[cell]};'>{symbols[cell]}</div>"
        html += "</div><br>"
        return html

    if st.button("⚔️ Iniciar Torneio", type="primary", disabled=(file_a is None or file_b is None)):
        if file_a and file_b:
            st.session_state.arena_active = True
            
            agent_a = QLearningAgent()
            meta_a = agent_a.load_q_table(file_a.getvalue().decode("utf-8"))
            st.session_state.agent_a = agent_a
            
            agent_b = QLearningAgent()
            meta_b = agent_b.load_q_table(file_b.getvalue().decode("utf-8"))
            st.session_state.agent_b = agent_b
            
            name_a = file_a.name.replace('.json', '')
            name_b = file_b.name.replace('.json', '')
            
            wins_a = 0
            wins_b = 0
            draws = 0
            
            matches_history = []
            
            env = TicTacToe()
            
            for match_idx in range(1, num_matches + 1):
                env.reset()
                
                agente_a_eh_x = (match_idx % 2 != 0)
                simbolo_a = 1 if agente_a_eh_x else -1
                simbolo_b = -1 if agente_a_eh_x else 1
                
                match_states = [list(env.board)]
                
                vez = 1
                primeira_jogada = True
                while not env.done:
                    avail = env.available_actions()
                    state_str = env.get_state()
                    
                    if primeira_jogada:
                        action = random.choice(avail)
                        primeira_jogada = False
                    elif vez == simbolo_a:
                        action = agent_a.choose_action(state_str, avail, explore=False, player=vez)
                    else:
                        action = agent_b.choose_action(state_str, avail, explore=False, player=vez)
                        
                    env.step(action, player=vez)
                    match_states.append(list(env.board))
                    
                    vez = -1 if vez == 1 else 1
                    
                if env.winner == simbolo_a:
                    wins_a += 1
                    winner_name = name_a
                elif env.winner == simbolo_b:
                    wins_b += 1
                    winner_name = name_b
                else:
                    draws += 1
                    winner_name = "Empate"
                    
                matches_history.append({
                    "match_id": match_idx,
                    "agente_a_eh_x": agente_a_eh_x,
                    "states": match_states,
                    "winner_name": winner_name
                })
                
            st.session_state.wins_a = wins_a
            st.session_state.wins_b = wins_b
            st.session_state.draws = draws
            st.session_state.matches_history = matches_history
            st.session_state.name_a = name_a
            st.session_state.name_b = name_b
            
            st.rerun()

    # Se a arena estiver ativa, exibe o placar e o replay
    if st.session_state.get('arena_active', False):
        st.divider()
        
        # Placar
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Vitórias {st.session_state.name_a}", st.session_state.wins_a)
        col2.metric("Empates", st.session_state.draws)
        col3.metric(f"Vitórias {st.session_state.name_b}", st.session_state.wins_b)
        
        st.divider()
        st.subheader("📺 Replay das Partidas")
        
        matches = st.session_state.matches_history
        options = [f"Partida {m['match_id']} - Vencedor: {m['winner_name']}" for m in matches]
        selected_option = st.selectbox("Escolha uma partida para assistir:", options)
        
        selected_idx = options.index(selected_option)
        match_data = matches[selected_idx]
        
        agente_a_eh_x = match_data["agente_a_eh_x"]
        states = match_data["states"]
        
        symbol_a = "X" if agente_a_eh_x else "O"
        symbol_b = "O" if agente_a_eh_x else "X"
        
        st.info(f"Nesta partida: **{st.session_state.name_a}** jogou como '{symbol_a}' e **{st.session_state.name_b}** jogou como '{symbol_b}'.")
        
        step = st.slider("Avançar jogadas", 0, len(states) - 1, 0)
        
        board_to_render = states[step]
        st.markdown(render_board(board_to_render), unsafe_allow_html=True)
        
        if step == len(states) - 1:
            if match_data['winner_name'] == "Empate":
                st.warning("Fim da Partida. Resultado: Empate")
            else:
                st.success(f"Fim da Partida. Vencedor: {match_data['winner_name']}")

elif menu == "2. Jogar contra o Agente":
    st.header("🎮 Jogue contra o Agente")
    st.markdown("Faça o upload do 'cérebro' (arquivo JSON) do seu agente treinado e tente vencê-lo!")
    
    file_agent = st.file_uploader("Upload do Agente (Joga como 'O')", type=['json'])
    
    if file_agent:
        agent = QLearningAgent()
        meta = agent.load_q_table(file_agent.getvalue().decode("utf-8"))
        agent_name = file_agent.name.replace('.json', '')
        
        if meta:
            with st.expander("ℹ️ Informações de Treinamento do Agente", expanded=False):
                st.markdown(f"**Épocas:** {meta['epochs']} | **Alfa:** {meta['alpha']} | **Vitória:** {meta['reward_win']} | **Empate:** {meta['reward_draw']} | **Derrota:** {meta['reward_loss']}")
        
        # Inicialização do estado do jogo na sessão do Streamlit
        if 'game_env' not in st.session_state:
            st.session_state.game_env = TicTacToe()
            st.session_state.humano_comeca = True
            
        humano_comeca = st.session_state.humano_comeca
        simbolo_humano = 1 if humano_comeca else -1
        simbolo_agente = -1 if humano_comeca else 1
        
        str_simbolo_humano = 'X' if humano_comeca else 'O'
        str_simbolo_agente = 'O' if humano_comeca else 'X'
        
        env = st.session_state.game_env
        
        st.subheader(f"Você é o '{str_simbolo_humano}' e o {agent_name} é o '{str_simbolo_agente}'")
        st.markdown("""
        <style>
        div.stButton > button:first-child { 
            height: 100px; 
            background-color: #2C3E50 !important;
            border-radius: 10px !important;
            border: none !important;
        }
        div.stButton > button:first-child, 
        div.stButton > button:first-child * { 
            font-size: 50px !important; 
            font-weight: 900 !important; 
            color: #ECF0F1 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Criação do tabuleiro visual com botões num grid 3x3
        # Centraliza o tabuleiro reduzindo sua largura total
        _, center_col, _ = st.columns([1, 1, 1])
        
        with center_col:
            for row in range(3):
                cols = st.columns(3)
                for col_idx in range(3):
                    i = row * 3 + col_idx
                    col = cols[col_idx]
                    cell_value = env.board[i]
                    
                    # Texto do botão baseado no estado da célula
                    text = " "
                    if cell_value == 1:
                        text = "X"
                    elif cell_value == -1:
                        text = "O"
                        
                    # Desabilita o botão se a célula já foi jogada ou o jogo acabou
                    disabled = cell_value != 0 or env.done
                    
                    # Quando o usuário clica num botão
                    if col.button(text, key=f"cell_{i}", disabled=disabled, use_container_width=True):
                        # Turno do Humano
                        _, done, winner = env.step(i, player=simbolo_humano)
                        st.rerun() # Atualiza a tela para refletir a jogada
                        
        if not env.done:
            vez_atual = 1 if env.board.count(0) % 2 != 0 else -1
            if vez_atual == simbolo_agente:
                # Turno do Agente
                avail = env.available_actions()
                state_str = env.get_state()
                action = agent.choose_action(state_str, avail, explore=False, player=simbolo_agente)
                _, done, winner = env.step(action, player=simbolo_agente)
                st.rerun()
        
        st.divider()
        if env.done:
            if env.winner == simbolo_humano:
                st.success("🎉 Você venceu! (Ou o agente ainda precisa treinar mais 😅)")
            elif env.winner == simbolo_agente:
                st.error("🤖 O Agente venceu! A máquina superou o criador.")
            else:
                st.info("🤝 Empate! Belo jogo.")
                
            if st.button("🔄 Jogar Novamente", type="primary"):
                env.reset()
                st.session_state.humano_comeca = not st.session_state.humano_comeca
                st.rerun()


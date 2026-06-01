import random
import os

def tela(p):
	os.system("cls")
	for i in range(len(p), 9):
		p = "0"+p
	k = ""
	print("    1   2   3  ")
	for i in range(0, 9):
		if i % 3 == 0:
			print("  +---+---+---+")
		k = k+"| "+valor(p[i])+" "
		if (i+1)%3==0:
			k = str(i//3+1)+" "+k+"|"
			print(k)
			k = ""
	print("  +---+---+---+")

def jogada(p):
	x = ""
	k = -1
	vk = "1"
	while vk != "0":
		l = int(input("Digite a linha: "))
		while l<1 or l>3:
			l = int(input("Digite a linha: "))

		c = int(input("Digite a coluna: "))
		while c<1 or c>3:
			c = int(input("Digite a coluna: "))
		k = indDaPos(l,c)
		vk = p[k]
	print(p)
	a = "1"
	for i in range(0,9):
		if i==k:
			x = x + a[0]
		else:
			x = x + p[i]
	return x

def jogaAleatorio(p, n):
	k = random.randint(0,8)
	x = ""
	while p[k] != "0":
		k = random.randint(0,8)
	a = n
	for i in range(0,9):
		if i==k:
			x = x + a[0]
		else:
			x = x + p[i]
	return x, k

def ganhou(p, n):
	if (p[0]==n and p[1]==n and p[2]==n) or (p[3]==n and p[4]==n and p[5]==n) or (p[6]==n and p[7]==n and p[8]==n):
		return True
	if (p[0]==n and p[3]==n and p[6]==n) or (p[1]==n and p[4]==n and p[7]==n) or (p[2]==n and p[5]==n and p[8]==n):
		return True
	if (p[0]==n and p[4]==n and p[8]==n) or (p[2]==n and p[4]==n and p[6]==n):
		return True
	return False

def indDaPos(lin, col):
	return (lin-1)*3+col-1

def estado(x):
	if x == 0:
		return ""
	else:
		return estado(x//3)+str(x%3)

def valor(x):
	if x == "0":
		return " "
	elif x == "1":
		return "X"
	else:
		return "O"

def partidaNormal(tipo, tQ):
	resposta = "S"
	partida_count = 0
	while resposta == "S" or resposta == "s":
		p = "000000000"
		tela(p)
		v = False
		# Inverte quem comeca a cada partida
		vez_do_humano = (partida_count % 2 == 0)
		simbolo_humano = "1" if vez_do_humano else "2"
		simbolo_agente = "2" if vez_do_humano else "1"
		vez = "1" # 1 sempre começa (X)

		while "0" in p:
			if vez == simbolo_humano:
				print(f"Sua vez ({simbolo_humano} - {valor(simbolo_humano)}):")
				p = jogada(p)
				tela(p)
				if ganhou(p, simbolo_humano):
					v = True
					print("Você Ganhou!")
					break
				vez = simbolo_agente
			else:
				print(f"Vez do computador ({simbolo_agente} - {valor(simbolo_agente)}):")
				if tipo == 1:
					p, k = jogaAleatorio(p, simbolo_agente)
				else:
					p, k = jogaComTQ(p, simbolo_agente, tQ[getIndEst(p)])
				tela(p)
				if ganhou(p, simbolo_agente):
					v = True
					print("Você Perdeu!")
					break
				vez = simbolo_humano
		if v == False:
			print("Deu velha!")
		print(p)
		resposta = input("Deseja jogar novamente [S] (sim) e [N] (não): ")
		partida_count += 1

def geraTabelaQ():
	tQ = []
	for i in range(0, 19683):
		lQ = [0,0,0,0,0,0,0,0,0]
		tQ.append(lQ)
	return tQ

def getIndEst(p):
	v = 0
	for i in range(0,len(p)):
		v = v + 3 ** i * int(p[i])
	return v

def jogaComTQ(p, n, vet):
	pv = True
	m = 0
	k = 0
	x = ""
	for i in range(0,9):
		if p[i] == "0":
			if pv or (n=="1" and vet[i]<m):
				pv = False
				m = vet[i]
				k = i
			if pv or (n=="2" and vet[i]>m):
				pv = False
				m = vet[i]
				k = i
	a = n
	for i in range(0,9):
		if i==k:
			x = x + a[0]
		else:
			x = x + p[i]
	return x, k

def treina(epocas, tQ):
    alpha = 0.8 # Taxa de aprendizagem
    gamma = 1 - alpha # Taxa de desconto
    epsilon = 0.3 # Percentual de jogos aleatórios para aprendizagem
    refVitoria = 5
    refEmpate  = 2
    refDerrota = -3

    for t in range(0, epocas):
        estadoAcao=[]
        usaTQ = True if random.random() > epsilon else False # Treina de maneira aleatória ou usa a Tabela Q
        p = "000000000"
        ref = refEmpate # Reforço para empate
        
        # Inverte quem o agente representa a cada partida
        agente_como = "1" if t % 2 == 0 else "2"
        adversario = "2" if agente_como == "1" else "1"
        vez = "1" # 1 sempre começa (X)

        while "0" in p:
            ea = p
            if vez == agente_como:
                if not usaTQ:
                    p, jgd = jogaAleatorio(p, agente_como)
                else: 
                    p, jgd = jogaComTQ(p, agente_como, tQ[getIndEst(p)])
                estAct = [getIndEst(ea), jgd, agente_como]
                estadoAcao.append(estAct)
                if ganhou(p, agente_como):
                    ref = refDerrota if agente_como == "1" else refVitoria
                    break
                vez = adversario
            else:
                if not usaTQ:
                    p, jgd = jogaAleatorio(p, adversario)
                else: 
                    p, jgd = jogaComTQ(p, adversario, tQ[getIndEst(p)])
                estAct = [getIndEst(ea), jgd, adversario]
                estadoAcao.append(estAct)
                if ganhou(p, adversario):
                    ref = refDerrota if adversario == "1" else refVitoria
                    break
                vez = agente_como
                
        for l in estadoAcao:
            i = l[0]
            j = l[1]
            jogador = l[2]
            if jogador == "1":
                tQ[i][j] = tQ[i][j]+alpha*(ref+gamma*(min(tQ[i])-tQ[i][j]))
            else:
                tQ[i][j] = tQ[i][j]+alpha*(ref+gamma*(max(tQ[i])-tQ[i][j]))
    return tQ

# Principal ...
tQ = geraTabelaQ()
q = 0
while q<1 or q>2:
	q = int(input("Digite: 1 para jogar contra o agente aleatório e 2 para jogar contra o treinado: "))

if q == 2:
    epocas = int(input("Digite a quantidade de épocas para o treinamento do agente: "))
    tQ = treina(epocas, tQ)

partidaNormal(q, tQ)
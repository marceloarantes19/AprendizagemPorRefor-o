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
	while resposta == "S" or resposta == "s":
		p = "000000000"
		tela(p)
		i = 0
		k = 0
		v = False
		while i<9:
			i = i + 1
			p = jogada(p)
			tela(p)
			if ganhou(p, "1"):
				v = True
				print("Você Ganhou!")
				break
			if i<9:
				i = i+1
				if tipo == 1:
					p, k=jogaAleatorio(p, "2")
				else:
					p, k=jogaComTQ(p, "2", tQ[getIndEst(p)])
				tela(p)
				if ganhou(p, "2"):
					v = True
					print("Você Perdeu!")
					break
		if v == False:
			print("Deu velha!")
		print(p)
		resposta = input("Deseja jogar novamente [S] (sim) e [N] (não): ")

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
        i = 0
        ref = refEmpate # Reforço para empate
        while i<9:
            i = i + 1
            ea = p
            if not usaTQ: # or t < 1000:
                p, jgd = jogaAleatorio(p, "1")
            else: 
                p, jgd = jogaComTQ(p, "1", tQ[getIndEst(p)])
            estAct = [getIndEst(ea), jgd]
            estadoAcao.append(estAct)
            if ganhou(p, "1"):
                ref = refDerrota # Reforço para derrota do agente
                break
            if i<9:
                i = i+1
                ea = p
                if not usaTQ or t<1000:
                    p, jgd = jogaAleatorio(p, "2")
                else: 
                    p, jgd = jogaComTQ(p, "2", tQ[getIndEst(p)])
                estAct = [getIndEst(ea), jgd]
                estadoAcao.append(estAct)
                if ganhou(p, "2"):
                    ref = refVitoria # Reforço para vitória do agente
                    break
        cnt = 0
        for l in estadoAcao:
            cnt = cnt + 1
            i = l[0]
            j = l[1]
            if (cnt % 2) == 1:
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
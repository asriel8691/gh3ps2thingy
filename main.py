import os
from PIL import Image

def preparacao(option, extensions): # lista os arquivos a serem processados com base nas extensões

    diretorio_atual = os.getcwd()  # pega o diretorio atual
    arquivos = [] # guarda os arquivos listados
    encontrou_arquivos = False

    for file in os.listdir(diretorio_atual): # para cada arquivo no diretorio atual
        fileLower = file.lower() # o nome do arquivo ficará em minusculo para usar a comparação do 'extensions'
        for extensao in extensions: # para cada extensão no parametro extensions
            if extensao in fileLower: # se o nome tiver a extensao
                encontrou_arquivos = True # marca o encontrou arquivos como true
                if file not in arquivos: # se o arquivo não estiver ainda na lista
                    arquivos.append(file) # adiciona o arquivo

    if encontrou_arquivos == False: # se nenhum arquivo com o parametro de extensions for encontrado
        print('Não há arquivos para trabalhar\nVerifique se houve erro de digitação no nome dos arquivos.')
    else:
        if option == 1: # se a opção for X
            listar_canais(arquivos) # ativa a função levando a lista de arquivos junto
        elif option == 2 or option == 3:
            vagparameter(arquivos)
        elif option == 4:
            inverte_colunas(arquivos)


def inverte_colunas(lista_arquivos):

    for imagem in lista_arquivos: # para cada imagem na lista de arquivos

        if "_inv" in imagem: # se tiver _inv no nome
            print("Pulando {} (já invertido)\n".format(imagem))
            continue

        nome, ext = os.path.splitext(imagem) # separa o nome da extensão
        img = Image.open(imagem) # abre a imagem como img
        pixels = img.load()
        largura, altura = img.size # pega a largura e a altura da img
        print("Invertendo {}".format(imagem))

        saida = img.copy() # copia a imagem para a saida
        saida_pixels = saida.load() # carrega cada pixel no saida_pixels
        saida_nome = nome + "_inv" + ext # o nome e a extensão será o mesmo junto com _inv, mostrando que inverteu as colunas

        for x in range(0, largura, 2): # range(0, largura da imagem, de 2 em 2)
            if x + 1 < largura:  # certifica se tem uma segunda coluna para trocar
                for y in range(altura): # repete a inversão em toda a altura
                    saida_pixels[x, y] = pixels[x + 1, y]  # coluna direita da entrada vai para a esquerda da saida
                    saida_pixels[x + 1, y] = pixels[x, y]  # coluna esquerda da entrada vai para a direita da saida
            else:
                for y in range(altura):  # se não houver uma segunda coluna
                    saida_pixels[x, y] = pixels[x, y]

        saida.save(saida_nome, icc_profile = img.info.get("icc_profile")) #iccprofile será o mesmo do input. se tiver o icc do photoshop, manterá saturado no final
        print("Colunas invertidas com sucesso!\n")

def vagparameter(lista_arquivos):

    for arquivo in lista_arquivos: # para cada arquivo na lista_arquivos
        with open(arquivo, 'rb') as file: # lê o arquivo como bytes

            conteudo = file.read() # guarda todos os bytes na variável
            palavras = [b"VAGp", b"MSVp"] # palavras chave para encontrar o header dentro do arquivo
            print("\nArquivo: {}".format(arquivo))

            for palavra in palavras: # para cada palavra chave na lista
                position = conteudo.find(palavra) # a posição 0 da palavra é guardada

                while position != -1: # enquanto a posição não for -1

                    file.seek(position + 4) # move o ponteiro para a position, em relação ao inicio do arquivo, + 4
                    file.seek(8,1) # move o ponteiro a partir de sua posição para 8 na direita
                    bytelength = file.read(4).hex() # lê a quantidade em bytes o tamanho do audio, tirando o header
                    sample = int.from_bytes(file.read(4), 'big') # lê o samplerate
                    file.seek(12,1) # move o ponteiro em 12 a partir de sua posição
                    inName = file.read(16).decode('utf-8', errors='ignore') # lê o nome interno da parte do arquivo

                    if option != 3 or arquivo != "sfx.wad": # se não for option 3 ou sfx.wad
                        print("{} - {} ({} bytes, {}Hz)".format(int(position), inName, bytelength.lstrip('0'), sample)) # printa
                        position = conteudo.find(palavra, position + 1) # procura a próxima instancia da palavra
                        continue # volta pro inicio do while

                    # quando opt = 3 e arquivo atual for sfx.wad, passa da condição e continua o while

                    file.seek(position) # move o ponteiro para a position, em relação ao inicio do arquivo
                    block = file.read(int(bytelength, 16) + 64) # lê o arquivo com o valor do tamanho de bytes + tamanho do header (64)

                    if sfxripper(inName, block) == False: # se em uma execução do sfxripper retornar false 
                        print("\nParando extração do sfx.wad\n(Já foi extraído)") # para a extração
                        break # quebra o loop

                    position = conteudo.find(palavra, position + 1) # procura a próxima instancia da palavra

def sfxripper(block_name, block_bytes): # quando a opção for 3 e o arquivo atual do vagparameter for sfx.wad, o bloco nome e bytes serão usados para extrair o arquivo

    i = 1 # instancia de nome igual

    current_file = block_name.replace("\x00", "").strip() # nome do arquivo atual sem caractere torto
    out_filename = f"{current_file} ({i}).vag" # nome do arquivo saida será o nome do bloco + instancia + .vag

    out_path = os.path.join("sfxrip", out_filename)  # caminho de saída para salvar será na pasta sfxrip
    os.makedirs("sfxrip", exist_ok=True)  # cria a pasta caso não exista

    while os.path.exists(out_path): # enquanto já ouver um arquivo/caminho com mesmo nome

        i = i + 1 # aumenta 1 na instancia
        out_filename = f"{current_file} ({i}).vag" # atualiza nome de saida

        if out_filename == 'gh3_battle_diff (2).vag': # se já houver o primeiro sfx na pasta
            return False # retorna false

        out_path = os.path.join("sfxrip", out_filename) # atualiza caminho de saida

    with open(out_path, 'wb') as out_file: # abre o caminho de saida como arquivo para escrita em bytes
        out_file.write(block_bytes) # escreve/extrai o bloco nele
    
    print("{} extraído\n".format(out_filename)) # printa



def listar_canais(lista_arquivos): # lista todos os arquivos vag e prepara em casais para ser processados

    casais = []
    encontrou_arquivos = False

    for arquivo in lista_arquivos:
        if arquivo.endswith("L.vag") or arquivo.endswith("R.vag"): # se terminar em l ou r
            encontrou_arquivos = True # encontrou arquivo
            casal = arquivo[:-5]  # remove até o l/r, sendo o casal atual
            if casal not in casais: # se o casal não estiver na lista
                casais.append(casal) # coloca nela
    
    if encontrou_arquivos == False: # se não tiver arquivos na pasta
        print('Não há arquivos para converter\nVerifique se houve erro de digitação no nome dos arquivos.')
    
    for casal in casais: # para cada casal na lista de casais

        arquivoL = casal + "L.vag"
        arquivoR = casal + "R.vag"

        if arquivoL in lista_arquivos and arquivoR in lista_arquivos: # se tiver ambos os canais
            print("\nPreparando o casal {}".format(casal))

            arquivosMSV = [] # lista para os msv criados para então ser usado no mesclar arquivos
            arquivosVAG = [arquivoL, arquivoR] # lista para criar o msv do casal, assim não alterando os arquivos vag originais

            for arquivoVAG in arquivosVAG: # para cada vag

                arquivoMSV = arquivoVAG[:-4] + ".msvs" # atualiza o nome do arquivo msv a cada iteração (L dps R)
                print("Criando {}".format(arquivoMSV))
                with open(arquivoVAG, 'rb') as arquivo_origem, open(arquivoMSV, 'wb') as arquivo_preparado: # abre para ler os bytes do vag atual e clona-o como msv
                    conteudo = arquivo_origem.read() # o conteudo terá todos os bytes do arquivo_origem / vag
                    arquivo_preparado.write(conteudo) # o conteudo é passado para o arquivo_preparado / msv
                    arquivo_origem.close()


                arquivosMSV.append(arquivoMSV) # após a clonação, o msv criado é listado no arquivos msv

            mesclar_arquivos(arquivosMSV, 0x20000, casal + ".msv") 

        else:
            if arquivoL not in lista_arquivos: # se não tiver um dos canais do casal atual no arquivos
                falta = "L"
            else:
                falta = "R"
            print("Casal incompleto: {} (Faltando o canal {})\nVerifique se há algum erro de digitação ou falta de canal".format(casal, falta))


def alterar_cabecalho(filepath): # altera o cabeçalho para ter MSV e o nome do arquivo

    print('Mudando cabeçalho {}'.format(filepath))

    with open(filepath, "r+b") as arquivo:
        cabecalho = arquivo.read(48)  # lê os primeiros 48 bytes (0x00 até 0x2F)
        
        if cabecalho[:3] == b'VAG':  # verifica se os primeiros 3 bytes são 'VAG'
            arquivo.seek(0)  # move o ponteiro para o início
            arquivo.write(b'MSV' + cabecalho[3:])  # substitui 'VAG' por 'MSV'

            arquivo.seek(32) # o ponteiro fica no 0x20, no início do nome do arquivo
            nome = filepath[:-5] # (arquivo) L.msv
            lado = filepath[-5] # arquivo (L) .msv
            arquivo.write((nome[:15] + lado).encode('utf-8')) # o nome é limitado a 15 chars. o lado ficará no final do nome mesmo se passar do limite
            tirar_trigger_final(filepath)
        

def tirar_trigger_final(filepath): # tira o trigger de parar a música no final do arquivo

    print('Tirando flag final {}'.format(filepath))

    with open(filepath, "r+b") as arquivo:
        arquivo.seek(-31, 2) # move o ponteiro para o final do arquivo e 31 para trás
        rodape = arquivo.read(31) # lê o final do arquivo
        if rodape[:1] == b'\x01': # se o primeiro byte for 0x01
            rodape = b'\x00' * 31 # o rodapé será reescrito com 0x00
            arquivo.seek(-31, 2) # move o ponteiro novamente
            arquivo.write(rodape) # o rodapé é escrito no arquivo atual


def ajustar_tamanho_para_multiplo(filepath, tamanho_multiplo):
    """
    Garante que o arquivo tenha tamanho múltiplo de `tamanho_multiplo`.
    Preenche com 0x00 (bytes nulos) no final, se necessário.
    """
    # Abrir o arquivo no modo binário para leitura
    with open(filepath, "rb") as arquivo:
        conteudo = arquivo.read()  # Lê todo o conteúdo do arquivo como bytes

    tamanho_atual = len(conteudo)  # Obtém o tamanho atual do arquivo
    restante = tamanho_multiplo - (tamanho_atual % tamanho_multiplo)  # Calcula os bytes faltantes para o próximo múltiplo

    if restante != tamanho_multiplo:  # Se o arquivo não for múltiplo exato do tamanho desejado
        conteudo += b'\x00' * restante  # Adiciona bytes nulos (0x00) para completar o tamanho

    # Salva o conteúdo ajustado de volta no arquivo
    with open(filepath, "wb") as arquivo:
        arquivo.write(conteudo)

    return conteudo  # Retorna o conteúdo ajustado para uso posterior


def mesclar_arquivos(lista_arquivos, tamanho_multiplo, arquivo_saida):
    """
    Combina os arquivos fornecidos em blocos de `tamanho_multiplo` (0x20000).
    Alterna blocos de cada arquivo até que todos sejam processados.
    """
    arquivos_processados = [] # cria uma lista limpa para os arquivos processados em bytes
    for arquivo in lista_arquivos: # para cada arquivo da lista_arquivo (casal de L e R)
        print('\nComeçando processamento {}'.format(arquivo))
        alterar_cabecalho(arquivo)
        arquivos_processados.append(ajustar_tamanho_para_multiplo(arquivo, tamanho_multiplo)) # chama a função para ajustar o tamanho do lado atual e coloca ela na lista
        print('Tamanho ajustado {}'.format(arquivo))

    
    # Determina o número máximo de blocos em qualquer arquivo
    num_blocos = max(len(arquivo) // tamanho_multiplo for arquivo in arquivos_processados)

    # Abre o arquivo de saída no modo binário para escrita
    with open(arquivo_saida, "wb") as saida:
        # Itera sobre os blocos de todos os arquivos
        for bloco in range(num_blocos):  # Para cada bloco (0, 1, 2, ...)
            print('Fazendo bloco {} de {} (L e R)'.format(bloco + 1, num_blocos), end='\r') # \r "reprinta" a linha atual
            for arquivo in arquivos_processados:  # Para cada arquivo na lista processada

                inicio = bloco * tamanho_multiplo  # Calcula o início do bloco
                fim = inicio + tamanho_multiplo  # Calcula o final do bloco

                if inicio < len(arquivo):  # Certifica-se de que o bloco existe no arquivo
                    saida.write(arquivo[inicio:fim])  # Escreve o bloco atual no arquivo de saída
    
    print('\nArquivo MSV feito!')


if __name__ == "__main__":
    
    option = None

    while option != 0:
        try:
            option = int(input("\nAsriel8691's GH3PS2 Thingy\n\n1 - VAGs 2 Menu music\n2 - VAG/MSV parameters\n3 - SFX Ripper\n4 - Invert images columns\n0 - Exit\n> "))
        except:
            print('\nValor inválido\n')
            continue

        if option == 1:
            preparacao(option, [".vag"])
        elif option == 2 or option == 3:
            preparacao(option, [".vag", ".wad", ".msv", ".msvs", ".isf", ".imf"])
        elif option == 4:
            preparacao(option, [".png", ".jpg", ".jpeg"])
        elif option == 9:
            print('Versão 1.2')
    
    print('Closing...')
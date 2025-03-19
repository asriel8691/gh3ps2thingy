import os
from PIL import Image

def preparacao(option, extensions): # lista os arquivos a serem processados com base nas extensões

    currentExecutedDir = os.getcwd()  # pega o diretorio atual
    fileList = [] # guarda os arquivos listados
    fileWasFound = False

    for file in os.listdir(currentExecutedDir): # para cada arquivo no diretorio atual
        fileLowercaseName = file.lower() # o nome do arquivo ficará em minusculo para usar a comparação do 'extensions'

        for fileExtensions in extensions: # para cada extensão no parametro extensions

            if fileExtensions in fileLowercaseName: # se o nome tiver a extensao
                fileWasFound = True # marca o encontrou arquivos como true

                if file not in fileList: # se o arquivo não estiver ainda na lista
                    fileList.append(file) # adiciona o arquivo

    if fileWasFound == False: # se nenhum arquivo com o parametro de extensions for encontrado
        print('\nNo files to work with\nCheck for typos in file names')
    else:
        if option == 1: # se a opção for X
            listar_canais(fileList) # ativa a função levando a lista de arquivos junto
        elif option == 2 or option == 3:
            vagparameter(fileList)
        elif option == 4:
            inverte_colunas(fileList)


def inverte_colunas(lista_arquivos):

    for imagem in lista_arquivos: # para cada imagem na lista de arquivos

        if "_inv" in imagem: # se tiver _inv no nome
            print("\nSkipping {} (already swapped)".format(imagem))
            continue

        nome, ext = os.path.splitext(imagem) # separa o nome da extensão
        img = Image.open(imagem) # abre a imagem como img
        pixels = img.load()
        largura, altura = img.size # pega a largura e a altura da img
        print("\nSwapping {}".format(imagem))

        saida = img.copy() # copia a imagem para a saida
        saida_pixels = saida.load() # carrega cada pixel no saida_pixels
        saida_nome = nome + "_inv" + ext # o nome e a extensão será o mesmo junto com _inv, mostrando que inverteu as colunas

        for x in range(0, largura - 1, 2): # largura - 1 garante que as imagens impares não troquem a ultima coluna
            for y in range(altura): # repete a inversão em toda a altura
                saida_pixels[x, y] = pixels[x + 1, y]  # coluna impar da saída será a par da entrada
                saida_pixels[x + 1, y] = pixels[x, y]  # coluna par da saída será a ímpar da entrada

        saida.save(saida_nome, icc_profile = img.info.get("icc_profile")) #iccprofile será o mesmo do input. se tiver o icc do photoshop, manterá saturado no final
        print("Column swapped successfully!")

def vagparameter(lista_arquivos):

    sfxWasFoundCounter = 1 # conta os arquivos passados

    for file in lista_arquivos: # para cada arquivo na lista_arquivos

        if option == 3 and file == 'sfx.wad': # se a opção for 3 e for sfx.wad
            sfxExtractPath = str(input('\nExtract sfx.wad to (ex: C:/sfxrip): ')) # pede o diretório para extração

        elif sfxWasFoundCounter == len(lista_arquivos) and option == 3: # se não achou
            print('\nNo sfx.wad to extract')
            return # sai da função sem retorno

        elif option == 3 and file != 'sfx.wad': # se a opção for 3 e não for sfx.wad 
            sfxWasFoundCounter = sfxWasFoundCounter + 1 # adiciona 1 ao contador
            continue # continua para o próximo arquivo
        

        with open(file, 'rb') as fileBytes: # lê o arquivo como bytes

            fileContent = fileBytes.read() # guarda todos os bytes na variável
            keywords = [b"VAGp", b"MSVp"] # palavras chave para encontrar o header dentro do arquivo
            print("\nFile: {}".format(file))

            for keyword in keywords: # para cada palavra chave na lista
                keyPosition = fileContent.find(keyword) # a posição da primeira palavra é guardada

                while keyPosition != -1: # enquanto a posição não for -1

                    fileBytes.seek(keyPosition + 4) # move o ponteiro para a position, em relação ao inicio do arquivo, + 4
                    fileBytes.seek(8,1) # move o ponteiro a partir de sua posição para 8 na direita
                    soundByteLength = fileBytes.read(4).hex() # lê a quantidade em bytes o tamanho do audio, tirando o header
                    soundSamplerate = int.from_bytes(fileBytes.read(4), 'big') # lê o samplerate
                    fileBytes.seek(12,1) # move o ponteiro em 12 a partir de sua posição
                    soundName = fileBytes.read(16).decode('utf-8', errors='ignore') # lê o nome interno da parte do arquivo
                    print("{} - {} ({} bytes, {}Hz)".format(int(keyPosition), soundName, soundByteLength.lstrip('0'), soundSamplerate)) # printa

                    if option != 3: # se não for option 3
                        keyPosition = fileContent.find(keyword, keyPosition + 1) # procura a próxima instancia da palavra
                        continue # volta pro inicio do while

                    # quando opt = 3 e arquivo atual for sfx.wad, passará da condição e continua o while

                    fileBytes.seek(keyPosition) # move o ponteiro para a position, em relação ao inicio do arquivo
                    soundBlock = fileBytes.read(int(soundByteLength, 16) + 64) # lê o arquivo com o valor do tamanho de bytes + tamanho do header (64)

                    if sfxripper(soundName, soundBlock, sfxExtractPath) == False: # se em uma execução do sfxripper retornar false 
                        print("\nStopping sfx.wad extraction\n(Already extracted)") # para a extração
                        break # quebra o loop

                    keyPosition = fileContent.find(keyword, keyPosition + 1) # procura a próxima instancia da palavra

def sfxripper(block_name, block_bytes, extract_path): # quando a opção for 3 e o arquivo atual do vagparameter for sfx.wad, o bloco nome e bytes serão usados para extrair o arquivo

    fileSameNameCounter = 1 # instancia de nome igual

    inFileName = block_name.replace("\x00", "").strip() # nome do arquivo atual sem caractere torto
    outFileName = f"{inFileName} ({fileSameNameCounter}).vag" # nome do arquivo saida será o nome do bloco + instancia + .vag

    outFileExtractPath = os.path.join(extract_path, outFileName)  # caminho de saída para salvar será na pasta extract_path
    os.makedirs(extract_path, exist_ok=True)  # cria a pasta caso não exista

    while os.path.exists(outFileExtractPath): # enquanto já houver um arquivo/caminho com mesmo nome

        fileSameNameCounter = fileSameNameCounter + 1 # aumenta 1 na instancia
        outFileName = f"{inFileName} ({fileSameNameCounter}).vag" # atualiza nome de saida

        if outFileName == 'gh3_battle_diff (2).vag': # se já houver o primeiro sfx na pasta
            return False # retorna false

        outFileExtractPath = os.path.join(extract_path, outFileName) # atualiza caminho de saida

    with open(outFileExtractPath, 'wb') as outFile: # abre o caminho de saida como arquivo para escrita em bytes
        outFile.write(block_bytes) # escreve/extrai o bloco nele
    
    print("{} extracted".format(outFileName)) # printa



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
        print('\nNo files to convert\nCheck for typos in file names')
    
    for casal in casais: # para cada casal na lista de casais

        arquivoL = casal + "L.vag"
        arquivoR = casal + "R.vag"

        if arquivoL in lista_arquivos and arquivoR in lista_arquivos: # se tiver ambos os canais
            print("\nChecking pair {}".format(casal))

            arquivosMSV = [] # lista para os msv criados para então ser usado no mesclar arquivos
            arquivosVAG = [arquivoL, arquivoR] # lista para criar o msv do casal, assim não alterando os arquivos vag originais

            for arquivoVAG in arquivosVAG: # para cada vag

                arquivoMSV = arquivoVAG[:-4] + ".msvs" # atualiza o nome do arquivo msv a cada iteração (L dps R)
                print("Creating {}".format(arquivoMSV))

                with open(arquivoVAG, 'rb') as arquivo_origem: # abre o arquivo original para copiar todo o conteudo
                    conteudo = arquivo_origem.read() # o conteudo terá todos os bytes do arquivo_origem / vag

                with open(arquivoMSV, 'wb') as arquivo_preparado: # cria/abre o arquivo preparado para colar o conteudo do original
                    arquivo_preparado.write(conteudo) # o conteudo é passado para o arquivo_preparado / msv

                arquivosMSV.append(arquivoMSV) # após a clonagem, o msv criado é listado no arquivos msv

            mesclar_arquivos(arquivosMSV, 0x20000, casal)


        else:
            if arquivoL not in lista_arquivos: # se não tiver um dos canais do casal atual no arquivos
                falta = "L"
            else:
                falta = "R"
            print("\nIncomplete pair: {} (Missing {} channel)\nCheck for typos in file name or missing file".format(casal, falta))


def alterar_cabecalho(filepath): # altera o cabeçalho para ter MSV e o nome do arquivo

    print('Changing header {}'.format(filepath))

    with open(filepath, "r+b") as arquivo: # abre como ler e escrever em binário
        cabecalho = arquivo.read(48)  # lê os primeiros 48 bytes (0x00 até 0x2F)
        
        if cabecalho[:3] == b'VAG':  # verifica se os primeiros 3 bytes são 'VAG'
            arquivo.seek(0)  # move o ponteiro para o início
            arquivo.write(b'MSV' + cabecalho[3:])  # substitui 'VAG' por 'MSV'

            arquivo.seek(32) # o ponteiro fica no 0x20, no início do nome do arquivo

            nome = (filepath.split('.')[0])[:-1] # (arquivo) L.msv (divide o nome do arquivo em 2 pelo '.', seleciona o primeiro item e depois corta o lado (L/R))
            lado = (filepath.split('.')[0])[-1] # arquivo (L) .msv

            arquivo.write((nome[:15] + lado).encode('utf-8')) # o nome é limitado a 15 chars. o lado ficará no final do nome mesmo se passar do limite
            tirar_trigger_final(filepath)
        

def tirar_trigger_final(filepath): # tira o trigger de parar a música no final do arquivo

    print('Cutting end flag {}'.format(filepath))

    with open(filepath, "r+b") as arquivo: # abre como ler e escrever em binário

        arquivo.seek(-31, 2) # move o ponteiro para o final do arquivo e 31 para trás
        rodape = arquivo.read(31) # lê o final do arquivo

        if rodape[:1] == b'\x01': # se o primeiro byte for 0x01
            rodape = b'\x00' * 31 # o rodapé será reescrito com 0x00
            arquivo.seek(-31, 2) # move o ponteiro novamente
            arquivo.write(rodape) # o rodapé é escrito no arquivo atual


def ajustar_tamanho_para_multiplo(filepath, tamanho_multiplo):
    # Abrir o arquivo no modo binário para leitura
    with open(filepath, "rb") as arquivo:
        conteudo = arquivo.read()  # Lê todo o conteúdo do arquivo como bytes

    tamanho_atual = len(conteudo)  # Obtém o tamanho atual do arquivo
    restante = tamanho_multiplo - (tamanho_atual % tamanho_multiplo)  # Calcula os bytes faltantes para o próximo múltiplo

    if restante != tamanho_multiplo:  # Se o arquivo não for múltiplo exato do tamanho desejado
        conteudo += b'\x00' * restante  # Adiciona bytes nulos (0x00) para completar o tamanho

    return conteudo  # Retorna o conteúdo ajustado para uso posterior


def mesclar_arquivos(lista_arquivos, tamanho_multiplo, arquivo_saida):
    """
    Combina os arquivos fornecidos em blocos de `tamanho_multiplo` (0x20000).
    Alterna blocos de cada arquivo até que todos sejam processados.
    """
    arquivos_processados = [] # cria uma lista limpa para os arquivos processados em bytes
    for arquivo in lista_arquivos: # para cada arquivo da lista_arquivo (casal de L e R)
        print('\nStarting process {}'.format(arquivo))
        alterar_cabecalho(arquivo)
        arquivos_processados.append(ajustar_tamanho_para_multiplo(arquivo, tamanho_multiplo)) # chama a função para ajustar o tamanho do lado atual e coloca ela na lista
        print('Adjusted size {}'.format(arquivo))

    
    # Determina o número máximo de blocos em qualquer arquivo
    num_blocos = max(len(arquivo) // tamanho_multiplo for arquivo in arquivos_processados)

    print('\nSorting channel blocks')

    # Abre o arquivo de saída no modo binário para escrita
    with open(arquivo_saida + '.msv', "wb") as saida:
        # Itera sobre os blocos de todos os arquivos
        for bloco in range(num_blocos):  # Para cada bloco (0, 1, 2, ...)
            print('Block {} of {} (L and R)'.format(bloco + 1, num_blocos), end='\r') # \r "reprinta" a linha atual
            for arquivo in arquivos_processados:  # Para cada arquivo na lista processada

                inicio = bloco * tamanho_multiplo  # Calcula o início do bloco
                fim = inicio + tamanho_multiplo  # Calcula o final do bloco

                if inicio < len(arquivo):  # Certifica-se de que o bloco existe no arquivo
                    saida.write(arquivo[inicio:fim])  # Escreve o bloco atual no arquivo de saída
    
    print('\nMSV created!')


if __name__ == "__main__":
    
    option = None

    while option != 0:
        try:
            option = int(input("\nAsriel8691's GH3PS2 Thingy\n\n1 - VAGs 2 Menu music\n2 - VAG/MSV parameters\n3 - SFX Ripper\n4 - Invert images columns\n\n0 - Exit\n> "))
        except:
            print('\nInput error\n')
            continue

        if option == 1:
            preparacao(option, [".vag"])
        elif option == 2 or option == 3:
            preparacao(option, [".vag", ".wad", ".msv", ".msvs", ".isf", ".imf"])
        elif option == 4:
            preparacao(option, [".png", ".jpg", ".jpeg"])
        elif option == 9:
            print('Versão 1.4')
    
    print('Closing...')
import os, io
from PIL import Image

def listfiles(extensions): # lista os arquivos a serem processados com base nas extensões

    currentExecutedDir = os.getcwd()  # pega o diretorio atual

    fileList = [] # guarda os arquivos listados
    fileWasFound = False

    for file in os.listdir(currentExecutedDir): # para cada arquivo no diretorio atual
        fileLowercaseName = file.lower() # o nome do arquivo ficará em minusculo para usar a comparação do 'extensions'

        for fileExtension in extensions: # para cada extensão no parametro extensions

            if fileLowercaseName.endswith(fileExtension.lower()): # se o nome tiver a extensao
                fileWasFound = True # marca o encontrou arquivos como true

                # fullFilePath = os.path.join(currentExecutedDir, file)

                if file not in fileList: # se o arquivo não estiver ainda na lista
                    fileList.append(file) # adiciona o arquivo

    if fileWasFound == False: # se nenhum arquivo com o parametro de extensions for encontrado
        print('\nNo files to work with\nCheck for typos in file names')
        return []
    else:
        return fileList



def sfxinjection_check(current_executed_dir): # checa se no diretório atual tem o sfx.wad (container) e sfx.header.qpScript (header)

    sfxContainerWasFound = False # checa se o sfx.wad está no mesmo diretório
    sfxHeaderWasFound = False # checa com o sfxheader.qbScript

    sfxContainer = None # guarda o diretório do sfx.wad
    sfxHeader = None # guarda o diretório do sfxheader.qbScript

    for file in os.listdir(current_executed_dir): # para cada arquivo no diretório

        base, ext = os.path.splitext(file) # separa o nome do arquivo da extensão

        if file == "sfx.wad": # se o arquivo for sfx.wad
            print('\nsfx.wad file found')
            sfxContainerWasFound = True # achou o container
            sfxContainer = file # guarda o diretório

        elif "sfxheader" in base.lower() or "sfx header" in base.lower(): # se tiver sfxheader no nome do arquivo com todas as letras minusculas
            if not "(injected)" in base.lower():
                print('\nsfx header file found')
                sfxHeaderWasFound = True # achou o header
                sfxHeader = file # guarda o diretório

        if sfxContainerWasFound == True and sfxHeaderWasFound == True: # se achou os dois
            print("\nStarting process")
            break # sai do loop de procurar arquivos
        
    if sfxContainerWasFound == False: # se não achou o container
        print('\nsfx.wad not found\nCopy the "sfx.wad" file from "sounds" folder in the GH3 root')
        return # sai da função

    elif sfxHeaderWasFound == False: # se não achou header
        print('\nsfxheader not found\nExtract the sfxheader file from qb.pak.ps2 using QueenBee')
        return # sai da função
    
    return sfxContainer, sfxHeader # começa a injeção de fato, com a lista de vags e diretórios do container e header



def sfxinjection_content(file_list): # injeta os vags no container e informações do vag no header

    currentExecutedDir = os.getcwd()

    sfxContainerFile, sfxHeaderFile = sfxinjection_check(currentExecutedDir)

    with open(sfxContainerFile, "rb") as sfxContainer: # abre o container em leitura para bytes
        sfxContainerContent = sfxContainer.read() # guarda os bytes

    with open(sfxHeaderFile, "rb") as sfxHeader: # abre o header original em leitura para bytes
        sfxHeaderContent = sfxHeader.read() # guarda os bytes dele no temporário

    for vag in file_list: # para cada vag na lista

        vagFileName, vagFileExt = os.path.splitext(vag) # separa o nome do arquivo da extensão
        bracketOpen = vagFileName.find('(') # ache se tem "(" no nome
        bracketEnd = vagFileName.find(')') # ache se tem ")" no nome

        # o nome do arquivo tem que ser: nome (X).vag
        # X sendo 1, 2, 3, etc

        print("\nInjecting {}".format(vagFileName))

        if bracketOpen == -1 or bracketEnd == -1: # se não tiver no nome
            print("Skipping {} (has no parentheses in file name)\nUse SFX Ripper to see the file name format".format(vag))
            continue # vai para o próximo vag

        vagInNameIterationEnd = int(vagFileName[bracketOpen + 1:bracketEnd]) # pega a iteração do nome interno que o vag irá substituir no container
        
        with open(vag, "rb") as vagFile: # lê o vag em bytes
            vagFile.seek(12) # move o ponteiro por 12 bytes
            vagFileByteLength = vagFile.read(4) # lê o tamanho do audio em bytes
            vagFileSamplerate = vagFile.read(4) # lê o samplerate

            vagFile.seek(12, 1) # move o ponteiro por 12 bytes a partir da posição atual
            vagFileInName = vagFile.read(32) # lê o nome interno do audio + 16 bytes vazios

            vagFileSound = vagFile.read() # lê o audio em bytes

        vagInNamePosition = sfxContainerContent.find(vagFileInName) # procura a posição do primeiro byte do nome interno no container
        vagInNameIteration = 0 # iteração de quantas vezes o nome interno se repete no container

        while vagInNameIteration < vagInNameIterationEnd: # enquanto a iteração for menor que a sequencia

            vagInNamePosition = sfxContainerContent.find(vagFileInName, vagInNamePosition + (32 * vagInNameIteration)) # procura a próxima posição do nome interno a partir da posição atual
            
            print('Intern name iteration: {} of {} - New position: {}'.format(vagInNameIteration + 1, vagInNameIterationEnd, hex(vagInNamePosition)), end = '\r')

            if vagInNamePosition == -1: # se for -1 / não achar
                print('\nIteration bigger than expected (sfx.wad has {} iterations)'.format(vagInNameIteration))
                break # quebra

            vagFileEndPosition = sfxContainerContent.find(b'\x00\x07\x77\x77', vagInNamePosition + (32 * vagInNameIteration)) # procura a posição do fim do vag de acordo com a iteração atual
            vagInNameIteration += 1 # passa para a próxima iteração

        if vagInNamePosition == -1:
            print('Skipping to next sequence')
            continue # continua no próximo vag

        print('\nRebuilding sfx.wad container')

        sfxContainerRemainder = sfxContainerContent[vagFileEndPosition + 16:] # guarda o restante do container a partir do final do vag atual
        # escreve o que estava antes do byte length, o próprio byte length, samplerate, espaço vazio, nome interno e o audio em si e, então escreve o restante
        sfxContainerContent = sfxContainerContent[:vagInNamePosition - 20] + vagFileByteLength + vagFileSamplerate + (b"\x00" * 12) + vagFileInName + vagFileSound + sfxContainerRemainder

    sfxinjection_construct(sfxContainerContent, sfxHeaderContent) # inicia a construção do header



def sfxinjection_construct(sfx_container_content, sfx_header_content):

    vagStartPositionList = [] # lista da posição inicial de todos os vags do container modificado
    vagSamplerateList = [] # lista de todos os samplerates
    vagTotalSizeList = [] # lista do tamanho total dos vags (bytes length + cabeçalho)

    vagStartPosition = sfx_container_content.find(b"VAGp") # procura a posição inicial do vag no container modificado

    while vagStartPosition != -1: # enquanto não for -1

        vagStartPositionList.append(vagStartPosition) # guarda a posição na lista
        vagStartPosition = sfx_container_content.find(b"VAGp", vagStartPosition + 4) # procura pela próxima instancia do VAGp no container a partir da posição atual + 4

    bufferContainer = io.BytesIO() # cria um arquivo temporário para o container modificado
    bufferContainer.write(sfx_container_content) # escreve o container nele
    bufferContainer.seek(0) # move o ponteiro para o início

    bufferHeader = io.BytesIO() # cria um arquivo temporário para o header
    bufferHeader.write(sfx_header_content) # escreve o conteúdo no temporário
    bufferHeader.seek(2) # move o ponteiro do temporário para o terceiro byte

    for position in vagStartPositionList: # para cada posição na lista de posições iniciais

        bufferContainer.seek(position + 12, 0) # move o ponteiro por 12 bytes a partir da posição atual

        vagFileSize = int.from_bytes(bufferContainer.read(4), "big") # lê o byte length e transforma em número inteiro
        vagFileSize = (vagFileSize + 64).to_bytes(4, "big") # adiciona 64, o tamanho do cabeçalho, e transforma para bytes novamente

        vagTotalSizeList.append(vagFileSize) # guarda o tamanho total na lista
        vagSamplerateList.append(bufferContainer.read(4)) # lê e guarda o samplerate na lista dele

    print('\nCreating injected container file')

    with open("sfx (injected).wad", "wb") as sfxContainerJ: # abre/cria o arquivo do container modificado
        sfxContainerJ.write(bufferContainer.getvalue()) # escreve o arquivo temporário no container

    bufferContainer.close() # limpa o buffer


    print('\nRebuilding sfxheader')

    sfxCurrentVag = 0 # linha atual do header

    while sfxCurrentVag < len(vagStartPositionList): # enquanto o numero do vag atual for menor que o tamanho da lista de posições (de todos os vags do container)
        bufferHeader.seek(42, 1) # move o ponteiro para 42 a partir da posição atual
        bufferHeader.write(vagSamplerateList[sfxCurrentVag][::-1]) # escreve o samplerate do vag atual em little

        bufferHeader.seek(12, 1) # move o ponteiro em 12
        sfxHeaderStereoCheck = bufferHeader.read(4) # lê o flag de mono ou estéreo da linha atual do header

        bufferHeader.seek(12, 1) # move o ponteiro em 12
        bufferHeader.write(vagStartPositionList[sfxCurrentVag].to_bytes(4, "little")) # escreve a posição atual do vag atual em little

        if sfxHeaderStereoCheck == b"\x72\xB3\x03\x02": # se a string do flag for estéreo
            sfxCurrentVag += 1 # pula para o próximo vag (se não pular, ele escreverá o lado direito do vag na próxima linha do header, quebrando a leitura no final)

        bufferHeader.seek(12, 1) # move o ponteiro em 12
        bufferHeader.write(vagTotalSizeList[sfxCurrentVag][::-1]) # escreve o tamanho total do arquivo do vag atual em little

        bufferHeader.seek(6, 1) # move o ponteiro em 6
        sfxCurrentVag += 1 # vai para o próximo vag

    if sfxCurrentVag < 558:
        print('Rebuilding process finished early\nRemaining headers will not be modified')

    print('\nCreating injected header file')

    with open("sfxheader (injected).qbScript", "wb") as sfxHeaderJ: # abre/cria o header modificado
        sfxHeaderJ.write(bufferHeader.getvalue()) # escreve o arquivo temporário do header modificado nele

    bufferHeader.close() # limpa o buffer

    print('\nFiles injected successfully!')



def swapcolumns(file_list):

    for image in file_list: # para cada imagem na lista de arquivos

        if "_inv" in image: # se tiver _inv no nome
            print("\nSkipping {} (already swapped)".format(image))
            continue

        imageName, imageExt = os.path.splitext(image) # separa o nome da extensão
        inImage = Image.open(image) # abre a imagem como img
        inImagePixels = inImage.load()
        inImageWidth, inImageHeight = inImage.size # pega a largura e a altura da img

        outImage = inImage.copy() # copia a imagem para a saida
        outImagePixels = outImage.load() # carrega cada pixel no saida_pixels
        outImageName = imageName + "_inv" + imageExt # o nome e a extensão será o mesmo junto com _inv, mostrando que inverteu as colunas

        print("\nSwapping {}".format(image))

        for x in range(0, inImageWidth - 1, 2): # largura - 1 garante que as imagens impares não troquem a ultima coluna
            for y in range(inImageHeight): # repete a inversão em toda a altura
                outImagePixels[x, y] = inImagePixels[x + 1, y]  # coluna impar da saída será a par da entrada
                outImagePixels[x + 1, y] = inImagePixels[x, y]  # coluna par da saída será a ímpar da entrada

        outImage.save(outImageName, icc_profile = inImage.info.get("icc_profile")) #iccprofile será o mesmo do input. se tiver o icc do photoshop, manterá saturado no final
        print("Column swapped successfully!")



def vagparameter(file_list):

    sfxWasFoundCounter = 1 # conta os arquivos passados

    for file in file_list: # para cada arquivo na lista_arquivos

        if option == 3 and file == 'sfx.wad': # se a opção for 3 e for sfx.wad
            sfxExtractPath = str(input('\nExtract sfx.wad to (ex: C:/sfxrip): ')) # pede o diretório para extração

        elif sfxWasFoundCounter == len(file_list) and option == 3: # se não achou
            print('\nNo sfx.wad to extract')
            return # sai da função sem retorno

        elif option == 3 and file != 'sfx.wad': # se a opção for 3 e não for sfx.wad 
            sfxWasFoundCounter = sfxWasFoundCounter + 1 # adiciona 1 ao contador
            continue # continua para o próximo arquivo
        

        with open(file, 'rb') as fileBytes: # lê o arquivo como bytes

            fileContent = fileBytes.read() # guarda todos os bytes na variável
            keywords = [b"VAGp", b"MSVp"] # palavras chave para encontrar o header dentro do arquivo
            print("\nFile: {}".format(file))

            soundIndex = 0

            for keyword in keywords: # para cada palavra chave na lista
                keyPosition = fileContent.find(keyword) # a posição da primeira palavra é guardada

                while keyPosition != -1: # enquanto a posição não for -1

                    fileBytes.seek(keyPosition + 4) # move o ponteiro para a position, em relação ao inicio do arquivo, + 4
                    fileBytes.seek(8,1) # move o ponteiro a partir de sua posição para 8 na direita
                    soundByteLength = fileBytes.read(4).hex() # lê a quantidade em bytes o tamanho do audio, tirando o header
                    soundSamplerate = int.from_bytes(fileBytes.read(4), 'big') # lê o samplerate
                    fileBytes.seek(12,1) # move o ponteiro em 12 a partir de sua posição
                    soundName = fileBytes.read(16).decode('utf-8', errors='ignore') # lê o nome interno da parte do arquivo
                    print("{} {} - {} ({} bytes, {}Hz)".format(soundIndex + 1, "0x" + str(format(keyPosition, '08x')), soundName, soundByteLength.lstrip('0'), soundSamplerate)) # printa

                    if option != 3: # se não for option 3
                        soundIndex += 1
                        keyPosition = fileContent.find(keyword, keyPosition + 1) # procura a próxima instancia da palavra
                        continue # volta pro inicio do while

                    # quando opt = 3 e arquivo atual for sfx.wad, passará da condição e continua o while

                    fileBytes.seek(keyPosition) # move o ponteiro para a position, em relação ao inicio do arquivo
                    soundBlock = fileBytes.read(int(soundByteLength, 16) + 64) # lê o arquivo com o valor do tamanho de bytes + tamanho do header (64)

                    if sfxripper(soundName, soundBlock, sfxExtractPath) == False: # se em uma execução do sfxripper retornar false 
                        print("\nStopping sfx.wad extraction\n(Already extracted)") # para a extração
                        break # quebra o loop
                    
                    soundIndex += 1
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
    
    print("{} extracted".format(outFileName))



def listchannels(file_list): # lista todos os arquivos vag e prepara em casais para ser processados

    vagPairs = []
    vagWasFound = False

    for file in file_list:

        if file.endswith("L.vag") or file.endswith("R.vag"): # se terminar em l ou r
            vagWasFound = True # encontrou arquivo
            pairName = file[:-5]  # remove até o l/r, sendo o par atual

            if pairName not in vagPairs: # se o par não estiver na lista
                vagPairs.append(pairName) # coloca nela
    
    if vagWasFound == False: # se não tiver arquivos na pasta
        print('\nNo files to convert\nCheck for typos in file names')
    
    for pairName in vagPairs: # para cada par na lista de casais

        vagChannelL = pairName + "L.vag"
        vagChannelR = pairName + "R.vag"

        print("\nChecking pair {}".format(pairName))

        if vagChannelL in file_list and vagChannelR in file_list: # se tiver ambos os canais
            
            vagPair = [vagChannelL, vagChannelR] # pega o caminho de cada lado e junta em uma lista
            createmsv(vagPair, pairName) # cria o msv com o par de vag e o nome do par bruto

        else:
            if vagChannelL not in file_list: # se não tiver um dos canais do par atual no arquivos
                vagPairMissing = "L"
            else:
                vagPairMissing = "R"
            print("\nIncomplete pair: {} (Missing {} channel)\nCheck for typos in file name or missing file".format(pairName, vagPairMissing))



def headerchanger(msvs_content, pair_name): # altera o cabeçalho do canal atual msvs

    with io.BytesIO(msvs_content) as buffer:

        vagHeader = buffer.read(3)  # lê os primeiros 48 bytes (0x00 até 0x2F)

        if vagHeader == b'VAG':  # verifica se os primeiros 3 bytes são 'VAG'
            buffer.seek(0)  # move o ponteiro para o início
            buffer.write(b'MSV')  # substitui 'VAG' por 'MSV'

        buffer.seek(32) # move o ponteiro ao 0x20 a partir do inicio, parando no inicio do nome interno
        buffer.write(b'\x00' * 16) # limpa o nome que estava antes, preenchendo com 0x00
        buffer.seek(-16, 1) # volta para o inicio do nome

        vagName = (pair_name.split('.')[0])[:-1] # (arquivo) L.msv (divide o nome do arquivo em 2 pelo '.', seleciona o primeiro item e depois corta o lado (L/R))
        vagChannelSide = (pair_name.split('.')[0])[-1] # arquivo (L) .msv

        buffer.write((vagName[:15] + vagChannelSide).encode('utf-8')) # o nome é limitado a 15 chars. o lado ficará no final do nome mesmo se passar do limite

        return buffer.getvalue() # retorna todo o conteudo do vag



def endtriggerremove(msvs_content): # tira o trigger de parar a música no final do canal

    with io.BytesIO(msvs_content) as buffer:
        
        buffer.seek(-31, 2) # move o ponteiro para o final e 0x1F para trás
        vagFlag = buffer.read(1) # lê a flag do final do arquivo

        if vagFlag == b'\x01': # se o byte for 0x01

            buffer.seek(-1, 1) # move o ponteiro novamente para a flag
            buffer.write(b'\x00') # remove a flag
            buffer.seek(15, 1) # avança 15 bytes a partir da posição atual
            buffer.write(b'\x00' * 15) # remove a linha 0x77 sobrescrevendo com 0x00
    
        return buffer.getvalue() # retorna todo o conteudo do vag



def adjustsize(msvs_content, block_quantity):

    with io.BytesIO(msvs_content) as buffer:

        msvsSize = len(buffer.getvalue()) # guarda o tamanho do vag
        msvsMaxSize = (block_quantity) * 0x20000 # calcula o tamanho máximo do vag com a quantidade de blocos máxima

        msvsSizeRemain = msvsMaxSize - msvsSize # calcula o restante fazendo a diferença do máximo pro tamanho atual
        buffer.seek(0) # move o ponteiro para o inicio
        buffer.write(buffer.getvalue() + (b'\x00' * msvsSizeRemain))  # preenche o conteudo com bytes vazios usando a quantidade do restante

        return buffer.getvalue()  # retorna todo o conteudo do vag
    
    
    
def createmsv(vag_pair_path, base_name):

    print('\nStarting process {}'.format(base_name + '.msv'))

    vagPairContent = [] # cria uma lista limpa para os arquivos msvs em bytes
    vagPairBlocks = [] # lista vazia para guardar a quantidade de blocos do tamanho block_byte_size cabem no conteudo
    msvsPair = [] # lista vazia para guardar os bytes do par processado

    for vagChannel in vag_pair_path: # para cada canal do par vag
        
        bufferVAG = io.BytesIO() # inicia um arquivo temporário em bytes para o vag atual

        with open(vagChannel, 'rb') as vagFile: # abre o lado atual em bytes
            bufferVAG.write(vagFile.read()) # lê o vag inteiro e guarda no buffer
        
        vagSize = len(bufferVAG.getvalue()) # pega o tamanho total do vag
        vagBlockRemain = 0x20000 - ((vagSize + 1) % 0x20000) # calcula a quantidade de bytes que faltam para o próximo bloco
        vagChannelBlocks = (vagSize + vagBlockRemain) // 0x20000 # divide o tamanho do conteudo + restante do bloco dividido por 0x20000

        vagPairBlocks.append(vagChannelBlocks) # guarda a divisão (o tanto de blocos) na lista
        vagPairContent.append(bufferVAG.getvalue()) # guarda os bytes de cada canal na lista

        bufferVAG.close() # fecha o buffer do vag atual

    if vagPairBlocks[0] != vagPairBlocks[1]: # se a quantidade de blocos de um canal for diferente do outro
        
        print('\nStopping {} process\nChannels differ in size/block quantities\n(Left: {}/Right: {})'.format(base_name + '.msv', vagPairBlocks[0], vagPairBlocks[1]))
        
        while True:
            option = input("Continue process? [Y/N]: ").strip().lower()

            if option in ('y', ''):
                break  # sai do loop e continua o programa

            elif option == 'n':
                print("Aborting {} creation".format(base_name + '.msv'))
                return  # aborta o processo

            else:
                print("Invalid input")

    vagBlocks = max(vagPairBlocks) # guarda qual canal tem a maior quantidade de blocos para usar na construção do msv
        
    for i, vagContent in enumerate(vagPairContent): # para cada conteudo no par atual (enumerate cria i)

        print('\nChanging header {}'.format(vag_pair_path[i]))
        vagProcessed = headerchanger(vagContent, vag_pair_path[i]) # muda o cabeçalho de VAG para MSV + nome interno
        
        print('Cutting end flag {}'.format(vag_pair_path[i]))
        vagProcessed = endtriggerremove(vagProcessed) # remove a flag final do arquivo

        msvsChannel = vag_pair_path[i][:-4] + '.msvs' # pega o nome do arquivo do vag e transforma para msvs
        with open(msvsChannel, 'wb') as msvsFile: # cria o arquivo msvs para o lado atual em bytes
            msvsFile.write(vagProcessed) # escreve o vag sem header e fim nele

        vagProcessed = adjustsize(vagProcessed, vagBlocks) # ajusta o tamanho com base do lado com quantidade de blocos máxima
        msvsPair.append(vagProcessed) # guarda os bytes do vag processado no par msvs

        print('Adjusted size {}'.format(vag_pair_path[i]))


    print('\nSorting channel blocks')

    bufferMSV = io.BytesIO() # cria um buffer para os blocos organizados

    for vagBlock in range(vagBlocks): # para cada bloco (0, 1, 2, ...)

        print('Block {} of {} (L and R)'.format(vagBlock + 1, vagBlocks), end='\r') # \r "reprinta" a linha atual
        for msvsChContent in msvsPair: # para cada conteudo de canal do par

            blockStart = vagBlock * 0x20000 # calcula o inicio do bloco (2 * 0x20000 = 0x40000)
            blockEnd = blockStart + 0x20000 # o final do bloco (0x40000 + 0x20000 = 0x60000)

            if blockStart < len(msvsChContent): # se o início do bloco for menor que o tamanho do conteudo do canal
                bufferMSV.write(msvsChContent[blockStart:blockEnd]) # escreve no buffer o conteudo do blockstart até o blockend
    
    with open(base_name + '.msv', "wb") as msvFile: # cria o msv do par atual e abre para escrita em bytes
        msvFile.write(bufferMSV.getvalue()) # escreve no msv o conteudo do blockstart até o blockend
    
    bufferMSV.close() # limpa o buffer

    print('\n{} created!'.format(base_name + '.msv'))



if __name__ == "__main__":
    
    option = None

    while option != 0:
        try:
            option = int(input("\nAsriel8691's GH3PS2 Thingy\n\n1 - VAGs 2 Menu music\n2 - VAG/MSV parameters\n3 - SFX Ripper\n4 - SFX Inject\n5 - Swap images columns\n\n0 - Exit\n> "))
        except:
            print('\nInvalid option')
            continue

        if option == 1:
            fileList = listfiles([".vag"])
            if fileList != []:
                listchannels(fileList)
        elif option == 2 or option == 3:
            fileList = listfiles([".vag", ".wad", ".msv", ".msvs", ".isf", ".imf"])
            if fileList != []:
                vagparameter(fileList)
        elif option == 4:
            fileList = listfiles([".vag"])
            if fileList != []:
                sfxinjection_content(fileList)
        elif option == 5:
            fileList = listfiles([".png", ".jpg", ".jpeg"])
            if fileList != []:
                swapcolumns(fileList)
            

        elif option == 9:
            print('Versão 1.7')


    print('Closing...')
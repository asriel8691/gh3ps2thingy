import os
from PIL import Image

def listfiles(option, extensions): # lista os arquivos a serem processados com base nas extensões

    currentExecutedDir = os.getcwd()  # pega o diretorio atual
    fileList = [] # guarda os arquivos listados
    fileWasFound = False

    for file in os.listdir(currentExecutedDir): # para cada arquivo no diretorio atual
        fileLowercaseName = file.lower() # o nome do arquivo ficará em minusculo para usar a comparação do 'extensions'

        for fileExtension in extensions: # para cada extensão no parametro extensions

            if fileExtension in fileLowercaseName: # se o nome tiver a extensao
                fileWasFound = True # marca o encontrou arquivos como true

                if file not in fileList: # se o arquivo não estiver ainda na lista
                    fileList.append(file) # adiciona o arquivo

    if fileWasFound == False: # se nenhum arquivo com o parametro de extensions for encontrado
        print('\nNo files to work with\nCheck for typos in file names')
    else:
        if option == 1: # se a opção for X
            listchannels(fileList) # ativa a função levando a lista de arquivos junto
        elif option == 2 or option == 3:
            vagparameter(fileList)
        elif option == 4:
            swapcolumns(fileList)


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
        outImagePixels = inImage.load() # carrega cada pixel no saida_pixels
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
            
            msvsPair = [createmsvs(vagChannelL), createmsvs(vagChannelR)] # após a clonagem, o msv criado é listado no arquivos msv
            createmsv(msvsPair, 0x20000, pairName)

        else:
            if vagChannelL not in file_list: # se não tiver um dos canais do par atual no arquivos
                vagPairMissing = "L"
            else:
                vagPairMissing = "R"
            print("\nIncomplete pair: {} (Missing {} channel)\nCheck for typos in file name or missing file".format(pairName, vagPairMissing))



def createmsvs(vag_channel): # cria os canais msvs a partir dos vags

    msvsChannel = vag_channel[:-4] + ".msvs" # coloca o nome e o canal do vag ao msvs
    print("Creating {}".format(msvsChannel))

    with open(vag_channel, 'rb') as vagFile: # abre o vag channel atual do par
        vagContent = vagFile.read() # guarda todo o conteudo do vag na variavel

    with open(msvsChannel, 'wb') as msvsFile: # cria/abre o arquivo msvs
        msvsFile.write(vagContent) # escreve todo o conteudo do vag no msvs

    return msvsChannel # retorna o nome canal do msvs



def headerchanger(msvs_channel): # altera o cabeçalho do canal atual msvs

    print('Changing header {}'.format(msvs_channel))

    with open(msvs_channel, "r+b") as msvsFile: # abre como ler e escrever em bytes
        msvsHeader = msvsFile.read(3)  # lê os primeiros 48 bytes (0x00 até 0x2F)
        
        if msvsHeader == b'VAG':  # verifica se os primeiros 3 bytes são 'VAG'
            msvsFile.seek(0)  # move o ponteiro para o início
            msvsFile.write(b'MSV')  # substitui 'VAG' por 'MSV'

        msvsFile.seek(32) # move o ponteiro ao 0x20 a partir do inicio, parando na linha do nome interno

        msvsName = (msvs_channel.split('.')[0])[:-1] # (arquivo) L.msv (divide o nome do arquivo em 2 pelo '.', seleciona o primeiro item e depois corta o lado (L/R))
        msvsChannelSide = (msvs_channel.split('.')[0])[-1] # arquivo (L) .msv

        msvsFile.write((msvsName[:15] + msvsChannelSide).encode('utf-8')) # o nome é limitado a 15 chars. o lado ficará no final do nome mesmo se passar do limite

        endtriggerremove(msvs_channel) # chama para remover o trigger final do canal atual



def endtriggerremove(msvs_channel): # tira o trigger de parar a música no final do canal

    print('Cutting end flag {}'.format(msvs_channel))

    with open(msvs_channel, "r+b") as msvsFile: # abre como ler e escrever em bytes

        msvsFile.seek(-31, 2) # move o ponteiro para o final e 0x1F para trás
        msvsFooter = msvsFile.read(31) # lê o final do arquivo

        if msvsFooter[:1] == b'\x01': # se o primeiro byte for 0x01
            # msvsFooter = b'\x00' * 31 # o rodapé será reescrito com 0x00
            msvsFile.seek(-31, 2) # move o ponteiro novamente
            msvsFile.write(b'\x00' * 31) # o rodapé é escrito no arquivo atual



def adjustsize(msvs_channel, block_byte_size):

    with open(msvs_channel, "rb") as msvsFile: # abre o canal msvs para ler em bytes
        msvsContent = msvsFile.read()  # guarda todos os bytes dele

    msvsSize = len(msvsContent)  # pega o tamanho do conteudo
    msvsSizeRemain = block_byte_size - (msvsSize % block_byte_size)  # calcula os bytes que faltam para o próximo multiplo

    if msvsSizeRemain != block_byte_size:  # se o tamanho restante for diferente do tamanho do bloco
        msvsContent += b'\x00' * msvsSizeRemain  # preenche o conteudo com bytes vazios usando a quantidade do restante

    return msvsContent  # retorna o CONTEÚDO processado, não o nome do canal



def createmsv(msvs_pair, block_byte_size, pair_name):

    msvsPairContent = [] # cria uma lista limpa para os arquivos msvs em bytes

    for msvsChannel in msvs_pair: # para cada canal do par msvs

        print('\nStarting process {}'.format(msvsChannel))

        headerchanger(msvsChannel) # muda o cabeçalho (e o rodapé)
        msvsPairContent.append(adjustsize(msvsChannel, block_byte_size)) # chama a função para ajustar o tamanho do canal atual e coloca o CONTEÚDO na lista

        print('Adjusted size {}'.format(msvsChannel))

    msvsPairBlocks = [] # lista vazia para guardar a quantidade de blocos do tamanho block_byte_size cabem no conteudo

    # esse for abaixo acho que não é necessário, já que os canais sempre terão o mesmo tamanho de conteudo. ou seja, o mesmo tanto de blocos

    for msvsChContent in msvsPairContent: # para cada conteudo de canal no par

        msvsChannelBlocks = len(msvsChContent) // block_byte_size # divide o tamanho do conteudo pelo tamanho do bloco em bytes
        msvsPairBlocks.append(msvsChannelBlocks) # guarda a divisão (o tanto de blocos) na lista

    msvBlocks = max(msvsPairBlocks) # acha qual canal tem a maior quantidade de blocos para usar na construção do msv

    print('\nSorting channel blocks')

    with open(pair_name + '.msv', "wb") as msvFile: # cria o msv do par atual e abre para escrita em bytes

        for msvBlock in range(msvBlocks): # para cada bloco (0, 1, 2, ...)

            print('Block {} of {} (L and R)'.format(msvBlock + 1, msvBlocks), end='\r') # \r "reprinta" a linha atual
            for msvsChContent in msvsPairContent: # para cada conteudo de canal do par

                blockStart = msvBlock * block_byte_size # calcula o inicio do bloco (2 * 0x20000 = 0x40000)
                blockEnd = blockStart + block_byte_size # o final do bloco (0x40000 + 0x20000 = 0x60000)

                if blockStart < len(msvsChContent): # se o início do bloco for menor que o tamanho do conteudo do canal
                    msvFile.write(msvsChContent[blockStart:blockEnd]) # escreve no msv o conteudo do blockstart até o blockend
    
    print('\nMSV created!')


if __name__ == "__main__":
    
    option = None

    while option != 0:
        try:
            option = int(input("\nAsriel8691's GH3PS2 Thingy\n\n1 - VAGs 2 Menu music\n2 - VAG/MSV parameters\n3 - SFX Ripper\n4 - Invert images columns\n\n0 - Exit\n> "))
        except:
            print('\nInvalid option\n')
            continue

        if option == 1:
            listfiles(option, [".vag"])
        elif option == 2 or option == 3:
            listfiles(option, [".vag", ".wad", ".msv", ".msvs", ".isf", ".imf"])
        elif option == 4:
            listfiles(option, [".png", ".jpg", ".jpeg"])
        elif option == 9:
            print('Versão 1.5')
    
    print('Closing...')
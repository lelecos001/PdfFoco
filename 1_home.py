import streamlit as st
import PyPDF2
from streamlit_option_menu import option_menu
from pathlib import Path
import tempfile
import zipfile
import io

st.set_page_config(
    page_title='PDFFOCO',
    page_icon=':page_facing_up:',
    layout='wide'
)

_, col2, _=st.columns(3)

with col2:
    st.title('Foco no PDF')
    st.markdown("""
    
    ### Escolha a opção desejada abaixo:
    """)

entradas = {
    'Extrair Página':':file-earmark-pdf-fill:',
    'Juntar Páginas':':page_facing_up:',
    'Verficar Páginas':':page_facing_up:',
}

escolha = option_menu(
    menu_title=None,
    orientation='horizontal',
    options=list(entradas.keys()),
    icons=list(entradas.values()),
    default_index=0,
)
_, col2, _=st.columns(3)

match escolha:
    case 'Extrair Página':
        tipoPagina = col2.radio("Qual página gostaria de retirar?",["Primeira Página","Última Página"],horizontal=True)

arquivos = col2.file_uploader("Selecione o(s) arquivo(s)",type="pdf",accept_multiple_files=True)

def retirarFolhas(tipoPagina,arquivos):
    dados = []
    for arquivo in arquivos:
            arquivoPyPDF2 = PyPDF2.PdfWriter()
            nomeArquivo = arquivo.name
            leitor = PyPDF2.PdfReader(arquivo)
            if tipoPagina == 'Última Página':
                arquivoPyPDF2.add_page(leitor.pages[-1])
            else:
                arquivoPyPDF2.add_page(leitor.pages[0])
            with tempfile.TemporaryDirectory() as tempDir:
                tempFile = Path(tempDir) / 'temp.pdf'
                arquivoPyPDF2.write(tempFile)
                with open(tempFile, 'rb') as nomeArquivo2:
                    dataDownload = nomeArquivo2.read()
            dados.append((nomeArquivo, dataDownload))
    return dados

def compactar(dados):
    # Criação do arquivo zip em memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nomeArquivo, arquivoData in dados:
            zip_file.writestr(nomeArquivo, arquivoData)
    
    # Movendo o ponteiro para o início para ser lido no download
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def etl():
        dados = retirarFolhas(tipoPagina,arquivos)
        if len(dados)>1:
            dadosDownload = compactar(dados)
            tipoMime = "application/zip"
            nomeStream = None
        else:
            dadosDownload = dados[0][1]
            tipoMime = "application/pdf"
            nomeStream = dados[0][0]
        return [dadosDownload,tipoMime,nomeStream]

if arquivos:
    col2.download_button(
        label="Clique aqui para realizar o Download",
        data=etl()[0],
        mime=etl()[1],
        file_name=etl()[2],
        icon=":material/download:",
    )
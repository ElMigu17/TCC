var dados_solucao = null;
var tipo_arquivo = "json";
var mostra_conflito = false;
var par_disc_doc_obrigatorio = []

def_display_na_classe("csv", "none");
def_display_na_classe("json", "flex");
document.getElementById("toggle").checked = false;
document.getElementById("mostra_conflito").checked = false;


//Util
function string_cod_turma(disc){
    var turmas = disc["turmas"]
    turmas.sort()
    turmas_as_string = ""
    for(i in turmas)
        turmas_as_string += turmas[i]
    return disc["codigo"] + "_" + turmas_as_string  
}

function get_dados_solucao(){
    $.ajax({
        url: "docentes-info",
        dataType: "json",
        success: function(data) {
            dados_solucao = data["docentes"];
            console.log(dados_solucao)
            mostra_analise_solucao(data["dados_solucao"])
            coloca_nome_no_select();
            organiza_tabelas_preferencias();
        },
        error: function(xhr, status, error) {
            console.log(xhr.responseText)
        }
    });
}

function download_link(){
    $.ajax({
        url: "download",
        dataType: "json",
        success: function(data) {
            return data
        },
        error: function(xhr, status, error) {
            window.alert(xhr.responseText)
        }
    });
}

function get_docente_por_nome(nome){
    retorno = false
    dados_solucao.forEach( (dado) => {
        if(dado["nome"] == nome){
            retorno = dado
        }
    })
    return retorno;
}
function get_disciplina_por_codigo(codigo){
    let retorno = false
    for(let i=0; i<dados_solucao.length; i++){
        dado = dados_solucao[i]["disciplinas_dados"]
        for(let j=0; j<dado.length; j++){
            dis = dado[j]
            if(string_cod_turma(dis) == codigo){
                return dis
            }
        }
    }
    return retorno;
}

//Arquivo
    //Tipo de arquivo
function alternar_tipo_arquivo(){
    if(tipo_arquivo === "json"){
        tipo_arquivo = "csv";
        def_display_na_classe("csv", "flex");
        def_display_na_classe("json", "none");
    }
    else{
        tipo_arquivo = "json";
        def_display_na_classe("csv", "none");
        def_display_na_classe("json", "flex");
    }
    verifica_existencia_arquivo();
}

function def_display_na_classe(classe, meu_display){
    elementos_csv = document.getElementsByClassName(classe);
    for(let i=0; i<elementos_csv.length; i++){
        elementos_csv[i].style.display = meu_display;
    }
}

    //Botões
function arquivo_emcima(event){
    event.preventDefault();
    event.target.style.backgroundColor = "#B2B2B2";
}

function arquivo_nao_emcima(elemento){
    elemento.style.backgroundColor = "#D2D2D2";
}

function arquivo_caiu(event){
    event.target.style.backgroundColor = "#D2D2D2";
    event.preventDefault();
    let file = event.dataTransfer.items[0].getAsFile()
    let id = event.originalTarget.nextElementSibling.id
    let div_nome_arquivo = event.originalTarget.nextElementSibling.nextElementSibling;
    let data = new FormData(); 
    data.append(id, file, id)

    all_file_name = file.name.split(".")
    if(all_file_name[all_file_name.length - 1] != tipo_arquivo){
        return 0;
    }

    enviar_um_arquivo(data, file, div_nome_arquivo);

}

function adiciona_listeners_nos_botoes_arquivo(){
    var botoes_selecao_arquivo = document.getElementsByClassName('botao-selecao-arquivo')

    function seleciona_arquivo(event){
        
        let div_nome_arquivo = event.explicitOriginalTarget.nextElementSibling;        
        let id = event.explicitOriginalTarget.id
        let form_data = new FormData($('#envioArquivos')[0]);
        let file = form_data.get(id);
        let data = new FormData(); 
        data.append(id, file, id)

        enviar_um_arquivo(data, file, div_nome_arquivo)
        
    }

    for(let i=0; i<botoes_selecao_arquivo.length; i++){
        botoes_selecao_arquivo[i].addEventListener('change',seleciona_arquivo,false);

    }
}

function enviar_um_arquivo(data, file, div_nome_arquivo){
    $.ajax({
        type: "POST",
        url: "enviar_um_arquivo/" + tipo_arquivo,
        data:  data,
        processData: false,
        contentType: false,

        success: function(response) {
            verifica_existencia_arquivo();
            if(response.length > 0){
                alert("Há erro no conteudo do arquivo enviado: " + file.name)
                div_nome_arquivo.innerHTML = "Arquivo enviado"
            }
            else{ 
                div_nome_arquivo.innerHTML = file.name

            }
        },
        error: function(xhr, status, error) {
            console.error(error);
            console.error(file.name);
        }
    })
}

    //Situação arquivo
function atualiza_situacao_arquivos(exist, element){
    if(exist){
        element.classList.remove("ausente");
        element.classList.add("presente");
        element.innerHTML = element.innerHTML.replace("ausente", "presente");
        element.children[0].src = element.children[0].src.replace("X", "Check");
    }
    else{
        element.classList.remove("presente");
        element.classList.add("ausente");
        element.innerHTML = element.innerHTML.replace("presente", "ausente");
        element.children[0].src = element.children[0].src.replace("Check", "X");
    }
}

function verifica_existencia_arquivo(){
    $.ajax({
        type: "GET",
        url: "files-existence/" + tipo_arquivo,
        processData: false,
        success: function(response) {
            if(tipo_arquivo === 'json'){
                let arquivos = document.getElementById("presenca-de-arquivo").getElementsByClassName("json")[0].children;
                atualiza_situacao_arquivos(response["disciplinas"], arquivos[0]);
                atualiza_situacao_arquivos(response["docentes"], arquivos[1]);
                atualiza_situacao_arquivos(response["solucao"], arquivos[2]);
            }
            else{
                let arquivos = document.getElementById("presenca-de-arquivo").getElementsByClassName("csv")[0].children;
                atualiza_situacao_arquivos(response["docentes_csv"], arquivos[0]);
                atualiza_situacao_arquivos(response["disciplinas_prox"], arquivos[1]);
                atualiza_situacao_arquivos(response["qtd_fim_ultimo_semestre"], arquivos[2]);
                atualiza_situacao_arquivos(response["preferencias"], arquivos[3]);
                atualiza_situacao_arquivos(response["ultimo_semestre"], arquivos[4]);
                atualiza_situacao_arquivos(response["penultimo_semestre"], arquivos[5]);
                atualiza_situacao_arquivos(response["antipenultimo_semestre"], arquivos[6]);
                atualiza_situacao_arquivos(response["solucao"], arquivos[7]);
            }

        },
        error: function(xhr, status, error) {
            console.error(error);
        }
    });
}

    //Solução
function solver(e){
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: "solver/" + tipo_arquivo,
        processData: false,
        contentType: false,
        success: function(response) {
            if(response == 'No solution found'){
                alert("Não foi encontrada solução")
            }
            else if(typeof response == typeof Object()){
                if("erro" in response){
                    alert(response["erro"])
                }
                else{
                    response_str = ''
                    for(let i in response){
                        response_str += '\n' + i;
                        turmas_str = '';
                        for(let j in response[i]){
                            turmas_str += response[i][j] + ", "
                        }

                        response_str += ': ' + turmas_str
                    }

                    alert("Na hora de fazer a leitura dos arquivos csv, algumas materias antigas aparentemente não foram lecionadas por docentes que lecionarão na solução ou houve uma confusão por haverem nomes indistinguiveis (como Fulano, Fulano de Tal e Fulano Silva). Isso pode ter ocorrido devido a um erro na escrita do nome do doscente. Com isso, segue a lista para futura verificação: \n" + response_str)
                }
            } 
            else{
                get_dados_solucao();
                verifica_existencia_arquivo();
                setTimeout(() => materias_liberadas(), 500);
            }
        },
        error: function(xhr, status, error) {
            console.error(error);
        }
    });
}

    //Analise de solução
function mostra_analise_solucao(data){
    let opt_data = document.getElementById("dados_solucao");
    let titulo = opt_data.getElementsByTagName("h3")[0];

    opt_data.innerHTML = '';
    opt_data.appendChild(titulo)
    
    for(let d in data){
        let opt = document.createElement('p');
        let anterior = d.split(" - ")[1];
        if(data[d] == true) {
            opt.innerHTML = anterior + " Houve";
        }
        else if(data[d] == false) {
            opt.innerHTML = anterior + " Não houve";
        }
        else {
            opt.innerHTML = anterior + ": " + data[d];
        }
        opt_data.appendChild(opt);
    }
}
function erros_de_leitura(e){
    e.preventDefault();
    $.ajax({
        url: "erros-de-leitura",
        dataType: "json",
        success: function(data) {
            document.getElementById("erros-de-leitura").style.display = "flex";
            cria_info_erro(data["incoerencias"]);
        },
        error: function(xhr, status, error) {
            console.log(xhr.responseText)
        }
    });

}
function fecha_erros_de_leitura(e){
    e.preventDefault();
    document.getElementById("erros-de-leitura").style.display = "none";
}
function cria_info_erro(erros){
    let tabela = document.getElementById("erros-de-leitura-interno");
    tabela.innerHTML = "";
    let mensagens = {};

    const tipos = [ "quebra_de_linha", 
        "presenca_palavra_para", 
        "presenca_palavra_mudar",
        "docent_not_found",
        "indistinguibilidade_de_nome"
    ];

    const tipos_pra_titulo = {"quebra_de_linha" : "Quebra de linha", 
        "presenca_palavra_para": "Presenca da palavra 'para'", 
        "presenca_palavra_mudar" : "Presenca da palavra 'mudar'",
        "docent_not_found" : "Docentes não encontrados",
        "indistinguibilidade_de_nome" : "Indistinguibilidade de nome"
    };

    mensagens["quebra_de_linha"] = []
    erros["quebra_de_linha"].forEach( (message) => {
            mensagens["quebra_de_linha"].push(message["arquivo"] + " - " + message["linha"]);
        }
    )

    mensagens["presenca_palavra_para"] = []
    erros["presenca_palavra_para"].forEach( (message) => {
            mensagens["presenca_palavra_para"].push(message["arquivo"] + " - " + message["linha"]);
        }
    )

    mensagens["presenca_palavra_mudar"] = []
    erros["presenca_palavra_mudar"].forEach( (message) => {
            mensagens["presenca_palavra_mudar"].push(message["arquivo"] + " - " + message["linha"]);
        }
    )

    mensagens["docent_not_found"] = []
    erros["docent_not_found"].forEach( (message) => {
            mensagens["docent_not_found"].push(message["arquivo"] + " - " + message["linha"] + " - " + message["doscente_disciplina"]);
        }
    )

    mensagens["indistinguibilidade_de_nome"] = []
    erros["indistinguibilidade_de_nome"].forEach( (message) => {
            mensagens["indistinguibilidade_de_nome"].push(message["arquivo"] + " - " + message["linha"] + " - " + message["nome"]);
        }
    )

    tipos.forEach((tipo) => {
        let div = document.createElement("div");
        div.id = tipo;
        
        let titulo = document.createElement("h4");
        titulo.innerHTML = tipos_pra_titulo[tipo];

        let list = document.createElement("ul");


        mensagens[tipo].forEach((text) => {
            let novo_item = document.createElement("li");
            novo_item.innerHTML = text;
            list.appendChild(novo_item);
        });
        

        div.appendChild(titulo);
        div.appendChild(list);
        tabela.appendChild(div);
        

    })
}

//Tabela Professores
    //Select
function select_docente(docente){
    limapr_tabela();
    mostra_disciplinas_docente(docente.target.value);
}

function coloca_nome_no_select(){
    var select = document.getElementById("nome_docentes")
    let valor_selecionado = select.value;
    select.innerHTML = ''
    dados_solucao.forEach(element => {
        var opt = document.createElement('option');
        opt.value = element["nome"];
        opt.innerHTML = element["nome"];
        if(mostra_conflito && element["conflitos"].length > 0){
            opt.innerHTML = element["nome"] + "*";
        }
        select.appendChild(opt);
    });
    select.value = valor_selecionado;
}

function alternar_mudanca_conflito(){
    mostra_conflito = !mostra_conflito;
    if(document.getElementById("nome_docentes").selectedOptions[0] != undefined){
        nome_docente = document.getElementById("nome_docentes").selectedOptions[0].value;
        mostra_disciplinas_docente(nome_docente);
    }
    coloca_nome_no_select();
    limapr_tabela();
}
    //Find class
function acha_cod_por_parte(){
    const codigo = document.getElementById("insere_cod_disciplinas").value;
    document.getElementById("cod_disciplinas").style.display="flex";
    const datalist = document.getElementById("cod_disciplinas");

    dados_solucao.forEach((doc) => {
        doc.disciplinas.forEach((dis) =>{
            if(dis.includes(codigo)){
                let nova_option = document.createElement("option");
                nova_option.value = dis;
                datalist.appendChild(nova_option);
            }
        })
    })
}
function inserir_par_obrigatorio(){
    const codigo = document.getElementById("insere_cod_disciplinas").value;
    const nome_docente = document.getElementById("nome_docentes").value;
    const doc = get_docente_por_nome(nome_docente.replace("*", ""))
    const dis = get_disciplina_por_codigo(codigo)
    par_disc_doc_obrigatorio.push([doc, dis])
}
function validar_solucao(){
    par_disc_doc_obrigatorio_para_envio = []
    disc_alocadas = {}

    console.log("aaaaaaaaaaaaaa", par_disc_doc_obrigatorio)
    for(let i=0; i<par_disc_doc_obrigatorio.length; i++){
        disc_alocadas[par_disc_doc_obrigatorio[i][1].pos] = par_disc_doc_obrigatorio[i][0].pos
        par_disc_doc_obrigatorio_para_envio.push([par_disc_doc_obrigatorio[i][0].pos, par_disc_doc_obrigatorio[i][1].pos])
    }


    for(let i=0; i<dados_solucao.length; i++){
        doc = dados_solucao[i]
        dado = doc["disciplinas_dados"]
        for(let j=0; j<dado.length; j++){
            dis = dado[j]
            if(disc_alocadas[dis.pos] == undefined){
                par_disc_doc_obrigatorio_para_envio.push([doc.pos, dis.pos])
            }
            else{
                console.log(dis.pos)
            }
        }
    }

    $.ajax({
        type: "POST",
        url: "validar_solucao",
        data: JSON.stringify({"pares_restricao": par_disc_doc_obrigatorio_para_envio}),
        contentType: 'application/json;charset=UTF-8',
        success: function(response) {
            console.log(response)
            if(response == 'No solution found'){
                alert("Não foi encontrada solução")
            }
            else if(typeof response == typeof Object()){
                if("erro" in response){
                    alert(response["erro"])
                }
                else{
                    response_str = ''
                    for(let i in response){
                        response_str += '\n' + i;
                        turmas_str = '';
                        for(let j in response[i]){
                            turmas_str += response[i][j] + ", "
                        }

                        response_str += ': ' + turmas_str
                    }

                    alert("Na hora de fazer a leitura dos arquivos csv, algumas materias antigas aparentemente não foram lecionadas por docentes que lecionarão na solução ou houve uma confusão por haverem nomes indistinguiveis (como Fulano, Fulano de Tal e Fulano Silva). Isso pode ter ocorrido devido a um erro na escrita do nome do doscente. Com isso, segue a lista para futura verificação: \n" + response_str)
                }
            } 
            else{
                get_dados_solucao();
                verifica_existencia_arquivo();
                setTimeout(() => materias_liberadas(), 500);
            }
        },
        error: function(xhr, status, error) {
            console.error(xhr, status, error);
        }
    });
}

    //Tabela
function cria_tabela(){
    let tabela = document.getElementById("horario");

    const semana = ["", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sabado"]
    let head = tabela.createTHead();
    let row = head.insertRow(0);
    
    for(let j=0; j<7; j++){
        row.insertCell(j).innerHTML = semana[j];
    }

    for(let i=1; i<17; i++){
        row = tabela.insertRow(i);
        row.insertCell(0).innerHTML=i+6;

        for(let j=1; j<7; j++){
            row.insertCell(j);
        }
    }

    get_dados_solucao();
}

function mostra_disciplinas_docente(nome_docente){
    var tabela = document.getElementById("horario");
    var i = 0;

    while(i < dados_solucao.length && dados_solucao[i]["nome"] != nome_docente){
        i++;
    }

    if(i < dados_solucao.length){
        var dados_disciplina = dados_solucao[i]["disciplinas_dados"]

        for(var j = 0; j < dados_disciplina.length; j++){    
            var horarios = dados_disciplina[j]["horarios"]
            
            for(var k = 0; k < horarios.length; k++){
                
                let pos_hora_inicio = parseInt(horarios[k]["hora_inicio"].split(':')) - 6;
                let pos_hora_fim = parseInt(horarios[k]["hora_fim"].split(':')) - 6;
                let pos_dia = horarios[k]["dia_semana"];
                let cod = dados_solucao[i]["disciplinas"][j]
                let code_splited = cod.split('_')

                let HTML_interno = "<p>"
                if(mostra_conflito && dados_solucao[i]["conflitos"].includes(cod)){
                    HTML_interno = "<p class='conflito_horario'>"
                }
                HTML_interno = HTML_interno + code_splited[0] + "</br>" + code_splited[1] + "</p>";

                for(var a = pos_hora_inicio; a <= pos_hora_fim; a++){
                    tabela.getElementsByTagName("tr")[a].getElementsByTagName("td")[pos_dia].innerHTML = HTML_interno
                }
            }
        }

    }
}

function limapr_tabela(){
    var tabela = document.getElementById("horario");

    for(var i=1; i<17; i++){
        var row = tabela.getElementsByTagName("tr")[i];

        for(var j=1; j<7; j++){
            row.getElementsByTagName("td")[j].innerHTML = "";
        }
    }
}


//Tabela Preferencia
function pega_disciplina_por_peso(preferencias, peso){
    for(pre in preferencias){
        if(preferencias[pre] == peso){
            return pre
        }
    }
}

function formata_nome(nome){
    var array_nome = nome.split(" ");
    array_nome[0] = array_nome[0] + " ";

    for (var i=1; i<array_nome.length; i++){
        array_nome[0] = array_nome[0] + array_nome[i][0] + "."
    }

    return array_nome[0]
}

function organiza_tabelas_preferencias(){
    let largura_disponivel = $(window).width()-180-43
    let qtd_profs = Math.trunc(largura_disponivel/142)
    let qtd_tabelas = Math.trunc(dados_solucao.length/qtd_profs)

    if(qtd_tabelas !== Math.trunc(qtd_tabelas)){
        qtd_tabelas = Math.trunc(qtd_tabelas)
        qtd_tabelas++
    }
    document.getElementById("tabela_preferencias").innerHTML = "";
    
    for(let i=1; i<=qtd_tabelas; i++){
        let inicio = (i-1)*qtd_profs
        let fim = i*qtd_profs
        let dados_sliced = dados_solucao.slice(inicio, fim)
        var tabela = document.createElement('table');
        
        document.getElementById("tabela_preferencias").appendChild(tabela);
        preenche_tabela_preferencias(dados_sliced, tabela);
    }
}

function preenche_tabela_preferencias(data, tabela){
    tabela.innerHTML = "";

    let qtd_rows = 0
    let head = tabela.createTHead();
    let row_head = head.insertRow(0);
    let body = tabela.createTBody();

    for(let i=0; i<data.length; i++){
        row_head.insertCell(i).innerHTML = formata_nome(data[i]["nome"]);
        if(data[i]["disciplinas_dados"].length > qtd_rows){
            qtd_rows = data[i]["disciplinas_dados"].length
        }
    }

    for(let i=0; i<qtd_rows; i++){
        body.insertRow(i);   
        let row_body = body.rows[i];            
        for(let j=0; j<data.length; j++){
            let cell = row_body.insertCell(j);
            cell.classList.add("cell-preference")
        }
    }

    for(let i=0; i<data.length; i++){
        
        let disciplinas_dados = data[i]["disciplinas_dados"];

        for(let j=0; j<disciplinas_dados.length; j++){
            let cell = body.rows[j].cells[i]
            let cod_turma = string_cod_turma(disciplinas_dados[j]);
            let code_splited = cod_turma.split('_')
            let HTML_interno = code_splited[0] + "</br>" + code_splited[1];
            cell.innerHTML = HTML_interno;

            if(Object.keys(data[i]["preferencia"]).includes(cod_turma)){
                cell.classList.add("presente")
            }
            else{
                cell.classList.add("ausente")
            }
        }
    }
}

//Materias Liberadas

function materias_serao_foram_liberadas(periodo_3, periodo_2, periodo_1, id){
    let disciplinas_liberadas = []
    for (i in dados_solucao) {
        let disciplinas_seguidas = structuredClone(dados_solucao[i][periodo_1])
        for (j in disciplinas_seguidas){
            if(!(disciplinas_seguidas[j] in dados_solucao[i][periodo_2])){
                disciplinas_seguidas.pop(j)
            }
        }

        for (j in disciplinas_seguidas){
            if(!(disciplinas_seguidas[j] in dados_solucao[i][periodo_3])){
                disciplinas_seguidas.pop(j)
            }
        }

        disciplinas_liberadas = disciplinas_liberadas.concat(disciplinas_seguidas)
    }
    document.getElementById(id).innerHTML = ""
    let lista = document.getElementById(id)

    for(i in disciplinas_liberadas){
        let novo_item = document.createElement('li') 
        novo_item.innerHTML = disciplinas_liberadas[i]
        lista.appendChild(novo_item)
    }
}

function materias_liberadas(){
    
    materias_serao_foram_liberadas("disc_per_2", "disc_per_1", "disciplinas", "disciplinas_serao_liberadas")
    materias_serao_foram_liberadas("disc_per_3", "disc_per_2", "disc_per_1", "disciplinas_estao_liberadas")
}

$(document).ready(function() {
    cria_tabela();
    verifica_existencia_arquivo();
    adiciona_listeners_nos_botoes_arquivo();
    
    document.getElementById("insere_cod_disciplinas").addEventListener("change", acha_cod_por_parte)
    document.getElementById("nome_docentes").addEventListener("change", select_docente)

    setTimeout(() => materias_liberadas(), 2400);
});
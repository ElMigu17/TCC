var data_table = null;
var type_json = true;
var file_type = "json";


setDisplayInClass("csv", "none");
setDisplayInClass("json", "flex");
document.getElementById("toggle").checked = false;

function setDisplayInClass(my_class, my_display){
    csvElements = document.getElementsByClassName(my_class);
    for(let i=0; i<csvElements.length; i++){
        csvElements[i].style.display = my_display;
    }
}

function toggleFileType(){
    if(file_type === "json"){
        file_type = "csv";
        setDisplayInClass("csv", "flex");
        setDisplayInClass("json", "none");
    }
    else{
        file_type = "json";
        setDisplayInClass("csv", "none");
        setDisplayInClass("json", "flex");
    }
    check_files_existence();
}

function show_docent_diciplins(docent_name, docents){
    var tabela = document.getElementById("horario");
    var i = 0;

    while(i < docents.length && docents[i]["nome"] != docent_name){
        i++;
    }

    if(i < docents.length){
        var disci_dados = docents[i]["disciplinas_dados"]

        for(var j = 0; j < disci_dados.length; j++){    
            var horarios = disci_dados[j]["horarios"]
            
            for(var k = 0; k < horarios.length; k++){
                
                pos_hora_inicio = parseInt(horarios[k]["hora_inicio"].split(':')) - 6;
                pos_hora_fim = parseInt(horarios[k]["hora_fim"].split(':')) - 6;
                pos_dia = horarios[k]["dia_semana"];
                innerHTML = "<p>" + docents[i]["disciplinas"][j] + "</p>";

                for(var a = pos_hora_inicio; a <= pos_hora_fim; a++){
                    tabela.getElementsByTagName("tr")[a].getElementsByTagName("td")[pos_dia].innerHTML = innerHTML
                }
            }
        }

    }
}

function put_names_in_select(docent){
    var select = document.getElementById("docent_names")
    docent.forEach(element => {
        var opt = document.createElement('option');
        opt.value = element["nome"];
        opt.innerHTML = element["nome"];
        select.appendChild(opt);
    });
}

function clear_table(){
    var tabela = document.getElementById("horario");

    for(var i=1; i<17; i++){
        var row = tabela.getElementsByTagName("tr")[i];

        for(var j=1; j<7; j++){
            row.getElementsByTagName("td")[j].innerHTML = "";
        }
    }
}

function update_file_situation(exist, element){
    if(exist){
        element.classList.remove("ausente")
        element.classList.add("presente")
        element.innerHTML = element.innerHTML.replace("ausente", "presente")
    }
    else{
        element.classList.remove("presente")
        element.classList.add("ausente")
        element.innerHTML = element.innerHTML.replace("presente", "ausente")
    }
}

function pega_disciplina_por_peso(preferencias, peso){
    for(pre in preferencias){
        if(preferencias[pre] == peso){
            return pre
        }
    }
}

function string_cod_turma(disc){
    var turmas = disc["turmas"]
    turmas.sort()
    turmas_as_string = ""
    for(i in turmas)
        turmas_as_string += turmas[i]
    return disc["codigo"] + "_" + turmas_as_string  
}

function format_name(name){
    var arr_name = name.split(" ");
    arr_name[0] = arr_name[0] + " ";

    for (var i=1; i<arr_name.length; i++){
        arr_name[0] = arr_name[0] + arr_name[i][0] + "."
    }

    return arr_name[0]
}

function materias_que_serao_liberadas(data){
    var disciplinas_liberadas = []

    for (i in data) {
        var disciplinas_seguidas = data[i]["disc_per_2"]
        for (j in disciplinas_seguidas){
            if(!(disciplinas_seguidas[j] in data[i]["disc_per_1"])){
                disciplinas_seguidas.pop(j)
            }
        }

        for (j in disciplinas_seguidas){
            if(!(disciplinas_seguidas[j] in data[i]["disciplinas"])){
                disciplinas_seguidas.pop(j)
            }
        }

        disciplinas_liberadas = disciplinas_liberadas.concat(disciplinas_seguidas)
    }
    var lista = document.getElementById("disciplinas_liberadas")
    for(i in disciplinas_liberadas){
        var novo_item = document.createElement('li') 
        novo_item.innerHTML = disciplinas_liberadas[i]
        lista.appendChild(novo_item)
    }
}

function preenche_tabela_preferencias(data, tabela){
    tabela.innerHTML = "";
    console.log(data);

    var head = tabela.createTHead();
    var row = head.insertRow(0);

    row.insertCell(j).innerHTML = "Peso";
    for(var i=0; i<data.length; i++){
        row.insertCell(j).innerHTML = format_name(data[i]["nome"]);
    }

    var body = tabela.createTBody();
    for(var i=0; i<5; i++){
        row = body.insertRow(i);
        row.insertCell(0).innerHTML = i+1;

        for(var j=1; j<=data.length; j++){
            disciplina_turma = pega_disciplina_por_peso(data[j-1]["preferencia"], i+1)
            var cell = row.insertCell(j)
            cell.innerHTML = disciplina_turma;
            cell.classList.add("cell-preference")
            cell.style.backgroundColor = "red";
            for(k in data[j-1]["disciplinas_dados"]){
                if(string_cod_turma(data[j-1]["disciplinas_dados"][k]) == disciplina_turma){
                    cell.style.backgroundColor = "green";
                }
            }
        }
    }
    console.log(tabela)

}

function create_table(){
    var tabela = document.getElementById("horario");

    const semana = ["", "segunda", "terça", "quarta", "quinta", "sexta", "sabado"]
    var head = tabela.createTHead();
    var row = head.insertRow(0);
    
    for(var j=0; j<7; j++){
        row.insertCell(j).innerHTML = semana[j];
    }

    for(var i=1; i<17; i++){
        row = tabela.insertRow(i);
        row.insertCell(0).innerHTML=i+6;

        for(var j=1; j<7; j++){
            row.insertCell(j);
        }
    }

    get_data_table();
}

function config_upload_files(){
    $('#envioArquivos').submit(function(e) {
        e.preventDefault(); 
        var data = new FormData($(this)[0]); 

        $.ajax({
            type: "POST",
            url: "upload/" + file_type,
            data:  data,
            processData: false,
            contentType: false,

            success: function(response) {
                check_files_existence();
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });
    });
}

function optimize(){
    $.ajax({
        type: "POST",
        url: "optimize/" + file_type,
        processData: false,
        contentType: false,
        success: function(response) {
            get_data_table();
            check_files_existence();
            setTimeout(() => materias_que_serao_liberadas(data_table), 500);
        },
        error: function(xhr, status, error) {
            console.error(error);
        }
    });
}

function get_data_table(){
    $.ajax({
        url: "docentes-info",
        dataType: "json",
        success: function(data) {
            data_table = data;
            put_names_in_select(data_table);

            var datas = []
            datas.push(data_table.slice(0,8))
            datas.push(data_table.slice(8,16))
            datas.push(data_table.slice(16))
            document.getElementById("tabela_preferencias").innerHTML = "";
            
            for (var i in datas) {
                var tabela = document.createElement('table');
                document.getElementById("tabela_preferencias").appendChild(tabela);
                preenche_tabela_preferencias(datas[i], tabela);
            }
            console.log(document.getElementById("tabela_preferencias"))

        },
        error: function(xhr, status, error) {
            window.alert(xhr.responseText)
        }
    });
}

function check_files_existence(){
    $.ajax({
        type: "GET",
        url: "files-existence/" + file_type,
        processData: false,
        success: function(response) {
            var files = document.getElementById("presenca-de-arquivo").getElementsByTagName("div")
            if(file_type === 'json'){
                var files = document.getElementById("presenca-de-arquivo").getElementsByClassName("json")[0].children;
                update_file_situation(response["disciplinas"], files[0]);
                update_file_situation(response["docentes"], files[1]);
                update_file_situation(response["resultado"], files[2]);
            }
            else{
                var files = document.getElementById("presenca-de-arquivo").getElementsByClassName("csv")[0].children;
                update_file_situation(response["docentes_csv"], files[0]);
                update_file_situation(response["ultimo_semestre"], files[1]);
                update_file_situation(response["disciplinas_prox"], files[2]);
                update_file_situation(response["preferencias"], files[3]);
                update_file_situation(response["resultado"], files[4]);
            }

        },
        error: function(xhr, status, error) {
            console.error(error);
        }
    });
}

function select_docente(docent){
    clear_table()
    show_docent_diciplins(docent.target.value, data_table);
}

$(document).ready(function() {
    create_table();
    check_files_existence();

    document.getElementById("docent_names").addEventListener("change", select_docente)
    config_upload_files();
    setTimeout(() => materias_que_serao_liberadas(data_table), 2400);

});
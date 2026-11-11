function cambia_localidad(datos){
  if(!datos){
	document.getElementById("palabra").value='';
	document.getElementById("tbl_productos").innerHTML='';
	limpiar_panel();
	document.getElementById('opc1').style.display='none';
	document.getElementById("panel").innerHTML="<img src=\"iconos/add.png\" title='Abrir el panel para agregar codigos de barras' alt='Abrir el panel para agregar codigos de barras' onClick=\"captura_cambio()\"/>&nbsp;<font color=\"#000000\"><b style=\"cursor:pointer\" onclick=\"captura_cambio()\">Agregar Producto</b></font>";
   var vars ='localidad='+document.getElementById('localidad').value;
	   vars+='&opc=cambio_localidad';
   CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars,"cambia_localidad(CAjax.data)");

  }
  else{
	var dat=datos.split('@@');
	document.getElementById('div_almacen').innerHTML=dat[0];
	document.getElementById('btn_excel').disabled=true;
	document.getElementById('btn_pdf').disabled=true;
	document.getElementById('btn_pdf_marbetes').disabled=true;
	document.getElementById("btn_pdf_marbetes_nvos").disabled=true;
	document.getElementById('btn_recargar').disabled=true;
	document.getElementById('archivo').disabled=true;
	document.getElementById('btn_importar').disabled=true;
	//habilitar_btns();
  }
}

function captura_cambio(){
	if(document.getElementById("opc1").style.display == 'none'){
		document.getElementById("opc1").style.display="inline";
		document.getElementById("panel").innerHTML="<img src=\"iconos/delete.png\" title='Cerra el panel para agregar codigos de barras' alt='Cerrar el panel para agregar codigos de barras' onClick=\"captura_cambio()\"/>&nbsp;<font color=\"#000000\"><b style=\"cursor:pointer\" onclick=\"captura_cambio()\">Cerrar</b></font>";
	}else {
		document.getElementById("opc1").style.display="none";
		document.getElementById("panel").innerHTML="<img src=\"iconos/add.png\" title='Abrir el panel para agregar codigos de barras' alt='Abrir el panel para agregar codigos de barras' onClick=\"captura_cambio()\"/>&nbsp;<font color=\"#000000\"><b style=\"cursor:pointer\" onclick=\"captura_cambio()\">Agregar Producto</b></font>";
	}
}

function cambio_almacen(datos){
  jQuery("#errors_table").hide();
  jQuery("#msg_span").hide();
  jQuery("#data_table").show();
  jQuery("#td_pag").show();

  if(!datos){
	document.getElementById("palabra").value='';
	document.getElementById("tbl_productos").innerHTML='';
	limpiar_panel();
	document.getElementById('opc1').style.display='none';
	document.getElementById("panel").innerHTML="<img src=\"iconos/add.png\" title='Abrir el panel para agregar codigos de barras' alt='Abrir el panel para agregar codigos de barras' onClick=\"captura_cambio()\"/>&nbsp;<font color=\"#000000\"><b style=\"cursor:pointer\" onclick=\"captura_cambio()\">Agregar Producto</b></font>";
	if(document.getElementById('almacen').value == -1){
		document.getElementById('btn_excel').disabled=true;
		document.getElementById('btn_pdf').disabled=true;
		document.getElementById('btn_pdf_marbetes').disabled=true;
		document.getElementById("btn_pdf_marbetes_nvos").disabled=true;
		document.getElementById('btn_recargar').disabled=true;
		document.getElementById('archivo').disabled=true;
		document.getElementById('btn_importar').disabled=true;
	}else{
		document.getElementById('archivo').value='';
		vars = 'inventario='+document.getElementById('almacen').value;
		vars +='&localidad='+document.getElementById("localidad").value;
		CAjax.send("div_ubicacion", "almacen/inventarios/seguimiento_inventario/acciones.php", vars+"&opc=ubicacion", true);

		CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars+"&opc=cargar_inventario","cambio_almacen(CAjax.data)");

	}
  }
  else{
	var elems=datos.split('QQ');
	var tbl_productos=document.getElementById("tbl_productos");
	cargar_filas(elems[0],1,elems[1],1);
	document.getElementById('btn_excel').disabled=false;
	document.getElementById('btn_pdf').disabled=false;
	document.getElementById('btn_pdf_marbetes').disabled=false;
	document.getElementById("btn_pdf_marbetes_nvos").disabled=false;
	document.getElementById('btn_recargar').disabled=false;
	document.getElementById('archivo').disabled=false;
	document.getElementById('btn_importar').disabled=false;
	habilitar_btns();
  }
}
function open_file(){
	var obj = document.getElementById("txtFileUpload");
	obj.click();
}

function cargar_filas(registros, pagina, totPag, opc, error, totUbi){

  var tbl_productos=document.getElementById("tbl_productos");
  var linea=null;
  var row=null;
  var datos= registros.split('##');

  for(var i=0; i<(datos.length-1); i++){
	var reg=datos[i].split('@@');
	linea=tbl_productos.rows.length+1;
	row=tbl_productos.insertRow(-1);
	var nCell=row.insertCell(-1);
	var uCell=row.insertCell(-1);
	var lCell=row.insertCell(-1);
	var cbCell=row.insertCell(-1);
	var dCell=row.insertCell(-1);
	var cadCell=row.insertCell(-1);
	var cantCell=row.insertCell(-1);
	var oCell=row.insertCell(-1);
	var mCell  =row.insertCell(-1);
	var imgCell=row.insertCell(-1);
	var bcoCell=row.insertCell(-1);

	nCell.className="cell";
	uCell.className="cell";
	lCell.className="cell";
	cbCell.className="cell";
	dCell.className="cell";
	cadCell.className="cell";
	cantCell.className="cell";
	oCell.className="cell";
	mCell.className="cell";
	imgCell.className="cell";
	bcoCell.className="cell";

	nCell.align="center";
	uCell.align="center";
	lCell.align="center";
	cbCell.align="center";
	dCell.align="left";
	cadCell.align="center";
	cantCell.align="center";
	oCell.align="center";
	mCell.align="center";
	imgCell.align="center";
	bcoCell.align="center";

  // alert(reg[9] +"--------"+ reg[12]);
	if(reg[9]=='0' || reg[12]=='0'){
		nCell.style.backgroundColor="#F0E68C";
		uCell.style.backgroundColor="#F0E68C";
		lCell.style.backgroundColor="#F0E68C";
		cbCell.style.backgroundColor="#F0E68C";
		dCell.style.backgroundColor="#F0E68C";
		cadCell.style.backgroundColor="#F0E68C";
		cantCell.style.backgroundColor="#F0E68C";
		oCell.style.backgroundColor="#F0E68C";
		mCell.style.backgroundColor="#F0E68C";
		imgCell.style.backgroundColor="#F0E68C";
		bcoCell.style.backgroundColor="#F0E68C";
	}
	else{
		nCell.style.backgroundColor="";
		uCell.style.backgroundColor="";
		lCell.style.backgroundColor="";
		cbCell.style.backgroundColor="";
		dCell.style.backgroundColor="";
		cadCell.style.backgroundColor="";
		cantCell.style.backgroundColor="";
		oCell.style.backgroundColor="";
		mCell.style.backgroundColor="";
		imgCell.style.backgroundColor="";
		bcoCell.style.backgroundColor="";
	}
	var ubicaciones="";
	//var marbetes="";
	if(typeof(reg[10]) != "undefined"){
		ubicaciones=reg[10];
		//marbetes=reg[11];

	}
	else{
		ubicaciones=$('ubicacion').innerHTML;
		//marbetes=reg[10];
	}

	nCell.innerHTML=linea;
	uCell.innerHTML="<input type='hidden' id='ubi_ini' value='"+reg[7]+"'><input type='hidden' id='ubi_ant' value='"+reg[0]+"'><select class=\"combo\" style=\"width: 110px;\" onchange=\"modifico(this)\">"+ubicaciones+"</select>";
	uCell.lastChild.value=reg[0];
	//uCell.lastChild.disabled=true;
	lCell.innerHTML=reg[1];
	cbCell.innerHTML=reg[2];
	dCell.innerHTML=reg[3];
	cadCell.innerHTML="<input type=\"text\" value=\""+reg[4]+"\" style=\"width:60px; font-size:10px\" autocomplete=\"off\" onchange=\"modifico(this)\"  autocomplete=\"off\" onkeyup=\"this.value=formateafecha(this.value,1)\" maxlength=\"10\">";
	var cantidad=reg[5];
	cantCell.innerHTML="<input type=\"text\" value=\""+cantidad+"\" style=\"width:50px; font-size:10px\" onchange=\"modifico(this)\" onkeypress=\"return validar(event,this,'numeros')\" onkeyup=\"cambiar_foco_registro(event, this);\" maxlength=\"6\">";
	oCell.innerHTML="<textarea rows=\"1\" cols=\"14\" style=\"resize:none;\" onchange=\"modifico(this)\" class=\"observa\">"+reg[6]+"</textarea>";

	if(typeof(reg[11]) != "undefined")
	var marbete=reg[11];
	else
	var marbete='';
	//alert(marbete+"==>>");
	mCell.innerHTML="<input type=\"text\" disabled=\"disabled\" value=\""+marbete+"\" style=\"width:50px; font-size:10px\"  maxlength=\"20\">";
	if(opc==2 || reg[8]=='1'){
		imgCell.innerHTML="<img src=\"iconos/delete.png\" onclick=\"eliminar_cb(this)\"  style=\"cursor:pointer\">";
		bcoCell.innerHTML="<input type='hidden' id='cambio' value='1'>";
	}else
		bcoCell.innerHTML="<input type='hidden' id='cambio'>";
  }
  var opciones='';
  if(opc !=2 ){
	if(totPag=='' || totPag=='0') totPag=1;
	for( i=0; i < totPag; i++){
		opciones += '<option value="'+(i+1)+'">'+(i+1)+'</option>';
	}
	document.getElementById('td_pag').innerHTML="P&aacute;gina:&nbsp;&nbsp; <select id='paginacion' onchange='cambio_pagina()'>"+opciones+"</select>&nbsp;de "+totPag;
	document.getElementById('paginacion').value=pagina;
	document.getElementById('pg_ant').value=pagina;
  }else{
	limpiar_panel();
  }
}

function modifico(elem){
	var row=elem.parentNode.parentNode;
	row.cells[10].firstChild.value=1;//9
	if(elem.parentNode.cellIndex == 1){
		valida_ubicacion(false,2,elem);
	}
}

function cambiar_foco_registro(evt, elem){
	tecla = (document.all) ? evt.keyCode : evt.which;
	if(tecla == 40 || tecla ==38 ){
		registro = (elem.parentNode.parentNode.rowIndex)-1;
		tabla =elem.parentNode.parentNode.parentNode;

		if(tecla==40 && registro+1<tabla.rows.length)
			sig_elem = tabla.rows[registro+1].cells[6].firstChild.focus();
		else if(tecla==38 && registro !=0 )
			sig_elem = tabla.rows[registro-1].cells[6].firstChild.focus();
	}
}

function recargar(){
	document.getElementById('palabra').value="";
	document.getElementById('search_descripcion').value="";
	document.getElementById("td_pag").innerHTML="P�gina:&nbsp;&nbsp;<select id='paginacion' onchange='cambio_pagina()'><option value='1'>1</option></select>&nbsp;de 1";
	cambio_pagina();
}

function cambio_pagina(datos){
  if(!datos){
	var cadena='';

	var reg_eliminados = document.getElementById("regsElim").value;
	var tbl_productos=document.getElementById("tbl_productos");
	var num=tbl_productos.rows.length;
	var existe=false;
	var error=false;
	for(var i=0; i<num; i++){
	  tbl_productos.rows[i].cells[1].lastChild.style.backgroundColor="";
	  tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="";
	  if(tbl_productos.rows[i].cells[1].lastChild.value==-1){
		tbl_productos.rows[i].cells[1].lastChild.style.backgroundColor="#FC3";
		error=true;
	  }
	  var fecha=tbl_productos.rows[i].cells[5].firstChild.value;
	  if(fecha=='' || (fecha.length) != 10){
		tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="#FC3";

		error=true;
	  }

	  if(tbl_productos.rows[i].cells[10].firstChild.value==1){//9
		cadena += tbl_productos.rows[i].cells[1].lastChild.value+',';
		cadena += tbl_productos.rows[i].cells[2].innerHTML+',';
		cadena += tbl_productos.rows[i].cells[3].innerHTML+',';
		cadena += tbl_productos.rows[i].cells[5].firstChild.value+',';
		cadena += tbl_productos.rows[i].cells[6].firstChild.value+',';
		cadena += tbl_productos.rows[i].cells[7].firstChild.value+'@@';
	  }
	}

	if(!error){
		var vars='opc=cambio_pagina';
		if(cadena != '' || reg_eliminados!=''){
			if(confirm('\u00bf'+"Desea guardar los cambios antes de cambiar de p"+'\u00e1'+"gina?")){
				vars+='&cadena='+cadena;
				vars+='&reg_eliminados='+reg_eliminados;
			}
			else
				vars+='&cadena=';
		}
		else vars+='&cadena=';
		vars+='&inventario='+document.getElementById('almacen').value;
		vars+='&pagina='+document.getElementById('paginacion').value;
		vars+='&palabra='+document.getElementById('palabra').value;
		vars+='&pg_ant='+document.getElementById('pg_ant').value;
		vars+='&localidad='+document.getElementById('localidad').value;
		CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars,"cambio_pagina(CAjax.data)");
	}
	else{
		alert("Faltan campos requeridos!!");
		document.getElementById('paginacion').value=document.getElementById('pg_ant').value;
	}
  }
  else{
	var elems=datos.split('#,#');
	document.getElementById("tbl_productos").innerHTML='';
	document.getElementById("regsElim").value="";
	cargar_filas(elems[0], elems[2], elems[1], 1);

  }
}

function desc_search(){
	if(document.getElementById('search_descripcion').value!=''){
		 if(document.getElementById('search_descripcion').value != document.getElementById('palabra').value ){
			document.getElementById('palabra').value=document.getElementById('search_descripcion').value;
		 }
		  cambio_pagina();
	}
	else
		document.getElementById('search_descripcion').focus();
}

function valida_ubicacion(datos,opc,elem){
  if(!datos){
	var inventario = document.getElementById('almacen').value;
	var pagina = document.getElementById('paginacion').value;
	var num='';
	if(opc==1){
	  var ubicacion=document.getElementById('ubicacion').value;
	  var codigo_barras=document.getElementById('codigo_barras').value;
	  var no_lote=(document.getElementById('lote').value).toUpperCase();
	 // var marbete=document.getElementById("marbete").value;
	  elem=-1;
	}
	else {
	  var ubicacion=elem.value;
	  var row = elem.parentNode.parentNode;
	  var codigo_barras=row.cells[3].innerHTML;
	  var no_lote = row.cells[2].innerHTML;
	 // var marbete  =row-cells[8].firstChild.value;
	  num=row.rowIndex;

	}
	var vars ='opc=valida_ubicacion';
		vars+='&ubicacion='+ubicacion;
		vars+='&inventario='+inventario;
		vars+='&no_lote='+no_lote;
		vars+='&codigo_barras='+codigo_barras;
		//vars+='&marbete='+marbete;
		vars+='&pagina='+pagina;
		vars+='&fila='+num;
	CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars,"valida_ubicacion(CAjax.data)");
  }
  else{
	var reg=datos.split('*,*');
	var existe=false;
	var tbl_productos=document.getElementById("tbl_productos");
	if(reg[0]==0){
		var num=tbl_productos.rows.length;
		for(var i=0; i<num; i++){
		  var ubi = tbl_productos.rows[i].cells[1].lastChild.value;
		  var cb = tbl_productos.rows[i].cells[3].innerHTML;
		  var lote = tbl_productos.rows[i].cells[2].innerHTML;
		  //alert(reg[2]+'=='+ubi +'&&'+ reg[3] +'=='+ cb +'&&'+ reg[4] +'=='+ lote +'&&'+ reg[1]+"!="+(i+1));
		  if(reg[2]==ubi && reg[3] == cb && reg[4] == lote && reg[1]!=(i+1)){
			existe=true;
			break;
		  }
		}
	}
	else existe=true;

	if(existe){
		if(reg[1]!='' && reg[1] != null){
			tbl_productos.rows[reg[1]-1].cells[1].lastChild.value=tbl_productos.rows[reg[1]-1].cells[1].childNodes[1].value;
			alert('La Ubicaci\u00f3n en la Fila '+reg[1]+' ya existe para ese C\u00f3digo de Barras y No. de lote en este inventario');
		}
		else{
			document.getElementById('ubicacion').value=-1;
			alert('La Ubicaci\u00f3n que desea agregar ya existe para ese C\u00f3digo de Barras y No. de lote en este inventario');
		}
	}else if(reg[1]=='' || reg[1] == null){
		agregar();
	}
	else{
		if(reg[1]!='' && reg[1] != null){
			tbl_productos.rows[reg[1]-1].cells[1].childNodes[1].value=tbl_productos.rows[reg[1]-1].cells[1].lastChild.value;
		}
	}
  }

}

function agregar(datos){
  if(!datos){
		var vars ='opc=codigo_barras';
			vars+='&localidad='+document.getElementById('localidad').value;
			vars+='&codigo_barras='+document.getElementById('codigo_barras').value;
			//vars+='&marbete='+document.getElementById('marbete').value;
		CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars,"agregar(CAjax.data)");
  }
  else{
		var dat=datos.split('*,*');
	if(dat[0]=='1'){
		var codigo_barras=document.getElementById('codigo_barras').value;
		var lote=(document.getElementById('lote').value).toUpperCase();
		var ubicacion=document.getElementById('ubicacion').value;
		var cantidad=document.getElementById('cantidad').value;
		var caducidad=document.getElementById('caducidad').value;
		var observaciones =document.getElementById('observaciones').value;
		//var marbete=document.getElementById("marbete").value;

		if(codigo_barras !='' && lote!='' && ubicacion!=-1 && (cantidad!='' && cantidad!='0') && caducidad != '' && caducidad.length==10){
			//var registros=ubicacion+'@@'+lote+'@@'+codigo_barras+'@@'+dat[1]+'@@'+caducidad+'@@'+cantidad+'@@'+observaciones+'@@'+marbete+'@@null@@@@'+dat[2]+'##';
			var registros=ubicacion+'@@'+lote+'@@'+codigo_barras+'@@'+dat[1]+'@@'+caducidad+'@@'+cantidad+'@@'+observaciones+'@@null@@@@'+dat[2]+'##';
			cargar_filas(registros, '', '', 2, '');
		}
		else if(caducidad.length!=10){
				alert("La Fecha de caducidad no es correcta");
				document.getElementById('caducidad').focus();
			}
			else
				alert("Faltan campos requeridos");

	}
	else
		alert(dat[1]);
  }
}

function limpiar_panel(){
	document.getElementById('codigo_barras').value='';
	document.getElementById('lote').value='';
	document.getElementById('ubicacion').value=-1;
	document.getElementById('cantidad').value='';
	document.getElementById('caducidad').value='';
	document.getElementById('observaciones').value='';
	//document.getElementById("marbete").value='';
}

function eliminar_cb(elemento){
	var row=elemento.parentNode.parentNode;
	var indice=row.rowIndex-1;
	var registro=row.cells[1].lastChild.value+'@@'+row.cells[2].innerHTML+'@@'+row.cells[3].innerHTML;

	if(document.getElementById("regsElim").value=="")
		document.getElementById("regsElim").value=registro;
	else
		document.getElementById("regsElim").value+='##'+registro;
	var tbl_productos=document.getElementById("tbl_productos");
	tbl_productos.deleteRow(indice);
	reasignar_num();
}

function reasignar_num(){
	var tbl_productos=document.getElementById("tbl_productos");
	var num=tbl_productos.rows.length;
	for(var i=0; i<num; i++){
		tbl_productos.rows[i].cells[0].firstChild.nodeValue=i+1;
	}
}

function guardar(datos){
  if(!datos){
	var cadena='';
	var registros_eliminados = document.getElementById("regsElim").value;
	var tbl_productos=document.getElementById("tbl_productos");
	var num=tbl_productos.rows.length;
	var error=false;
	for(var i=0; i<num; i++){
	  if(tbl_productos.rows[i].cells[10].firstChild.value==1){//9
		if((tbl_productos.rows[i].cells[5].firstChild.value).length==10){
		  tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="";
		  cadena += tbl_productos.rows[i].cells[1].lastChild.value+',';   	//0
		  cadena += tbl_productos.rows[i].cells[2].innerHTML+',';			//1
		  cadena += tbl_productos.rows[i].cells[3].innerHTML+',';			//2
		  cadena += tbl_productos.rows[i].cells[5].firstChild.value+',';	//3
      // alert(tbl_productos.rows[i].cells[5].firstChild.value+','); //sergio=>
		  cadena += tbl_productos.rows[i].cells[6].firstChild.value+',';	//4
		  cadena += tbl_productos.rows[i].cells[7].firstChild.value+',';	//5
		  cadena += tbl_productos.rows[i].cells[8].firstChild.value+',';	//6 marbete
		  cadena += tbl_productos.rows[i].cells[1].firstChild.value+'@@';	//7
		}
		else{
			cadena='';
			tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="#FC3";
			error=true;
		}

		if(tbl_productos.rows[i].cells[1].lastChild.value==-1){
			tbl_productos.rows[i].cells[1].lastChild.style.backgroundColor="#FC3";
			error=true;
		}
	  }
	}

	if(error){
		alert("Faltan campos requeridos!!");
	}
	else
	{
		if(cadena != '' || registros_eliminados!=''){
			
		  var vars='inventario='+document.getElementById('almacen').value;
			  vars+='&pagina='+document.getElementById('pg_ant').value;
			  vars+='&palabra='+document.getElementById('palabra').value;
			  vars+='&pg_ant='+document.getElementById('pg_ant').value;
			  vars+='&localidad='+document.getElementById('localidad').value;
			  vars+='&cadena='+cadena;
			  vars+='&regsElim='+registros_eliminados;
			  vars+='&finalizar=0';
			  vars+='&actualizar=0';
			  console.log(vars);
		  CAjax.receive("almacen/inventarios/seguimiento_inventario/guardar_seguimiento_inventario.php", vars,"guardar(CAjax.data)");
		}

	}
  }
  else{
	var elems=datos.split('*#*');
  // alert("GUARDAR >>>>>>>>>>>>"+elems); //sergio=>
	if(elems[0]==1){
		document.getElementById("tbl_productos").innerHTML='';
		cargar_filas(elems[1], elems[3], elems[2], 1);
		document.getElementById("regsElim").value="";
		alert("Datos Guardados Correctamente");
	}
	else if(elems[0]=='999'){
			alert("El inventario ha sido cancelado o finalizado previamente!!");
			window.location.reload();
		}
		else
			alert('Ocurrio un Error al guardar: '+elems[0]);
  }
}

function pdf(){
	var vars ='localidad='+document.getElementById('localidad').value;
		vars+='&inventario='+document.getElementById('almacen').value;
	window.open("almacen/inventarios/seguimiento_inventario/pdf_seguimiento_inventario.php?"+vars);
}

function excel(){
	var vars ='localidad='+document.getElementById('localidad').value;
		vars+='&inventario='+document.getElementById('almacen').value;
		vars+='&opc=0';
	window.open("almacen/inventarios/seguimiento_inventario/excel_seguimiento_inventario.php?"+vars);
}

function validar_archivo(formulario){
  var localidad=$('localidad').value;
  var inventario=$('almacen').value;
  if(localidad != -1 && inventario != -1){
	var file=formulario.archivo;
	var archivo=file.value;

	var maximo=10485760;
	var extension = (archivo.substring(archivo.lastIndexOf("."))).toLowerCase();
	var extPermitida = false;
	if(extension == 'xls' || extension == '.xlsx')
		extPermitida = true;
	if (!extPermitida) {
		mierror = "Comprueba la extensi�n de los archivos a subir. \nS�lo se pueden subir archivos con extensiones: .xls, .xlsx";
    }else{
		var size=file.files[0].filesize;
		  var date = new Date();
		  var curDate = null;
		  do { curDate = new Date(); }
		  while(curDate-date < 1250);
		  $('btn_importar').disabled=true;
		  $('btn_search_descripcion').disabled=true;
		  $('btn_actualizar').disabled=true;
		  $('btn_guardar').disabled=true;
		  //$('btn_finalizar').disabled=true;
			if(document.getElementById("privilegio").value=='2')
				$('btn_cancelar').disabled=true;
		 if(confirm("Se Remplazaran los Datos conforme Archivo?")){
			//Obtener los registros nuevos insertados para adicionarlos al cargar el archivo nuevo
			var tbl_productos=document.getElementById("tbl_productos");
			var num=tbl_productos.rows.length;
			var cadena="";
			for(var i=0; i<num; i++){
			  if(tbl_productos.rows[i].cells[1].firstChild.value=='null'){
				cadena+=tbl_productos.rows[i].cells[1].lastChild.value+'QQ';	//ubicacion
				cadena+=tbl_productos.rows[i].cells[1].lastChild.innerHTML+'QQ';//
				cadena+=tbl_productos.rows[i].cells[2].innerHTML+'QQ';			// lote
				cadena+=tbl_productos.rows[i].cells[3].innerHTML+'QQ';			//codigo barras
				cadena+=tbl_productos.rows[i].cells[4].innerHTML+'QQ';			//descripcion
				cadena+=tbl_productos.rows[i].cells[5].firstChild.value+'QQ';	//caducidad
				cadena+=tbl_productos.rows[i].cells[6].firstChild.value+'QQ';	//cantidad
				cadena+=tbl_productos.rows[i].cells[8].firstChild.value+'QQ';	//marbetes
				cadena+=tbl_productos.rows[i].cells[7].firstChild.value+'##';	//observaciones
				//alert(cadena+"-->"); //sergio=>
			  }
			}
			document.getElementById("claves_agregadas").value=cadena;
			document.getElementById("td_pag").innerHTML='';
			formulario.submit();
			return 1;
		  }else{	  $('btn_importar').disabled=false;
					  $('btn_search_descripcion').disabled=false;
					  $('btn_actualizar').disabled=false;
					  $('btn_guardar').disabled=false;
					  //$('btn_finalizar').disabled=false;
					  if(document.getElementById("privilegio").value=='2')
						$('btn_cancelar').disabled=false;
					return 1;
				}
	}
	if(mierror!=" "){
	  alert (mierror);
	  formulario.reset();
	  return 0;
	}
  }else alert("Es necesario capturar Localidad y Almacen");
}
var cambio_guardar = false;
function agregar_producto_excel(obj){

      cambio_guardar = true;
      var importarexcel = 0;
			var inputFile    = $(obj.id);
			var file 	       = inputFile.files[0];
			var data 	       = new FormData();
			var id_localidad = jQuery("#localidad").val();
			var id_inventario = jQuery("#almacen").val();
			var inventario   = jQuery("#almacen option:selected").text();

			data.append('archivo',     file);
			data.append('accion',      'subirArchivo');
			data.append('tipoArchivo', "excel");
			data.append('id_localidad',id_localidad);
      data.append('id_inventario',id_inventario);
      data.append('nombre_inventario',inventario);
			data.append('pag_actual',document.getElementById("pagina"));


			jQuery.ajax({
				url         : "almacen/inventarios/seguimiento_inventario/ajax_peticion2.php",
				type        : 'POST',
				contentType : false,
				data        : data,
				processData : false,
				cache       : false,
				dataType		: 'json',
				success: function(data){

					document.getElementById("progress").innerHTML = null;
					if(data.info == undefined ){
						alert(data.mensaje);
					} else {
            // alert("ELSE"); //sergio=>
						if(data.info.errores){
							// alert("Con errores"); //sergio=>
							jQuery("#tbl_errors").html("");
							jQuery("#data_table").slideUp(100);
							for (var i = 0; i < data.info.ERR.length; i++) {
								jQuery("#errors_table").slideDown(100);
								jQuery("#msg_span").slideDown();
								jQuery("#tbl_errors").append(data.info.ERR[i]);
							}
              // alert("ERRORES TRUE"); //sergio=>
							jQuery("#msg_span").text(data.info.ERR.length + " error(es) encontrados");
							jQuery("#msg_span").slideDown();

						}else{
              // alert("ERRORES FALSE"); //sergio=>
							jQuery("#data_table").slideDown(100);
							var total_filas = data.info.FILAS.length;
							cont = total_filas;
							for (var i = 0; i < total_filas; i++) {
								jQuery("#tbl_productos").append(data.info.FILAS[i]);
							}

							// alert("sin errores"); //sergio=>
							jQuery("#msg_span").text(total_filas+" registro(s) cargado(s) sin errores");
							jQuery("#msg_span").slideDown();
						}
					}
						importarexcel++;
						if(importarexcel > 0){
							jQuery("#txtFileUpload").live("click", function(e){
								jQuery(this).val('');
							} );
						}
				},
				beforeSend: function(){
					document.getElementById("progress").innerHTML="Cargando <img src=\"img/loader.gif\" />";

						limpiar_tabla();
						jQuery("#errors_table").slideUp(10);
						jQuery("#msg_span").slideUp();
				},
				complete: function(){
          jQuery("#td_pag").hide();
				},
				error: function(jqXHR, textStatus, errorThrown){

				},
			}).done(function(data){
			});

}

function cargar_ocultos(){
	var localidad=$('localidad').value;
	var inventario=$('almacen').value;
	$('ocultos').innerHTML="<input type='hidden' id='loc2' name='loc2' value='"+localidad+"'><input type='hidden' id='inventario' name='inventario' value='"+inventario+"'>";
}

function importar(datos,formulario){
		var file=formulario.archivo;
	var type=file.files[0].type;
	var tmp_name=file.files[0].tmp_name;
	alert(type + ' ');
}

function cancelar(datos){
  if(!datos){
	if(confirm('\u00bf'+"Est"+'\u00e1'+"s seguro que quieres cancelar este inventario?")){
		var vars ='opc=cancelar';
			vars+='&inventario='+document.getElementById('almacen').value;
			vars+='&localidad='+document.getElementById("localidad").value;
		CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars,"cancelar(CAjax.data)");
	}
  }
  else{
	if(datos==0){
		limpiar();
		alert("Inventario Cancelado correctamente");
	}
  }
}

function limpiar(){
	document.getElementById('localidad').value=-1;
	document.getElementById('archivo').value='';
	document.getElementById('search_descripcion').value='';
	document.getElementById('tbl_productos').innerHTML='';
	document.getElementById('div_almacen').innerHTML="<select id=\"almacen\" class=\"combo\" disabled='disabled'> <option value='-1'>--Seleccione una Opci&oacute;n--</option></select>";
	document.getElementById("finalizar").checked=false;
	limpiar_panel_add();
}

function limpiar_panel_add(){
	document.getElementById('codigo_barras').value='';
	document.getElementById('cantidad').value='';
	document.getElementById('lote').value='';
	document.getElementById('ubicacion').value=-1;
	document.getElementById('caducidad').value='';
	if(document.getElementById("opc1").style.display == 'inline')
		captura_cambio();
}

function actualizar(datos){
  if(!datos || datos=='actualizar'){
   if(confirm('\u00bf'+"Est"+'\u00e1'+"s seguro que quieres ac este inventario?")){
	var vars ='opc=actualizar';
		vars+='&localidad='+document.getElementById('localidad').value;
		vars+='&inventario='+document.getElementById('almacen').value;
	CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars,"actualizar(CAjax.data)");
	}
  }
  else{
	var dat = datos.split(',');
	if(dat[0]==0){
		if(dat[1]!=''){
			document.getElementById('tbl_productos').innerHTML='';
			cargar_filas(dat[1], dat[2], dat[2], 1);
			alert('Inventario Actualizado correctamente');
		}
		else alert('No hay datos para actualizar');
	}
	else alert("Error al Actualizar, informa al área de sistemas");
  }

}

function guardar_finalizar(){
	var cadena='';

	var tbl_productos=document.getElementById("tbl_productos");
	var num=tbl_productos.rows.length;
	var error=0;

	for(var i=0; i<num; i++){
		
	  	if(tbl_productos.rows[i].cells[1].lastChild.value==-1){
			tbl_productos.rows[i].cells[1].lastChild.style.backgroundColor="#FC3";
			console.log(tbl_productos.rows[i].cells[1].lastChild.value+'-----1guardar finalizar'); //sergio=>
			error=2;
	  	}

	  	if(tbl_productos.rows[i].cells[10].firstChild.value==1){//9
			if((tbl_productos.rows[i].cells[5].firstChild.value).length==10){
				tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="";
				cadena += tbl_productos.rows[i].cells[1].lastChild.value+',';     //0
				cadena += tbl_productos.rows[i].cells[2].innerHTML+',';			//1
				cadena += tbl_productos.rows[i].cells[3].innerHTML+',';			//2
				cadena += tbl_productos.rows[i].cells[5].firstChild.value+',';	//3
				cadena += tbl_productos.rows[i].cells[6].firstChild.value+',';	//4
				cadena += tbl_productos.rows[i].cells[7].firstChild.value+',';	//5
				cadena += tbl_productos.rows[i].cells[8].firstChild.value+',';	//6
				cadena += tbl_productos.rows[i].cells[1].firstChild.value+'@@';	//7
			}else{

				cadena='';
				tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="#FC3";
				alert(tbl_productos.rows[i].cells[5].firstChild.value+'-----5guardar finalizar'); //sergio=>
				error=1;
				break;
			}
	  	}
	}

	if(cadena != '' && error == 0){

	  	var vars ='inventario='+document.getElementById('almacen').value;
			vars+='&pagina='+document.getElementById('pg_ant').value;
			vars+='&palabra='+document.getElementById('palabra').value;
			vars+='&pg_ant='+document.getElementById('pg_ant').value;
			vars+='&localidad='+document.getElementById('localidad').value;
			vars+='&cadena='+cadena;
			vars+='&regsElim='+document.getElementById("regsElim").value;
			vars+='&finalizar=1';
			vars+='&actualizar=1';
			CAjax.receive("almacen/inventarios/seguimiento_inventario/guardar_seguimiento_inventario.php", vars,"finalizar(CAjax.data)");
	}else{

		if(error==1)
			alert('La Fecha de caducidad no es correcta');
		else if(error==2)
			alert("Faltan campos requeridos!!");
		else finalizar(false);
	}


}

function finalizar(datos){

  	if(!datos || datos=='finalizar'){
		document.getElementById('btn_guardar').disabled=true;
		document.getElementById('btn_recargar').disabled=true;

		if(document.getElementById("privilegio").value=='2')
			document.getElementById('btn_cancelar').disabled=true;
			
		var localidad = document.getElementById('localidad').value;
		var inventario =  document.getElementById('almacen').value;
		if(localidad != -1 && inventario != -1){
		if(confirm("Se actualizaran todos las existencias con los datos de este inventario, deseas continuar?")){

			var vars ='localidad='+localidad;
				vars+='&inventario='+inventario;
				vars+='&inventario='+inventario;
				vars+='&regsElim='+document.getElementById("regsElim").value;
				
			CAjax.receive("almacen/inventarios/seguimiento_inventario/finalizar_inventario.php", vars,"finalizar(CAjax.data)");
		}
		else{
			document.getElementById('btn_guardar').disabled=false;
			document.getElementById('btn_recargar').disabled=false;
			if(document.getElementById("privilegio").value=='2')
				document.getElementById('btn_cancelar').disabled=false;
		}
		}
	}
	else{
		document.getElementById('btn_guardar').disabled=false;
		document.getElementById('btn_recargar').disabled=false;

		if(document.getElementById("privilegio").value=='2')
			document.getElementById('btn_cancelar').disabled=false;
		if(datos == 1){
			limpiar();
			alert('Inventario Ajustado corectamente');
		}
		else alert(datos);
	}
}

function habilitar_btns(){
	document.getElementById("btn_actualizar").disabled=false;
  //	document.getElementById("btn_finalizar").disabled=false;
    document.getElementById("btn_guardar").disabled=false;
	if(document.getElementById("privilegio").value=='2')
		document.getElementById("btn_cancelar").disabled=false;
	document.getElementById("btn_search_descripcion").disabled=false;
}

function guardar_actualizar(){
  var cadena='';
  var tbl_productos=document.getElementById("tbl_productos");
  var num=tbl_productos.rows.length;
  var error=false;
  for(var i=0; i<num; i++){
	  if(tbl_productos.rows[i].cells[10].firstChild.value==1){//9
		if((tbl_productos.rows[i].cells[5].firstChild.value).length==10){
		  tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="";
		  cadena += tbl_productos.rows[i].cells[1].lastChild.value+',';   //0
		  cadena += tbl_productos.rows[i].cells[2].innerHTML+',';			//1
		  cadena += tbl_productos.rows[i].cells[3].innerHTML+',';			//2
		  cadena += tbl_productos.rows[i].cells[5].firstChild.value+',';	//3
		  cadena += tbl_productos.rows[i].cells[6].firstChild.value+',';	//4
		  cadena += tbl_productos.rows[i].cells[7].firstChild.value+',';	//5
		  cadena += tbl_productos.rows[i].cells[8].firstChild.value+',';	//6
		  cadena += tbl_productos.rows[i].cells[1].firstChild.value+'@@';	//7
		}
	    else{
			cadena='';
			tbl_productos.rows[i].cells[5].firstChild.style.backgroundColor="#FC3";
      // console.log(tbl_productos.rows[i].cells[5].firstChild.value+'-----5guardar actualizar'); //sergio=>
			error=true;
			break;
	    }
	}
  }
	if(cadena != ''){
	  if(confirm('\u00bf'+"Desea guardar los cambios antes de actualizar?")){
		  var vars='inventario='+document.getElementById('almacen').value;
			  vars+='&pagina='+document.getElementById('pg_ant').value;
			  vars+='&palabra='+document.getElementById('palabra').value;
			  vars+='&pg_ant='+document.getElementById('pg_ant').value;
			  vars+='&localidad='+document.getElementById('localidad').value;
			  vars+='&cadena='+cadena;
			  vars+='&regsElim='+document.getElementById("regsElim").value;
			  vars+='&actualizar=1';
			  CAjax.receive("almacen/inventarios/seguimiento_inventario/guardar_seguimiento_inventario.php", vars,"actualizar(CAjax.data)");
	  }
	  else actualizar(false);
	}
	else{
	  if(error) alert('La Fecha de caducidad no es correcta');
	  else actualizar(false);
	}
}

function validar_guardar(){

  if (cambio_guardar) {
    // alert("cambio guardar");
    guardar_excel();
  }else{

	if(document.getElementById("finalizar").checked)
		guardar_finalizar();
	else
		guardar();
  }
}

function guardarresp(datos){
  // alert("GUARDARRESP>>>>>>>>>>>>>>>>>" + datos); //sergio=>
  cambio_guardar = false;

  var elems = datos.split('*#*');
  // console.log(datos);
  jQuery("#td_pag").show();
  // console.log("Guardarrespuesta"+elems);
  // alert("GUARDARRESP>>>>>>>>>>>>>>>>>" + elems); //sergio=>
  if (elems[0] == 1) {
      document.getElementById("tbl_productos").innerHTML = '';
      cargar_filas(elems[1], elems[3], elems[2], 1);
      // console.log("1: "+elems[1]);
      // console.log("3: "+elems[3]);
      // console.log("2: "+elems[2]);
      document.getElementById("regsElim").value = "";
      alert("Datos Guardados Correctamente");
  } else {
      if (elems[0] == '999') {
          alert("El inventario ha sido cancelado o finalizado previamente!!");
          window.location.reload();
      } else
          alert('Ocurrio un Error al guardar: ' + elems[0]);
  }
}

function guardar_excel(){

  	var cadena='';
  	var registros_eliminados = document.getElementById("regsElim").value;
  	var tbl_productos=document.getElementById("tbl_productos");
  	var num=tbl_productos.rows.length;
  	var error=false;
  	for(var i=0; i<num; i++){
  		  cadena +=tbl_productos.rows[i].cells[1].firstChild.value + '|';
          cadena +=tbl_productos.rows[i].cells[2].innerHTML + '|';
  		  cadena +=tbl_productos.rows[i].cells[3].innerHTML + '|';
  		  cadena +='nada' + '|';
  		  cadena +=tbl_productos.rows[i].cells[5].firstChild.value + '|';
  		  cadena +=tbl_productos.rows[i].cells[6].firstChild.value + '|';
  		  cadena +=tbl_productos.rows[i].cells[7].firstChild.value + '@@';
  		}

  		if(cadena != '' || registros_eliminados!=''){
  		  var vars='inventario='+document.getElementById('almacen').value;
  			  vars+='&pagina=1';
          vars+='&palabra='+document.getElementById('palabra').value;
          vars+='&pg_ant='+document.getElementById('pg_ant').value;
  			  vars+='&localidad='+document.getElementById('localidad').value;
  			  vars+='&cadena='+cadena;
  			  vars+='&regsElim='+registros_eliminados;
  			  vars+='&finalizar=0';
  			  vars+='&actualizar=0';
  		  CAjax.receive("almacen/inventarios/seguimiento_inventario/guardar_archivo.php", vars,"guardarresp(CAjax.data)");
      }
}

function pdf_marbetes(pdf){
	var vars="";
	vars+="localidad="+document.getElementById("localidad").value;
	vars+="&idInv="+document.getElementById("almacen").value;
	//vars+="&tipo_pdf="+tipo_pdf;
	if(pdf==1)
	window.open("almacen/inventarios/inventario_periodico/pdf_marbetes.php?"+vars);
	if(pdf==2){
	 vars+="&cantidad="+document.getElementById("cantidad_marbetes").value;
	if(document.getElementById("cantidad_marbetes").value!=""&&document.getElementById("cantidad_marbetes").value<=100)
	window.open("almacen/inventarios/inventario_periodico/pdf_marbetes_blancos.php?"+vars);
	else if(document.getElementById("cantidad_marbetes").value==""){
	alert("Ingrese una Cantidad");
	document.getElementById("cantidad_marbetes").focus();
	}
	else{
		alert("La cantidad maxima que puede generar son 100 marbetes en blanco");
		document.getElementById("cantidad_marbetes").focus();
		}
	}
}

function valida_localidad(tipo_pdf){
  var vars="";
  var id_localidad=document.getElementById("localidad").value;
  var id_inventario=document.getElementById("almacen").value;
  	vars+="opc="+'valida_localidad';
  	vars+="&id_localidad="+id_localidad;
  	vars+="&id_inventario="+id_inventario;
  	vars+="&tipo_pdf="+tipo_pdf;
   CAjax.receive("almacen/inventarios/seguimiento_inventario/acciones.php", vars,"rpta_localidad(CAjax.data)");

}

function rpta_localidad(dato){
	var sep=dato.split("##");
	if(sep[0]==2&&sep[1]>0)
	pdf_marbetes(sep[2]);
	else if(sep[0]==2&&sep[1]<1)
	alert("Para esta localidad no se generaron marbetes");
	else
	alert("Esta localidad no es de tipo Matriz, por lo cual no genera marbetes");
}

function generar_marbetes_nuevos(){
	var vars="";
	vars+="opc="+'marbetes_nuevos';

	var win = new Window({id:"v_marbetes_n",className: "alphacube", width:300, height:120, zIndex: 100, resizable: true, title: "Generar Marbetes Nuevos",draggable:true,wiredDrag:true,onClose:function(win){},showEffectOptions: {duration:0}

	});

		win.setAjaxContent("almacen/inventarios/seguimiento_inventario/acciones.php", {method:'post', postBody:vars});

		win.setDestroyOnClose();
		win.showCenter(0);


}

function cambio_codigo_barras(){
	var codigo_barras=$('codigo_barras').value;
	var id_inventario = $('almacen').value;
	if(fcn.trim(codigo_barras)!=''){
	  data = { opc:'cambio_codigo_barras',
	           codigo_barras:codigo_barras,
		   	   id_inventario:id_inventario
		     };

	  jQuery.post("almacen/inventarios/seguimiento_inventario/acciones.php",data,function(response){
		  var dat = response.split("##");
		  if(dat[0]!=1){
			  alert(dat[1]);
			  $('codigo_barras').value='';
			  $('codigo_barras').focus();
		  }
	  });
	}
}

function resalta_fila(fila,color){
	fila.style.backgroundColor = "#"+color;
}

function restaura_fila(fila){
	fila.style.backgroundColor = "#FFFFFF";
}

function limpiar_tabla(){
	var tbl_productos = document.getElementById("tbl_productos");
	var num_rows = tbl_productos.rows.length;
	if(num_rows > 0)
		for(var i=0; i<num_rows; i++)
			tbl_productos.deleteRow(-1);
}

jQuery(function(){

    jQuery('.observa').live("focusout", function(e){
      var cadena = jQuery(this).val();
      var bnd = true;
      while(cadena.indexOf(",") > -1){
        cadena = jQuery(this).val();
        if(cadena.indexOf(",") > -1) {
          var cadena2 = cadena.replace(","," ");
          jQuery(this).val(cadena2);
          if (bnd) {
            alert("No se permiten comas");
            bnd = false;
          }
        }
      }
      var bnd = true;
      while(cadena.indexOf("@") > -1){
        cadena = jQuery(this).val();
        if(cadena.indexOf("@") > -1) {
          var cadena2 = cadena.replace("@"," ");
          jQuery(this).val(cadena2);
          if (bnd) {
            alert("No se permiten @");
            bnd = false;
          }
        }
      }
      var bnd = true;
      while(cadena.indexOf("Q") > -1){
        cadena = jQuery(this).val();
        if(cadena.indexOf("Q") > -1) {
          var cadena2 = cadena.replace("Q"," ");
          jQuery(this).val(cadena2);
          if (bnd) {
            alert("No se permiten Q�s");
            bnd = false;
          }
        }
      }

    });

		jQuery("#txtFileUpload").change( function(e){
				agregar_producto_excel(this);
		});
		jQuery("#msg_span").hide();
		jQuery("#modalidad2").hide();
		jQuery(".input_file").hide();
		jQuery("#idPlantilla").hide();
		// jQuery("#txtFileUpload").attr('disabled',true); //sergio=>

		jQuery("#localidad").live("change",function(){
      jQuery("#modalidad2").hide();
      jQuery(".input_file").hide();

    });
		jQuery("#almacen").live("change",function(){
			jQuery("#tbl_errors").html("");
			var localidad = jQuery(this).val();
			// var almacen = jQuery(this).val();


			if (localidad == -1) {
			    jQuery("#txtFileUpload").attr('disabled', false);
			    jQuery(".input_file").hide();
          jQuery("#modalidad2").hide();
			    jQuery("#idPlantilla").hide();
			} else {

			    jQuery("#txtFileUpload").attr('disabled', false);
			    jQuery(".input_file").show();
			    jQuery("#modalidad2").show();
			    jQuery("#idPlantilla").show();
			}
		});

});

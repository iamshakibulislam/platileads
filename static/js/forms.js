$(document).ready(function(){

	$("select[name='country']").prepend('<option value="select" disabled selected hidden>Select your country</option>');
});


$(document).ready(function(){
	$("label[for='id_email']").remove();
	$("label[for='id_new_password1']").remove();
	$("label[for='id_new_password2']").remove();
	$("span[class='helptext']").remove();

	$('#id_email').attr({class:'form-control',placeholder:'Enter your email'});
	$('#id_new_password1').attr({class:'form-control',placeholder:'Enter new password'});
	$('#id_new_password2').attr({class:'form-control',placeholder:'Confirm new password'});

	$(document).on('click','#business_submit',function(event){


		var agent_id = $('#agent_number').val();
        if(agent_id == ''){alert('agent id can not be blank');

	
		event.preventDefault();
	};

});//





});
$(function(){
	var task_id;
	$("#login_butt").click(function(){
		var values = $('#login_form').serialize();
		values += "&submit=" + 'login';
		console.log(values);
		$.ajax({
			url: '/hello',
			data: values,
			type: 'POST',
			success: function(data, status, request){	
				console.log(request);
				console.log(request['responseJSON']);
				status_url = request.getResponseHeader('Location');
				console.log('login_test')
				console.log(status_url)
//             	update_progress(status_url);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
	
	$("#register_butt").click(function(){
// 		var values = JSON.stringify($('#login_form').serializeArray());
		var values = $('#login_form').serialize();
		values += "&submit=" + 'register';
// 		jsoncallback: "%3F"
		console.log(values);
		$.post({
			url: '/hello',
			data: values,
			type: 'POST',
			success: function(data, status, request){	
				console.log(request);
				console.log(request['responseJSON']);
				status_url = request.getResponseHeader('Location');
				console.log('test')
				console.log(status_url)
//             	update_progress(status_url);
			},
			error: function(error){
				console.log(error);
			}
		});
	});	
});

// var msg_ids = ["login", "incorrect login", "taken warning", "registered"];
// 
// function update_progress(status_url) {
// 	console.log(status_url)
// 	// send GET request to status URL
// 	$.getJSON(status_url, "", function(data) {
// 		console.log('update progress');
// 		console.log(data);
// 		// update UI
// 		if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
// 			if ('result' in data) {
// 				console.log('1');
// 				// show result
// 				for (var i = 0; i < msg_ids.length; i++) {
// 					hide(document.getElementById(msg_ids[i]));
// 				}
// 				show(document.getElementById(data['result']));
// 			}
// 			else {
// 				// something unexpected happened
// 				console.log('unexpected happening');
// 			}
// 		}
// 		else {
// 			console.log('rerun');
// 			// rerun in 2 seconds
// 			setTimeout(function() {
// // 				update_progress(status_url);
// 			}, 2000);
// 		}
// 	});
// }
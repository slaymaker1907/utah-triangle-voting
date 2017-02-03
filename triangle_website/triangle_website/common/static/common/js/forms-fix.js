function djangoToBootstrap(element){
	element.attr('class', 'form-control')
}

$(document).ready(function() {
	// This makes it so it changes all of the form inputs to be as bootstrap needs them to be.
	djangoToBootstrap($('input'));
	djangoToBootstrap($('textarea'));
	djangoToBootstrap($('select'));
});

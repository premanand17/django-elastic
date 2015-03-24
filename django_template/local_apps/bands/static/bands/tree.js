(function(gdxbase_tree, $, undefined) {
	gdxbase_tree.init = function(treeId, color) {
		$(treeId+" i").each(function() {
				$( this ).css('color', color);
		});
		$(treeId+" li ul" ).hide();

		$(treeId).on('click', 'li', function(event) {
			event.stopPropagation(); // stop bubble up

            //console.log(event.target);
            if( $(this).children('ul').size() === 0 )
                return;
            
			if($(this).children('ul:first').is(":visible")) {
				$(this).children('ul:first').hide();
				$(this).children('i').first().addClass("fa-folder");
				$(this).children('i').first().removeClass("fa-folder-open");
			} else {
				$(this).children('ul:first').show();
				$(this).children('i').first().removeClass("fa-folder");
				$(this).children('i').first().addClass("fa-folder-open");
			}
		});
	}
	
	function getCookie(name) {
		//
	}
}( window.gdxbase_tree = window.gdxbase_tree || {}, jQuery ));

(function( $ ) {
 
    $.fn.tree = function( options ) {
        var settings = $.extend({
            // the defaults
        	color: "red",
        }, options );
 
        gdxbase_tree.init(this.selector, settings.color);

        return this;
    };
 
}( jQuery ));
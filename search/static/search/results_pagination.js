
(function( results_pagination, $, undefined ) {
	
	results_pagination.build = function(paginationId, overviewId, query, db, size, total) {
		var npages = total / size;
		$('#'+paginationId).empty();
		$('#'+paginationId).append('<ul class="pagination pagination-sm" id="search-pagination" style="margin: 0;"></ul>');

		updatePager(npages, 1);
		$('#search-pagination').on( "click", "li", function() {
			updateResults(this, paginationId, overviewId, db, size, total, query, npages);
		});
		
		updateResults($('.active'), paginationId, overviewId, db, size, total, query, npages);
		addDropDownSize(paginationId, overviewId, query, db, size, total);

		var dbs = db.split(',');
		for(var i=0; i<dbs.length; i++) {
			addCounter(query, dbs[i]);
		}
	}
	
	updatePager = function(npages, start) {
		$('#search-pagination').empty();
		$('#search-pagination').append('<li><a href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>');
		$('#search-pagination').append('<li class="active"><a href="#">'+start+'</a></li>');
		for (i = start+1; i < npages+1 && i < 10+start; i++) {
			$('#search-pagination').append('<li><a href="#">'+i+'</a></li>');
		}
		
		if(npages > 10) {
			$('#search-pagination').append('<li><a style="font-size:0; padding: 0px 10px"></a></li>');
			$('#search-pagination').append('<li><a href="#">'+Math.ceil(npages)+'</a></li>');
		}
		
		$('#search-pagination').append('<li><a href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>');
		if(npages === 1) {
			$('#search-pagination').children("li").first().addClass("disabled");
			$('#search-pagination').children("li").last().addClass("disabled");
		}
		return $('.active');
	}
	
	addCounter = function(query, db) {
		var url = window.location.pathname;
		if(url.match(/\/db\//g)) {
			url = url+'/count';
		} else {
			url = url+'db/'+db+'/count';
		}

		$.ajax({
	       	url: url,
	       	dataType: "json",
	       	type: "GET",
	       	success: function(json){
	       	$('#'+db+' span').replaceWith("<span class='badge'>"+
	       				json.count+"</span>");
	       		
	       		var path_name = window.location.pathname; 
	       		var my_regexp = /search\/(.*?)\//gi
	       		var match = my_regexp.exec(path_name);
	       		href_url = 'http://'+window.location.host+'/search/'+ match[1] + '/db' + '/' + db;
				$('#'+db+' a[href]').attr('href',href_url );
	       		
	       	}
	    });
	}
	
	addDropDownSize = function(paginationId, overviewId, query, db, size, total) {
		var sizerId = paginationId+'-sizer';
		$('#'+paginationId).append('<div class="btn-group pull-right">'+
				'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">'+
				'  Per Page <span class="caret"></span>'+
				'</button>'+
				'<ul id="'+sizerId+'" class="dropdown-menu" role="menu"></ul>'+
				'</div>');
		$('#'+sizerId).append('<li><a href="#">10</a></li>');
		$('#'+sizerId).append('<li><a href="#">20</a></li>');
		$('#'+sizerId).append('<li><a href="#">50</a></li>');
		$('#'+sizerId).append('<li><a href="#">100</a></li>');
		
		$('#'+sizerId).on( "click", "li", function() {
			results_pagination.build(paginationId, overviewId, query, db, $(this).text(), total);
		});
	}
	
	// update results when a new page number is clicked
	updateResults = function(thisPage, paginationId, overviewId, db, size, total, query, npages) {
		var url = window.location.pathname;
		if(url.match(/\/db\//g)) {
			url = url+'/page';
		} else {
			url = url+'db/'+db+'/page';
		}
		
		var page = $( thisPage ).text().match(/[0-9]+/);
		if( page === null ) {
			var label = $( thisPage ).children('a').first().attr('aria-label');
			if(label === 'Next') {
				page = parseInt($('.active').text().match(/[0-9]+/)) + 1;
				var mod = page % 10;
				if(mod === 1) {
					thisPage = updatePager(npages, page);
				}
			} else {
				page = parseInt($('.active').text().match(/[0-9]+/)) - 1;
				var mod = page % 10;
				console.log(mod);
				if(mod === 0) {
					thisPage = updatePager(npages, page-9);
				}
			}
			thisPage = $("#search-pagination li:contains('"+page+"')" );
			thisPage = thisPage.filter(function() { return $.text([this]) === ''+page+''; })
		} else
			page = page[0]


        $('.active').removeClass('active');
        $('span .pagination-sr').remove();
        $(thisPage).addClass('active');
        $(thisPage).siblings('a').append('<span class="sr-only" id="pagination-sr">(current)</span>');

        $.ajax({
        	url: url,
        	dataType: "json",
        	type: "POST",
        	data: {
				"from" : (((page-1)*size)), "size" : size
			},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
		        }
		    },
        	success: function(json){
        		$('#results').empty();
        		var hits = json.hits.hits;
        		$('#'+overviewId).html('Showing '+hits.length+' of '+total+' hits');

        		for(var i=0; i<hits.length; i++) {
        			var hit = hits[i]._source;
        		        			
        			if(hit.id){
        				$('#results').append(
        						'<ul class="list-group">' +
        						'<li class="list-group-item"><a href="/marker/'+hit.id+'">'+hit.id+'</a></li>'+
        						'<li class="list-group-item">Chromosome: '+hit.seqid+'; Position: '+hit.start+'; '+
					                        hit.ref+'/'+hit.alt+'</li>'+
        				'</ul>');
        				}else if(hit.hgnc){
        				$('#results').append(
        						'<ul class="list-group">' +
        						'<li class="list-group-item"><a href="/gene/'+hit.gene_symbol+'">'+hit.gene_symbol+'</a></li>'+
        						'<li class="list-group-item">HGNC: '+hit.hgnc+'</li>'+
        				'</ul>');
        				}else if(hit.type == 'region'){
        				$('#results').append(
        						'<ul class="list-group">' +
        						'<li class="list-group-item"><a href="/region/'+hit.attr.region_id+'">'+hit.attr.Name +'</a></li>'+
        						'<li class="list-group-item">Location: <a href="/search/' + hit.seqid + ':' + hit.start + '-' + hit.end + '">' +  hit.seqid + ':' + hit.start + '-' + hit.end + '</a>' + 
        						
        				'</ul>');
        				}
        		}
        	}
        });
	}
	
	getCookie = function(name) {
	    var cookieValue = null;
	    if (document.cookie && document.cookie != '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	}


}( window.results_pagination = window.results_pagination || {}, jQuery ));

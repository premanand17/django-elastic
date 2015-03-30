
(function( cytobands, $, undefined ) { 
	cytobands.col = {
		gpos100 : "rgb(0,0,0)",
		gpos    : "rgb(0,0,0)",
		gpos75  : "rgb(130,130,130)",
		gpos66  : "rgb(160,160,160)",
		gpos50  : "rgb(200,200,200)",
		gpos33  : "rgb(210,210,210)",
		gpos25  : "rgb(200,200,200)",
		gvar    : "rgb(220,220,220)",
		gneg    : "rgb(255,255,255)",
		acen    : "rgb(217,47,39)",
		stalk   : "rgb(100,127,164)"
	}

	// seqArr - contains uniquename and seqlen
	cytobands.drawChromosome = function (seqArr, maxlen, id) {
		d3.select("#"+id).selectAll("div")
		.data(seqArr)
		.enter()
		.append("div")
		.attr("class", "col-md-6")
		.append("p")
		.text(function(d) { return d.uniquename; })
		.append("div")
		.attr("class", "chr")
		.attr('id', function(d) { return d.uniquename; })
		.attr('label', function(d) { return d.uniquename; })
		.style("width", function(d) {
			var barwidth = (d.seqlen / maxlen) * 100;
			return barwidth + "%";
		});
	}
	
	// add the g-stain cytobands
	cytobands.addBands = function addBands(chr, srcseqlen, bands) {
		var width = $("#"+chr).width();
		d3.select("#"+chr).selectAll("div")
	    	.data(bands)
	    	.enter()
	    	.append("div")
	    	.attr("class", "band")
	    	.attr('label', function(d) { return d.fmin; })
	    	.style("background-color", function(d) {
	    		return d.col;
	    	})
	   	 	.style("width", function(d) {
	   	 		var barwidth = (d.seqlen / srcseqlen) * 100;
	   	 		//console.log(chr+" "+barwidth);
	   	 		return barwidth + "%";
	   	 	})
	   	 	.style("right", function(d) {
	   	 		//console.log( (d.fmax / maxlen) + " " +width + " " + d.seqlen);
	   	 		//var fmax = width-((d.fmax / srcseqlen) * width);
	   	 	    var fmax = (width-((d.fmax / srcseqlen) * width))/width * 100;
	   	 		return fmax +"%"; 
	   	 	});
	}

	cytobands.ajaxCall = function(chr, seqlen, org) {
		var url_band_terms = "/api/dev/cvterm/?format=json&cv__name=gstain&limit=0";
		$.ajax({
			url: url_band_terms,
			contentType: 'application/json',
			success: function(data, textStatus, jqXHR) {

				var gstainCvterms = data.objects;
				var bandTypes = "";
				for (var i = 0; i < gstainCvterms.length; i++) {
					bandTypes += gstainCvterms[i].cvterm_id;
					if(i < gstainCvterms.length-1)
						bandTypes += ",";
				}

		  		var url = '/api/dev/featurelocfull/?format=json'+
				  '&feature__type__in='+bandTypes+
				  '&srcfeature__uniquename='+chr+
				  '&srcfeature__organism__common_name='+org+
				  '&limit=0';
				$.ajax({
					url: url,
					contentType: 'application/json',
					success: function(res, textStatus, jqXHR) {
						cytobands.addBands(chr, seqlen, getAjaxBands(res, gstainCvterms));
					}
				});
				
			}
		});
	}

	function getAjaxBands(data, gstainCvterms) {
  		var bands = [];
  		for (var i = 0; i < data.objects.length; i++) {
  			var d = data.objects[i];
  			var fmin = d.fmin+1;
  			var fmax = d.fmax;
  			var fname = getCvtermName(d.feature.type, gstainCvterms);

  			var colour = cytobands.col[ fname ];
  			var seqlen = fmax - fmin;
		    var band = { seqlen:(fmax - fmin), fmin:fmin, fmax:fmax, col: colour };
	    	bands.push(band);
		}
		return bands;
	}

	function getCvtermName(type_id, cvterms) {
		for (var i = 0; i < cvterms.length; i++) {
			if(type_id.indexOf( cvterms[i].cvterm_id ) > -1)
				return cvterms[i].name;
		}
		return undefined;
	}
}( window.cytobands = window.cytobands || {}, jQuery ));

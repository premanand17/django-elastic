
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
	cytobands.drawChromosome = function (seqArr, maxlen, chartId) {
		d3.select("#"+chartId).selectAll("div")
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
	cytobands.addBands = function(chr, srcseqlen, bands) {
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
	   	 		var fmax = (width-((d.fmax / srcseqlen) * width))/width * 100;
	   	 		return fmax +"%"; 
	   	 	});
	}
}( window.cytobands = window.cytobands || {}, jQuery ));

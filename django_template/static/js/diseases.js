
(function( diseases, $, undefined ) {

	function getCvtermName(type_id, cvterms) {
		for (var i = 0; i < cvterms.length; i++) {
			if(type_id.indexOf( cvterms[i].type_id ) > -1)
				return cvterms[i].name;
		}
		return undefined;
	}

	diseases.addDiseaseButtons = function (organism, dilCvterms, residues) {
    	var url = '/api/dev/cvtermfull/?format=json&cv__name=disease';
    	var spinner = '<i class="fa fa-spinner fa-spin pull-right" id="disease_spinner"></i>';
    	$(spinner).insertAfter($("#diseases"));
    	
    	$.ajax({
    		url: url,
    		contentType: 'application/json',
    		success: function(data, textStatus, jqXHR) {
    			for (var i = 0; i < data.objects.length; i++) {
    	  			var disease_term = data.objects[i];
	  				var shortName;
	  				var colour;
	  				var rank;
    	  			for(var j=0; j < disease_term.cvtermprops.length; j++) {
    	  				var cvtermprop = disease_term.cvtermprops[j];
    	  				var cvtermName = getCvtermName(cvtermprop.type_id, dilCvterms);
    	  				if(cvtermName === "disease short name") {
    	  					shortName = cvtermprop.value;
    	  					rank = cvtermprop.rank;
    	  				} else if(cvtermName === "colour") {
    	  					colour = cvtermprop.value;
    	  				}
    	  			}

    	  			if(rank == 0) {
    	  				$("#diseases").append('<button type="button" data-toggle="btn-input" '+
    	  					'id="disease_'+shortName+'" value="'+disease_term.name+'" '+
    	  					'class="btn btn-default btn-disease"><strong>'+shortName+'</strong></button>');
    	  				$("#disease_"+shortName).css({ "background-color": colour, "color": "white"});
    	  			} else {
    	  				if($("#diseaseDropDown").length == 0) {
    	  					$("#diseases").append('<div class="btn-group btn-group-xs" role="group" id="diseaseDropDown">'+
    	  						'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">' +
    	  						'<strong>OTHERS</strong> <span class="caret"></span></button>'+
    	  						'<ul class="dropdown-menu" role="menu" id="diseaseDropDownMenus"></ul></div>');
    	  				}
    	  				$("#diseaseDropDownMenus").append('<li><a href="#"><strong>'+shortName+'</strong></a></li>');
    	  			}
    			}

    			
    			$("#diseases").on("click", ".btn-disease", function() {
    				var bg = $(this).css('backgroundColor');
    				diseases.diseaseButtonClick($( this ).attr("value"), $( this ).text(), bg, organism, residues);
    			});
    			
    			// tooltip for disease bar
    			$("#diseases").on("mouseenter", ".btn-disease", function() {
    				var str_url = "/api/dev/cvterm/?format=json&cv__name=disease&name="+
    					encodeURIComponent($( this ).attr("value"));
    				$(this).qtip({
    					content: {
    						text: $( this ).attr("value"),
    						title: $( this ).text()+" - "+$( this ).attr("value"),
    						ajax: {
    							url: str_url, 
    							type: 'GET',
    							contentType: 'application/json',
    							success: function(response){
    								this.set('content.text', response.objects[0].definition);
    							}
    						}
    					},
    					position: {
    						my: 'top left',
    						at: 'bottom center',
    						effect: false // Disable positioning animation
    					},
    					show: {
    						event: 'mouseover',
    						solo: true // Only show one tooltip at a time
    					},
    					hide: 'unfocus',
    					style: {
    						classes: 'qtip-help qtip-shadow qtip-rounded qtip-bootstrap',
    						width:350
    					}
    				});
    			});
    			
    			
    			$("#disease_spinner").hide();
    		}
    	});
	}

	diseases.diseaseButtonClick = function(diseaseName, abbr, bgcolour, organismName, residues) {
		var url = '/api/dev/featurepropfull/?format=json'+
				'&feature__type__name=region'+
				'&feature__organism__common_name='+organismName+
				'&type__cv__name=disease'+
				'&type__name='+encodeURIComponent(diseaseName)+
				'&limit=0';

		var regionId = 'region_'+abbr+'_';
		
		if($('div[id^="'+regionId+'"]').length) {
			$('div[id^="'+regionId+'"]').remove();
			return;
			
		}

		$("#disease_spinner").show();
		$.ajax({
			url: url,
			contentType: 'application/json',
			success: function(data, textStatus, jqXHR) {
				var regions = [];
				for (i = 0; i < data.objects.length; i++) {
	  				var f = data.objects[i].feature;
	  				var res = f.uniquename.split("_");

	  				var seqlen = f.featurelocs[0].fmax-f.featurelocs[0].fmin+1;
	  				// get the srcfeature seqlen from residues array
	  				var result = $.grep(residues, function(e){ return e.uniquename == res[0]; });
	  				var width = $("#"+res[0]).width();
	  				var fmax = width-((f.featurelocs[0].fmax / result[0].seqlen) * width);
	  				var rwidth = (seqlen / result[0].seqlen) * 100;

	  				$("#"+res[0]).append("<div class='region' title='"+f.name+"' id='"+regionId+i+"'></div>");
	  				$("#region_"+abbr+"_"+i).css( { 
	  					"background-color":bgcolour,
	  					"right":fmax+"px",
	  					"width":rwidth+"px",
	  					"border": "2px solid " +bgcolour,
	  				});
				}
				$("#disease_spinner").hide();
			}
		});

		$("#chart").on("mouseenter", ".region", function() {
			$(this).qtip({
				content: {
					text: $( this ).attr("title"),
					title: abbr,
				},
				position: {
					my: 'top left',
					at: 'bottom center',
					effect: false // Disable positioning animation
				},
				show: {
					event: 'click',
					solo: true // Only show one tooltip at a time
				},
				hide: 'unfocus',
				style: {
					classes: 'qtip-help qtip-shadow qtip-rounded qtip-bootstrap',
					width:150
				}
			});
		});
		
	}
}( window.diseases = window.diseases || {}, jQuery ));

'use strict';

/* Filters */

angular.module('elixir_front.filters', []).
// necessary for paging
filter('startFrom', function() {
	return function(input, start) {
			start = +start; //parse to int
			if (input) {
				return input.slice(start);
			} else {
				return;
			}
	}
}).
// filtering of a list of object by an object - used in filters in query interface
filter('filterByObject', function($filter) {
	return function (list, filter) {
		// recursively go through list entry and filter objects to find a match
		function filterMatch(entry, filter) {
			if (typeof filter === 'undefined') {
				return true;
			} else if (entry == null) {
				return false;
			}
			var result = false;
			for (var _key in filter) {
				result = false;
				// return true if filter empty
				if (typeof filter[_key] === 'undefined' || filter[_key] == '') {
					result = true;
				// skip if entry does not have the key from the filter
				} else if (typeof entry[_key] === 'undefined') {
					result = false;
				// if filter is not a deeper object nor an array just perform normal comparison
				} else if (typeof filter[_key] !== 'object') {
					// if entry is not a deeper object nor an array just perform normal comparison
					if (typeof entry[_key] !== 'object') {
						result = entry[_key].toLowerCase().indexOf(filter[_key].toLowerCase()) > -1
					// if entry is a deeper object perform deeper checking
					} else {
						// if entry is an array
						if (Array.isArray(entry[_key])) {
							// need a boolean to store whether any of the former array elements matched the filter; need this otherwise result could be overwritten with latter elements, even if the former ones matched
							var result_inner = false;
							// go through the whole entry array and check each element against the filter
							for (var j = 0; j < entry[_key].length; j++) {
								// if entry is a string, just perform normal comparison
								if (typeof entry[_key][j] == "string") {
									result_inner = entry[_key][j].toLowerCase().indexOf(filter[_key].toLowerCase()) > -1
								// if entry is an ontology only compare the term and not the URI to the filter
								} else if ('term' in entry[_key][j]) {
									result_inner = entry[_key][j].term.toLowerCase().indexOf(filter[_key].toLowerCase()) > -1
								// if entry is a different object then search for filter within it
								} else {
									// need to go through all properties of an entry to see if any matches are found
									for (var property in entry[_key][j]) {
										if(entry[_key][j].hasOwnProperty(property)) {
											if (JSON.stringify(entry[_key][j][property]).toLowerCase().indexOf(filter[_key].toLowerCase()) > -1) {
												result_inner = true;
												break;
											}
										}
									}
								}
								// if any of array elements matches, set result to true; this way even if the former elements match, the unmatching latter ones will not overwrite result
								if (result_inner) {
									result = true;
									break;
								}
							}
						// if entry is not an array
						} else {
							// if entry is an ontology only compare the term and not the URI to the filter
							if ('term' in entry[_key]) {
								result = entry[_key].term.toLowerCase().indexOf(filter[_key].toLowerCase()) > -1
							// if entry is a different object then search for filter within it
							} else {
								// need to go through all properties of an entry to see if any matches are found
								for (var property in entry[_key]) {
									if(entry[_key].hasOwnProperty(property)) {
										if (JSON.stringify(entry[_key][property]).toLowerCase().indexOf(filter[_key].toLowerCase()) > -1) {
											result = true;
											break;
										}
									}
								}
							}
						}
					}
				// if entry is an array and not an object
				} else if (Array.isArray(entry[_key])) {
					// go through the array and run the filter recursively
					for (var j = 0; j < entry[_key].length; j++) {
						if (filterMatch(entry[_key][j], filter[_key])) {
							result = true;
							break;
						}
					}
				} else {
					// if filter is a deeper object, call the same function recursively
					result = filterMatch(entry[_key], filter[_key]);
				}
				// if one of the filters didn't match return false
				if (!result) {
					return false;		
				}
			}
			// return true only if all the elements matched
			return true;
		}
		
		// list of matching elements
		var return_list = [];
		if (list) {
			// go through all elements
			for (var i=0; i < list.length; i++) {
				// add element to list if filter matches
				if ( filterMatch(list[i], filter) == true ) {
					return_list.push(list[i]);   
				}
			}
		}
		return return_list;
	};
}).
// query fuzzy matching which produces the relevance score
filter('filterQuery', function() {
	return function (list, filter) {
		// if filter empty return all resources
		if (filter == "" || filter == null) {
			return list;
		}

		// list of matching elements
		var return_list = [];
		if (list && list.length > 0) {
			// go through all elements
			for (var i=0; i < list.length; i++) {
				if (!_.isEmpty(list[i])){
					// calculate the fuzzy score of some of the attributes of each resource vs the filter
					var search_score = (list[i].name + " " + list[i].description + " " + list[i].topic + " " + list[i].function + " " + list[i].affiliation).score(filter);
					// if there is a non-zero match
					if ( search_score > 0 ) {
						// invert the score for sorting purposes
						list[i].search_score = 1.0 - search_score;
						return_list.push(list[i]);   
					}
				}
			}
		}
		return return_list;
	}
}).
// filter that highlights matches
filter('highlight', function($sce) {
	return function(str, termsToHighlight) {
		if (str && termsToHighlight.length > 0) {
			// Sort terms by length
			termsToHighlight.sort(function(a, b) {
				return b.length - a.length;
			});
			// Regex to simultaneously replace terms
			var regex = new RegExp('(' + termsToHighlight.join('|') + ')', 'gi');
			return $sce.trustAsHtml(str.replace(regex, '<span class="highlightedTerm">$&</span>'));
		} else {
			return str;
		}
	};
});
javascript:(function(){if%20(window.location.href.match(/ItemDetail\.aspx/)){var%20pattern=/Barcode=(\d+)/;}else%20if%20(window.location.href.match(/Imagine\.asp/)){var%20pattern=/B=(\d+)/;}else{alert("Whoops!%20I%20can't%20find%20a%20barcode.")}window.location='http://dhistory.org/archives/naa/items/'+pattern.exec(window.location.href)[1]})();
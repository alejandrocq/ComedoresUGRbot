var casper = require('casper').create();

var days = [
	'monday',
	'tuesday',
	'wednesday',
	'thursday',
	'friday',
	'saturday'
];

casper.start('http://scu.ugr.es', function() {
  this.echo('Loading web page: ' + this.getCurrentUrl());
});

casper.then(function() {
  this.waitForSelector('.inline', function() {
		var rects = this.evaluate(function() {
			var result = [];
			var tables = document.querySelectorAll('.inline');

			for (var i = 0; i < tables.length; i++) {
				result.push(tables[i].getBoundingClientRect());
			}

			return result;
		});

		// Render only tables with menu of each day
		for (var i = 0; i < days.length; i++) {
      var tableRect = rects[i];
      this.capture('images/' + days[i] + '.png', {
        top: tableRect.top,
        left: tableRect.left,
        width: tableRect.width,
        height: tableRect.height
      });
    }

		this.echo('Images rendered successfully')
  })
});

casper.run();

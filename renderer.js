var casper = require('casper').create({
  verbose: true,
  logLevel: 'info'
});

var days = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday'
];

casper.start('http://scu.ugr.es', function() {
  casper.log('Loading web page: ' + this.getCurrentUrl(), 'info');
});

casper.on("page.error", function(msg, trace) {
  casper.log(msg, 'error');
});

casper.then(function() {
  this.waitForSelector('.inline', function() {
    var rects = this.evaluate(function() {
      var result = [];
      var containers = document.querySelectorAll('div.level2');
      var tables = containers[containers.length - 1]
        .querySelectorAll('.inline');

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

    casper.log('Images rendered successfully', 'info');
  });
});

casper.run();

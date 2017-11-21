var casper = require('casper').create({
  verbose: true,
  logLevel: 'info'
});

casper.start('http://scu.ugr.es', function() {
  casper.log('Loading web page: ' + this.getCurrentUrl(), 'info');
});

casper.on("page.error", function(msg, trace) {
  casper.log(msg, 'error');
});

casper.then(function() {
  this.waitForSelector('.inline', function() {
    var result = this.evaluate(function() {
      var result = [];
      var tables = document.querySelectorAll('.inline');

      for (var i = 0; i < tables.length; i++) {
        var el = tables[i].querySelector("tbody > tr > td.leftalign");
        var date = el == null ? "" : el.textContent;
        result.push({
          rect: tables[i].getBoundingClientRect(),
          date: date
        });
      }

      return result;
    });

    // Render only tables with menu of each day
    for (var i = 0; i < result.length; i++) {
      var tableRect = result[i].rect;
      var tableDate = result[i].date;
      if (tableDate === "") continue;
      this.capture('images/' + tableDate + '.png', {
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

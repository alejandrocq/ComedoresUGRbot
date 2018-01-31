var casper = require('casper').create({
  verbose: false,
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
    var data = this.evaluate(function() {
      var result = [];
      var tables = document.querySelectorAll('table.inline');

      // Find first table to render (monday menu)
      var startIndex = 0;
      for (var i = 0; i < tables.length; i++) {
        var td = tables[i].querySelector("tbody > tr > td.leftalign");
        var date = td == null ? "" : td.textContent;

        if (date.indexOf('LUNES') !== -1) {
          startIndex = i; break;
        }
      }

      for (var i = startIndex; i < startIndex + 6; i++) {
        var td = tables[i].querySelector("tbody > tr > td.leftalign");
        var date = td == null ? "" : td.textContent;
        result.push({
          rect: tables[i].getBoundingClientRect(),
          date: date
        });
      }

      return result;
    });

    // Render only tables with menu of each day
    for (var i = 0; i < data.length; i++) {
      var tableRect = data[i].rect;
      var tableDate = data[i].date;
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

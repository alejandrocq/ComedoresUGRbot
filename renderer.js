var casper = require('casper').create({verbose: false, logLevel: 'info'});

casper.start('http://scu.ugr.es', function() {
  casper.log('Loading web page: ' + this.getCurrentUrl(), 'info');
});

casper.then(function() {
  this.waitForSelector('.inline', function() {
    var data = this.evaluate(function() {
      var days = [
        'LUNES',
        'MARTES',
        'MIÉRCOLES',
        'JUEVES',
        'VIERNES',
        'SÁBADO'
      ];

      var result = [];
      var tables = document.querySelectorAll('table.inline');

      var currentDate = new Date();
      var dayOfWeek = currentDate.getDay() - 1;
      var today = days[dayOfWeek] + ',' + currentDate.getDate();

      // Find first table to render (today menu)
      var startIndex = 0;
      for (var i = 0; i < tables.length; i++) {
        var td = tables[i].querySelector("tbody > tr > td.leftalign");
        var date = td === undefined ? null : td.textContent.replace(/\s/g, "");

        if (date !== null && date.indexOf(today) > -1) {
          startIndex = i;
          break;
        }
      }

      for (var i = startIndex; i < days.length - dayOfWeek + startIndex; i++) {
        var td = tables[i].querySelector("tbody > tr > td.leftalign");
        var date = td == null ? "" : td.textContent;
        result.push({rect: tables[i].getBoundingClientRect(), date: date});
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

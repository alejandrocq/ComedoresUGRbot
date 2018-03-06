const puppeteer = require('puppeteer')

const BROWSER_PATH = process.env.BROWSER_PATH;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: BROWSER_PATH
  })

  const page = await browser.newPage()
  page.setViewport({width: 1920, height: 1080, deviceScaleFactor: 2})

  await page.goto('http://scu.ugr.es')
  await page.waitForSelector('.inline')

  let data = await page.evaluate(() => {
    let days = [
      'LUNES',
      'MARTES',
      'MIÉRCOLES',
      'JUEVES',
      'VIERNES',
      'SÁBADO'
    ]

    let result = []
    let container = document.querySelectorAll('div.level2')[0]
    let tables = container.querySelectorAll('table.inline')

    let currentDate = new Date()

    // monday (0) - sunday (6)
    let dayOfWeek = currentDate.getDay() - 1
    let today = days[dayOfWeek] + ',' + currentDate.getDate()

    // Find first table to render (today menu)
    let startIndex = -1
    for (let i = 0; i < tables.length; i++) {
      let td = tables[i].querySelector('tbody > tr > td.leftalign')
      let date = td === null
        ? null
        : td.textContent.replace(/\s/g, '')

      if (date !== null && date.includes(today)) {
        startIndex = i
        break
      }
    }

    // Today menu not found, so return an empty array
    if (startIndex === -1) {
      return result
    }

    let daysToRender = days.length - dayOfWeek
    let endIndex = daysToRender > tables.length
      ? tables.length
      : daysToRender + startIndex

    for (let i = startIndex; i < endIndex; i++) {
      let td = tables[i].querySelector('tbody > tr > td.leftalign')
      let date = td === null
        ? null
        : td.textContent.replace(/\s/g, '')

      const {x, y, width, height} = tables[i].getBoundingClientRect()
      result.push({rect: {
        left: x,
        top: y,
        width,
        height
      },
      date: date})
    }

    return result
  })

  // Render only tables with menu of each day
  for (let i = 0; i < data.length; i++) {
    let tableRect = data[i].rect
    let tableDate = data[i].date
    if (tableDate === null) continue

    let imagePath = 'images/' + tableDate + '.png'
    await page.screenshot({
      path: imagePath,
      clip: {
        x: tableRect.left,
        y: tableRect.top,
        width: tableRect.width,
        height: tableRect.height
      }
    })
    console.log('INFO Image ' + imagePath + ' rendered successfully')
  }

  await browser.close()
})()

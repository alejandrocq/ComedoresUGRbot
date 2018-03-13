const puppeteer = require('puppeteer')

const BROWSER_PATH = process.env.BROWSER_PATH;

(async () => {
  let browser = null
  try {
    browser = await puppeteer.launch({ executablePath: BROWSER_PATH })

    const page = await browser.newPage()
    page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 })

    await page.goto('http://scu.ugr.es')
    await page.waitForSelector('.inline')

    let data = await page.evaluate(() => {
      let days = [
        'DOMINGO',
        'LUNES',
        'MARTES',
        'MIÉRCOLES',
        'JUEVES',
        'VIERNES',
        'SÁBADO'
      ]

      let result = []
      let tables = document.querySelectorAll('table.inline')

      let currentDate = new Date()

      // sunday (0) - saturday (6)
      let dayOfWeek = currentDate.getDay()
      if (dayOfWeek === 0) { // If sunday, load next week menu (starting monday)
        currentDate.setDate(currentDate.getDate() + 1)
        dayOfWeek = currentDate.getDay()
      }
      let dayOfMonth = currentDate.getDate()
      let today = days[dayOfWeek] + ',' + dayOfMonth

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

        // Discard if date string does not include an actual day
        if (!days.includes(date.substring(0, date.indexOf(',')))) {
          continue
        }

        const {x, y, width, height} = tables[i].getBoundingClientRect()
        result.push({
          rect: {
            left: x,
            top: y,
            width,
            height
          },
          date: date
        })
      }

      return result
    })

    console.log('INFO Rendering ' + data.length + ' images')

    // Render only tables with menu of each day
    let screenshots = []
    for (let i = 0; i < data.length; i++) {
      let tableRect = data[i].rect
      let tableDate = data[i].date

      if (tableDate === null) {
        continue
      }

      let imagePath = 'images-new/' + tableDate + '.png'
      screenshots.push(page.screenshot({
        path: imagePath,
        clip: {
          x: tableRect.left,
          y: tableRect.top,
          width: tableRect.width,
          height: tableRect.height
        }
      }).then(i => {
        console.log('INFO Image ' + imagePath + ' rendered successfully')
      }))
    }

    await Promise.all(screenshots)
    await browser.close()
    console.log('INFO Browser closed')
  } catch (e) {
    if (browser !== null) {
      await browser.close()
      console.error("ERROR Can't render menu images", e.stack)
    } else {
      console.error("ERROR Can't render menu images. Browser not initialized.",
        e.stack)
    }
  }
})()

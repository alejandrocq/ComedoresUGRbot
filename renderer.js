const puppeteer = require('puppeteer');

(async () => {
  let browser = null
  try {
    browser = await puppeteer.launch()

    const page = await browser.newPage()
    await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 })

    await page.goto(process.env.COMEDORES_URL)
    await page.waitForSelector('.inline')

    let data = await page.evaluate(() => {
      const sanitizeDate = date => {
        return date.replace(/\s/g, '').toLowerCase()
      }

      const includesDay = (container, dayStr) => {
        let trs = container.querySelectorAll('tr')
        for (let i = 0; i < trs.length; i++) {
          let th = trs[i].querySelector('th.leftalign > strong')
          let date = th === null ? null : sanitizeDate(th.textContent)
          if (date !== null && date.includes(dayStr)) return true
        }
        return false
      }

      let days = [
        'domingo',
        'lunes',
        'martes',
        'miércoles',
        'jueves',
        'viernes',
        'sábado'
      ]

      let tables = []

      let currentDate = new Date()

      // sunday (0) - saturday (6)
      let dayOfWeek = currentDate.getDay()
      if (dayOfWeek === 0) { // If sunday, load next week menu
        currentDate.setDate(currentDate.getDate() + 1)
        dayOfWeek = currentDate.getDay()
      }

      // set current date as monday of the current week
      let diff = (dayOfWeek - 1) * 24 * 60 * 60 * 1000
      currentDate.setTime(currentDate.getTime() - diff)

      let containers = document.querySelectorAll('div.content_doku > div.level1')
      let container = null
      for (let i = 0; i < containers.length; i++) {
        let dateAux = new Date(currentDate.getTime())
        let found = false

        // Test all days of the week until we find one of them on the tables
        let dayOffset = 0
        while (dayOffset !== 7) {
          dateAux.setDate(dateAux.getDate() + (dayOffset === 0 ? 0 : 1))
          let dayOfMonth = dateAux.getDate()
          let dayStr = days[dateAux.getDay()] + ',' + dayOfMonth + 'd'
          if (includesDay(containers[i], dayStr)) {
            container = containers[i]
            found = true
          }
          if (found) break
          dayOffset++
        }

        if (found) break
      }

      // If the menu of the current week couldn't be found, just return
      if (container === null) return tables

      let trs = container.querySelectorAll('tr')
      let dateIdxs = []
      for (let i = 0; i < trs.length; i++) {
        let th = trs[i].querySelector('th.leftalign')
        let date = th === null ? null : sanitizeDate(th.textContent)
        if (date !== null && days.includes(date.substring(0, date.indexOf(',')))) {
          dateIdxs.push(i)
        }
      }

      let out = []
      for (let i = 0; i < dateIdxs.length; i++) {
        let dateIdx = dateIdxs[i]
        let date = sanitizeDate(trs[dateIdx].querySelector('th.leftalign').textContent)
        let outTable = document.createElement('table')
        let outTableBody = document.createElement('tbody')
        outTable.append(outTableBody)

        let endIndex = i === dateIdxs.length - 1 ? trs.length : dateIdxs[i + 1]
        for (let j = dateIdx; j < endIndex; j++) {
          outTableBody.append(trs[j])
        }

        out.push({ table: outTable, date: date })
      }

      // Add all tables to DOM before getting their client rect
      for (let i = 0; i < out.length; i++) {
        container.appendChild(out[i].table)
      }

      for (let i = 0; i < out.length; i++) {
        const { x, y, width, height } = out[i].table.getBoundingClientRect()
        tables.push({
          rect: {
            left: x,
            top: y,
            width,
            height
          },
          date: out[i].date
        })
      }

      return tables
    })

    console.log('INFO Rendering ' + data.length + ' images')

    // Render only tables with menu of each day
    let screenshots = []
    for (let i = 0; i < data.length; i++) {
      let tableRect = data[i].rect
      let tableDate = data[i].date

      if (tableDate === null) continue

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
      console.error("ERROR Can't render menu images. Browser not initialized.", e.stack)
    }
  }
})()
